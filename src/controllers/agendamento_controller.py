import uuid
from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm.attributes import flag_modified  # Importação necessária

from src.models.agendamento import Agendamento
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.schemas.agendamento import AgendamentoCreate, AgendamentoUpdate, AgendamentoResponse, TipoAgendamento
from src.schemas.prescricao import PrescricaoResponse


async def listar_agendamentos(
        agendamento_provider: AgendamentoProviderInterface,
        prescricao_provider: PrescricaoProviderInterface,
        data_inicio: Optional[date],
        data_fim: Optional[date]
) -> List[AgendamentoResponse]:
    agendamentos = await agendamento_provider.listar_agendamentos(data_inicio, data_fim)
    if not agendamentos: return []

    paciente_ids = list(set([a.paciente_id for a in agendamentos if a.paciente_id]))
    prescricoes = await prescricao_provider.listar_por_paciente_multi(paciente_ids)
    mapa_prescricoes = {p.paciente_id: p for p in reversed(prescricoes)}

    response = []
    for ag in agendamentos:
        ag_resp = AgendamentoResponse.model_validate(ag)

        if ag.paciente_id in mapa_prescricoes:
            prescricao_obj = mapa_prescricoes[ag.paciente_id]
            p_resp = PrescricaoResponse.model_validate(prescricao_obj)
            p_resp.protocolo = prescricao_obj.protocolo_nome_snapshot
            p_dict = p_resp.model_dump()
            p_dict['qt'] = [i for i in prescricao_obj.itens if i.tipo == 'qt']
            p_dict['medicamentos'] = [i for i in prescricao_obj.itens if i.tipo == 'pre']
            p_dict['pos_medicacoes'] = [i for i in prescricao_obj.itens if i.tipo == 'pos']
            ag_resp.prescricao = PrescricaoResponse(**p_dict)

        response.append(ag_resp)

    return response


async def criar_agendamento(
        provider: AgendamentoProviderInterface,
        dados: AgendamentoCreate,
        criado_por_id: str
) -> AgendamentoResponse:
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

    atualizado = await provider.atualizar_agendamento(agendamento)
    return AgendamentoResponse.model_validate(atualizado)
