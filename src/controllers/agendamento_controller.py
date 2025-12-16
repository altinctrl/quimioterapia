import uuid
from datetime import date
from typing import List, Optional

from fastapi import HTTPException, status

from src.models.agendamento import Agendamento
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.schemas.agendamento import AgendamentoCreate, AgendamentoUpdate, AgendamentoResponse


async def listar_agendamentos(provider: AgendamentoProviderInterface, data_inicio: Optional[date],
        data_fim: Optional[date]) -> List[AgendamentoResponse]:
    agendamentos = await provider.listar_agendamentos(data_inicio, data_fim)
    return [AgendamentoResponse.model_validate(a) for a in agendamentos]


async def criar_agendamento(provider: AgendamentoProviderInterface, dados: AgendamentoCreate) -> AgendamentoResponse:
    novo_id = str(uuid.uuid4())
    agendamento = Agendamento(**dados.model_dump(), id=novo_id)
    criado = await provider.criar_agendamento(agendamento)
    return AgendamentoResponse.model_validate(criado)


async def atualizar_agendamento(provider: AgendamentoProviderInterface, agendamento_id: str,
                                dados: AgendamentoUpdate) -> AgendamentoResponse:
    agendamento = await provider.obter_agendamento(agendamento_id)
    if not agendamento:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

    update_data = dados.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(agendamento, key, value)

    atualizado = await provider.atualizar_agendamento(agendamento)
    return AgendamentoResponse.model_validate(atualizado)
