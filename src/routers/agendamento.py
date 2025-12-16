from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from src.auth.auth import auth_handler
from src.controllers import agendamento_controller
from src.dependencies import get_agendamento_provider
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.schemas.agendamento import AgendamentoCreate, AgendamentoUpdate, AgendamentoResponse

router = APIRouter(prefix="/api/agendamentos", tags=["Agendamentos"], dependencies=[Depends(auth_handler.decode_token)])


@router.get("", response_model=List[AgendamentoResponse])
async def listar_agendamentos(data_inicio: Optional[date] = Query(None), data_fim: Optional[date] = Query(None),
        provider: AgendamentoProviderInterface = Depends(get_agendamento_provider)):
    return await agendamento_controller.listar_agendamentos(provider, data_inicio, data_fim)


@router.post("", response_model=AgendamentoResponse)
async def criar_agendamento(dados: AgendamentoCreate,
        provider: AgendamentoProviderInterface = Depends(get_agendamento_provider)):
    return await agendamento_controller.criar_agendamento(provider, dados)


@router.put("/{agendamento_id}", response_model=AgendamentoResponse)
async def atualizar_agendamento(agendamento_id: str, dados: AgendamentoUpdate,
        provider: AgendamentoProviderInterface = Depends(get_agendamento_provider)):
    return await agendamento_controller.atualizar_agendamento(provider, agendamento_id, dados)
