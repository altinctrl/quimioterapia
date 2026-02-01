import io
import os
import uuid
from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from src.models.prescricao import Prescricao
from src.providers.interfaces.equipe_provider_interface import EquipeProviderInterface
from sqlalchemy.orm.attributes import flag_modified

from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.schemas.prescricao import PrescricaoCreate, PrescricaoResponse, MedicoSnapshot, PrescricaoStatusEnum, PrescricaoStatusUpdate


async def listar_prescricoes_por_paciente(
        provider: PrescricaoProviderInterface,
        paciente_id: str,
) -> List[PrescricaoResponse]:
    lista = await provider.listar_por_paciente(paciente_id)
    return [PrescricaoResponse.model_validate(p) for p in lista]


async def buscar_prescricao(
        provider: PrescricaoProviderInterface,
        prescricao_id: str,
) -> PrescricaoResponse:
    prescricao = await provider.obter_prescricao(prescricao_id)
    if not prescricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescrição não encontrada")
    return PrescricaoResponse.model_validate(prescricao)


async def buscar_prescricao_multi(
        provider: PrescricaoProviderInterface,
        prescricao_ids: List[str],
) -> List[PrescricaoResponse]:
    lista = await provider.obter_prescricao_multi(prescricao_ids)
    return [PrescricaoResponse.model_validate(p) for p in lista]


async def criar_prescricao(
        prescricao_provider: PrescricaoProviderInterface,
        equipe_provider: EquipeProviderInterface,
        dados: PrescricaoCreate,
) -> PrescricaoResponse:
    try:
        medico = await equipe_provider.buscar_profissional_por_username(dados.medico_id)
        medico_snapshot = MedicoSnapshot(nome=medico.nome, crm_uf=medico.registro)
    except:
        medico_snapshot = MedicoSnapshot(nome="Médico não identificado", crm_uf="") # TODO: Remover

    blocos_processados = []
    for bloco in dados.blocos:
        bloco_dict = bloco.model_dump()
        for item in bloco_dict['itens']:
            if not item.get('id_item'):
                item['id_item'] = str(uuid.uuid4())
        blocos_processados.append(bloco_dict)

    documento_json = {
        "data_emissao": datetime.now().isoformat(),
        "paciente": dados.dados_paciente.model_dump(),
        "medico": medico_snapshot.model_dump(),
        "protocolo": dados.protocolo.model_dump(),
        "blocos": blocos_processados,
        "observacoes": dados.observacoes_clinicas
    }

    nova_prescricao = Prescricao(
        id=str(uuid.uuid4()),
        paciente_id=dados.paciente_id,
        medico_id=dados.medico_id,
        status="pendente",
        data_emissao=datetime.now(),
        conteudo=documento_json
    )

    criado = await prescricao_provider.criar_prescricao(nova_prescricao)

    return PrescricaoResponse.model_validate(criado)


def _append_historico_status(prescricao: Prescricao, status_anterior: str, status_novo: str,
                             usuario_id: Optional[str], usuario_nome: Optional[str], motivo: Optional[str] = None):
    historico = list(prescricao.historico_status or [])
    historico.append({
        "data": datetime.now().isoformat(),
        "usuario_id": usuario_id,
        "usuario_nome": usuario_nome,
        "status_anterior": status_anterior,
        "status_novo": status_novo,
        "motivo": motivo
    })
    prescricao.historico_status = historico
    flag_modified(prescricao, "historico_status")


