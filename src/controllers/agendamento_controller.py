import uuid
from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm.attributes import flag_modified

from src.models.agendamento import Agendamento
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.schemas.agendamento import AgendamentoCreate, AgendamentoUpdate, AgendamentoResponse, TipoAgendamento, \
    AgendamentoBulkUpdateList
from src.schemas.prescricao import PrescricaoResponse

def _aplicar_regras_atualizacao(agendamento: Agendamento, update_data: dict):
    if 'tipo' in update_data:
        if update_data['tipo'] != agendamento.tipo:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não é permitido alterar o tipo de um agendamento. Cancele este e crie um novo."
            )
        del update_data['tipo']

    novo_status = update_data.get('status', agendamento.status)
    novo_checkin = update_data.get('checkin', agendamento.checkin)

    status_permitidos_sem_checkin = [
        'agendado',
        'aguardando-consulta',
        'aguardando-exame',
        'aguardando-medicamento',
        'internado',
        'suspenso',
        'remarcado'
    ]

    if not novo_checkin and novo_status not in status_permitidos_sem_checkin:
        if 'checkin' in update_data and update_data['checkin'] is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Não é possível remover o Check-in enquanto o paciente estiver com status '{novo_status}'."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O status '{novo_status}' exige que o paciente tenha realizado o Check-in."
            )

    if 'detalhes' in update_data:
        novos_detalhes = update_data['detalhes']
        detalhes_atuais = dict(agendamento.detalhes) if agendamento.detalhes else {}

        mapa_tipo_chave = {
            TipoAgendamento.INFUSAO.value: 'infusao',
            TipoAgendamento.PROCEDIMENTO.value: 'procedimento',
            TipoAgendamento.CONSULTA.value: 'consulta'
        }
        tipo_chave_principal = mapa_tipo_chave.get(agendamento.tipo)
        chaves_proibidas = {v for k, v in mapa_tipo_chave.items() if v != tipo_chave_principal}

        for chave in novos_detalhes.keys():
            if chave in chaves_proibidas:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Agendamento do tipo {agendamento.tipo} não pode ter detalhes de {chave}."
                )

        for chave, valor_novo in novos_detalhes.items():
            valor_atual = detalhes_atuais.get(chave)
            if isinstance(valor_atual, dict) and isinstance(valor_novo, dict):
                valor_atual.update(valor_novo)
            else:
                detalhes_atuais[chave] = valor_novo

        update_data['detalhes'] = detalhes_atuais

    for key, value in update_data.items():
        setattr(agendamento, key, value)

    if 'detalhes' in update_data:
        flag_modified(agendamento, "detalhes")


async def listar_agendamentos(
        agendamento_provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        data_inicio: Optional[date],
        data_fim: Optional[date],
        paciente_id: Optional[str] = None
) -> List[AgendamentoResponse]:
    agendamentos = await agendamento_provider.listar_agendamentos(data_inicio, data_fim, paciente_id)
    if not agendamentos: return []

    prescricao_ids = set()
    for ag in agendamentos:
        if ag.tipo == TipoAgendamento.INFUSAO and ag.detalhes:
            infusao = ag.detalhes.get('infusao')
            if infusao and 'prescricao_id' in infusao: prescricao_ids.add(infusao['prescricao_id'])

    lista_prescricoes = await prescricao_provider.obter_prescricao_multi(list(prescricao_ids))
    mapa_prescricoes = {p.id: p for p in lista_prescricoes}

    response = []
    for ag in agendamentos:
        ag_resp = AgendamentoResponse.model_validate(ag)
        if ag.tipo == 'infusao' and ag.detalhes and 'infusao' in ag.detalhes:
            p_id = ag.detalhes['infusao'].get('prescricao_id')
            if p_id and p_id in mapa_prescricoes:
                prescricao_obj = mapa_prescricoes[p_id]
                p_resp = PrescricaoResponse.model_validate(prescricao_obj)
                ag_resp.prescricao = p_resp
        response.append(ag_resp)

    return response


async def criar_agendamento(
        provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        dados: AgendamentoCreate,
        criado_por_id: str
) -> AgendamentoResponse:
    if dados.tipo == TipoAgendamento.INFUSAO:
        detalhes_inf = dados.detalhes.infusao

        prescricao = await prescricao_provider.obter_prescricao(detalhes_inf.prescricao_id)
        if not prescricao:
            raise HTTPException(status_code=400, detail="Prescrição informada não encontrada.")

        if prescricao.paciente_id != dados.paciente_id:
            raise HTTPException(status_code=400, detail="A prescrição não pertence ao paciente informado.")

        conteudo = prescricao.conteudo
        dias_validos = set()

        if 'blocos' in conteudo:
            for bloco in conteudo['blocos']:
                for item in bloco.get('itens', []):
                    for dia in item.get('dias_do_ciclo', []):
                        dias_validos.add(dia)

        if detalhes_inf.dia_ciclo not in dias_validos:
            dias_str = ", ".join(map(str, sorted(dias_validos)))
            raise HTTPException(
                status_code=400,
                detail=f"Dia do ciclo {detalhes_inf.dia_ciclo} inválido para esta prescrição. Dias válidos com medicação: {dias_str}."
            )

        agendamentos_existentes = await provider.buscar_por_prescricao_e_dia(
            detalhes_inf.prescricao_id,
            detalhes_inf.dia_ciclo
        )

        conflito = [a for a in agendamentos_existentes if a.status not in ['cancelado', 'suspenso', 'remarcado']]

        if conflito:
            data_existente = conflito[0].data.strftime('%d/%m/%Y')
            raise HTTPException(
                status_code=409,
                detail=f"Já existe um agendamento ativo para o Dia {detalhes_inf.dia_ciclo} desta prescrição em {data_existente}. Use a remarcação se necessário."
            )

    novo_id = str(uuid.uuid4())

    agendamento = Agendamento(
        **dados.model_dump(),
        id=novo_id,
        criado_por_id=criado_por_id
    )

    criado = await provider.criar_agendamento(agendamento)
    return AgendamentoResponse.model_validate(criado)


async def atualizar_agendamento(provider: AgendamentoProviderInterface, agendamento_id: str,
                                dados: AgendamentoUpdate) -> AgendamentoResponse:
    agendamento = await provider.obter_agendamento(agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

    update_data = dados.model_dump(exclude_unset=True)
    _aplicar_regras_atualizacao(agendamento, update_data)
    atualizado = await provider.atualizar_agendamento(agendamento)
    return AgendamentoResponse.model_validate(atualizado)


async def atualizar_agendamentos_lote(
        provider: AgendamentoProviderInterface,
        dados_lote: AgendamentoBulkUpdateList
) -> List[AgendamentoResponse]:
    ids = [item.id for item in dados_lote.itens]
    agendamentos_existentes = await provider.buscar_por_id_multi(ids)
    mapa_agendamentos = {a.id: a for a in agendamentos_existentes}

    if len(mapa_agendamentos) != len(set(ids)):
        ids_encontrados = set(mapa_agendamentos.keys())
        ids_faltantes = set(ids) - ids_encontrados
        raise HTTPException(
            status_code=404,
            detail=f"Agendamentos não encontrados: {', '.join(ids_faltantes)}"
        )

    for item_update in dados_lote.itens:
        agendamento = mapa_agendamentos[item_update.id]
        update_data = item_update.model_dump(exclude={'id'}, exclude_unset=True)
        _aplicar_regras_atualizacao(agendamento, update_data)

    atualizados = await provider.atualizar_agendamento_multi(list(mapa_agendamentos.values()))
    return [AgendamentoResponse.model_validate(a) for a in atualizados]
