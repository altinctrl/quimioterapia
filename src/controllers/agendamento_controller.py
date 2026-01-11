import uuid
from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm.attributes import flag_modified  # Importação necessária

from src.models.agendamento import Agendamento
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.schemas.agendamento import AgendamentoCreate, AgendamentoUpdate, AgendamentoResponse, TipoAgendamento


async def listar_agendamentos(provider: AgendamentoProviderInterface, data_inicio: Optional[date],
                              data_fim: Optional[date]) -> List[AgendamentoResponse]:
    agendamentos = await provider.listar_agendamentos(data_inicio, data_fim)
    return [AgendamentoResponse.model_validate(a) for a in agendamentos]


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