async def recalcular_status_prescricao(
        prescricao_provider: PrescricaoProviderInterface,
        agendamento_provider: AgendamentoProviderInterface,
        prescricao_id: str,
        usuario_id: Optional[str] = "sistema",
    usuario_nome: Optional[str] = "Sistema",
    commit: bool = True
):
    prescricao = await prescricao_provider.obter_prescricao(prescricao_id)
    if not prescricao:
        return

    if prescricao.status in [
        PrescricaoStatusEnum.SUSPENSA.value,
        PrescricaoStatusEnum.CANCELADA.value,
        PrescricaoStatusEnum.SUBSTITUIDA.value
    ]:
        return

    agendamentos = await agendamento_provider.listar_por_prescricao(prescricao_id, incluir_concluidos=True)
    if not agendamentos:
        novo_status = PrescricaoStatusEnum.PENDENTE.value
    elif all(ag.status == 'concluido' for ag in agendamentos):
        novo_status = PrescricaoStatusEnum.CONCLUIDA.value
    elif any(ag.status in [
        'em-triagem',
        'em-infusao',
        'intercorrencia',
        'aguardando-consulta',
        'aguardando-exame',
        'aguardando-medicamento',
        'internado'
    ] for ag in agendamentos):
        novo_status = PrescricaoStatusEnum.EM_CURSO.value
    else:
        novo_status = PrescricaoStatusEnum.AGENDADA.value

    if prescricao.status != novo_status:
        status_anterior = prescricao.status
        prescricao.status = novo_status
        _append_historico_status(prescricao, status_anterior, novo_status, usuario_id, usuario_nome, motivo="Atualização automática")
        await prescricao_provider.atualizar_prescricao(prescricao, commit=commit)


async def atualizar_status_prescricao(
        prescricao_provider: PrescricaoProviderInterface,
        agendamento_provider: AgendamentoProviderInterface,
        prescricao_id: str,
        dados: PrescricaoStatusUpdate,
        usuario_id: Optional[str],
        usuario_nome: Optional[str],
) -> PrescricaoResponse:
    @asynccontextmanager
    async def _maybe_transaction(session):
        if session.in_transaction():
            yield
        else:
            async with session.begin():
                yield

    prescricao = await prescricao_provider.obter_prescricao(prescricao_id)
    if not prescricao:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescrição não encontrada")

    status_anterior = prescricao.status
    status_novo = dados.status.value if isinstance(dados.status, PrescricaoStatusEnum) else str(dados.status)

    if status_novo == PrescricaoStatusEnum.SUBSTITUIDA.value:
        if not dados.prescricao_substituta_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="prescricao_substituta_id é obrigatório para substituição.")

        prescricao_substituta = await prescricao_provider.obter_prescricao(dados.prescricao_substituta_id)
        if not prescricao_substituta:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescrição substituta não encontrada")

        session = getattr(prescricao_provider, "session", None)
        if session is None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Provider sem suporte a transações")

        async with _maybe_transaction(session):
            prescricao.prescricao_substituta_id = dados.prescricao_substituta_id
            prescricao_substituta.prescricao_original_id = prescricao.id
            prescricao.status = status_novo

            _append_historico_status(prescricao, status_anterior, status_novo, usuario_id, usuario_nome, dados.motivo)
            await prescricao_provider.atualizar_prescricao(prescricao, commit=False)
            await prescricao_provider.atualizar_prescricao(prescricao_substituta, commit=False)

            agendamentos = await agendamento_provider.listar_por_prescricao(prescricao.id, incluir_concluidos=False)
            for ag in agendamentos:
                detalhes = dict(ag.detalhes) if ag.detalhes else {}
                infusao = detalhes.get('infusao') or {}
                prescricao_id_anterior = infusao.get('prescricao_id')
                infusao['prescricao_id'] = dados.prescricao_substituta_id
                detalhes['infusao'] = infusao

                historico_prescricoes = list(detalhes.get('historico_prescricoes') or [])
                historico_prescricoes.append({
                    "data": datetime.now().isoformat(),
                    "usuario_id": usuario_id,
                    "usuario_nome": usuario_nome,
                    "prescricao_id_anterior": prescricao_id_anterior,
                    "prescricao_id_nova": dados.prescricao_substituta_id,
                    "motivo": dados.motivo
                })
                detalhes['historico_prescricoes'] = historico_prescricoes

                ag.detalhes = detalhes
                flag_modified(ag, "detalhes")

                historico_agendamento = list(ag.historico_alteracoes or [])
                historico_agendamento.append({
                    "data": datetime.now().isoformat(),
                    "usuario_id": usuario_id,
                    "usuario_nome": usuario_nome,
                    "tipo_alteracao": "prescricao",
                    "campo": "prescricao_id",
                    "valor_antigo": prescricao_id_anterior,
                    "valor_novo": dados.prescricao_substituta_id,
                    "motivo": dados.motivo
                })
                ag.historico_alteracoes = historico_agendamento
                flag_modified(ag, "historico_alteracoes")

                await agendamento_provider.atualizar_agendamento(ag, commit=False)

            await recalcular_status_prescricao(
                prescricao_provider,
                agendamento_provider,
                dados.prescricao_substituta_id,
                usuario_id=usuario_id,
                usuario_nome=usuario_nome,
                commit=False
            )

        return PrescricaoResponse.model_validate(prescricao)

    if status_novo in [PrescricaoStatusEnum.SUSPENSA.value, PrescricaoStatusEnum.CANCELADA.value]:
        prescricao.status = status_novo
        _append_historico_status(prescricao, status_anterior, status_novo, usuario_id, usuario_nome, dados.motivo)
        await prescricao_provider.atualizar_prescricao(prescricao)

        agendamentos = await agendamento_provider.listar_por_prescricao(prescricao.id, incluir_concluidos=False)
        for ag in agendamentos:
            status_anterior_ag = ag.status
            ag.status = 'suspenso'
            detalhes = dict(ag.detalhes) if ag.detalhes else {}
            detalhes_suspensao = detalhes.get('suspensao') or {}
            detalhes_suspensao.setdefault('motivo_suspensao', 'sem_processo')
            detalhes_suspensao['observacoes'] = f"Suspenso automaticamente pela prescrição {status_novo}."
            detalhes['suspensao'] = detalhes_suspensao
            ag.detalhes = detalhes
            flag_modified(ag, "detalhes")

            historico_agendamento = list(ag.historico_alteracoes or [])
            historico_agendamento.append({
                "data": datetime.now().isoformat(),
                "usuario_id": usuario_id,
                "usuario_nome": usuario_nome,
                "tipo_alteracao": "status",
                "campo": "status",
                "valor_antigo": status_anterior_ag,
                "valor_novo": "suspenso",
                "motivo": dados.motivo
            })
            ag.historico_alteracoes = historico_agendamento
            flag_modified(ag, "historico_alteracoes")

            await agendamento_provider.atualizar_agendamento(ag)

        return PrescricaoResponse.model_validate(prescricao)

    prescricao.status = status_novo
    _append_historico_status(prescricao, status_anterior, status_novo, usuario_id, usuario_nome, dados.motivo)
    atualizado = await prescricao_provider.atualizar_prescricao(prescricao)
    return PrescricaoResponse.model_validate(atualizado)


