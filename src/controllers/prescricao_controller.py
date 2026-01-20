import io
import os
import uuid
from datetime import datetime
from typing import List

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

from src.models.prescricao import Prescricao
from src.providers.interfaces.equipe_provider_interface import EquipeProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.schemas.prescricao import PrescricaoCreate, PrescricaoResponse, MedicoSnapshot


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