async def gerar_pdf_prescricao(
        prescricao_id: str,
        prescricao_provider: PrescricaoProviderInterface,
):
    prescricao_db = await prescricao_provider.obter_prescricao(prescricao_id)
    if not prescricao_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prescrição não encontrada")

    dados_prescricao = prescricao_db.conteudo

    mapa_categorias = {
        'pre_med': 'Pré-Medicação',
        'qt': 'Terapia',
        'pos_med_hospitalar': 'Pós-Medicação (Hospitalar)',
        'pos_med_domiciliar': 'Pós-Medicação (Domiciliar)',
        'infusor': 'Instalação de Infusor'
    }

    for bloco in dados_prescricao['blocos']:
        cat_codigo = bloco.get('categoria')
        bloco['categoria_label'] = mapa_categorias.get(cat_codigo, cat_codigo.upper())

        for item in bloco['itens']:
            un = item.get('unidade', '')
            item['unidade_formatada'] = un.split('/')[0] if '/' in un else 'mg' if 'AUC' in un else un

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, 'templates')

    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('prescricao_pdf.html')

    data_emissao_dt = datetime.fromisoformat(dados_prescricao['data_emissao'])
    data_formatada = data_emissao_dt.strftime("%d/%m/%Y")
    hora_geracao = datetime.now().strftime("%d/%m/%Y às %H:%M")

    html_content = template.render(
        prescricao=dados_prescricao,
        data_formatada=data_formatada,
        data_hora_geracao=hora_geracao
    )

    pdf_file = HTML(string=html_content).write_pdf()

    return StreamingResponse(
        io.BytesIO(pdf_file),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename=prescricao_{prescricao_id}.pdf"}
    )
