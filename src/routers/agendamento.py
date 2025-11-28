from fastapi import APIRouter, Depends
from typing import List

from ..controllers import agendamento_controller
from ..dependencies import get_agendamento_provider
from ..providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from ..schemas.agendamento import AgendamentoCreate, AgendamentoResponse, AgendamentoUpdateStatus
from ..auth.auth import auth_handler

STRATEGY = "POSTGRES"

router = APIRouter(
    prefix="/api/agendamentos",
    tags=["Agendamentos"],
    dependencies=[Depends(auth_handler.decode_token)]
)

@router.get("/dia/{data}", response_model=List[AgendamentoResponse])
async def listar_por_data(
    data: str,
    provider: AgendamentoProviderInterface = Depends(get_agendamento_provider(STRATEGY))
):
    """Lista agendamentos de uma data específica (YYYY-MM-DD)."""
    return await agendamento_controller.listar_agendamentos_do_dia(data, provider)

@router.post("", response_model=AgendamentoResponse)
async def criar(
    agendamento: AgendamentoCreate,
    provider: AgendamentoProviderInterface = Depends(get_agendamento_provider(STRATEGY))
):
    """Cria um novo agendamento com horário definido pelo frontend."""
    return await agendamento_controller.criar_agendamento(agendamento, provider)

@router.patch("/{agendamento_id}/status", response_model=AgendamentoResponse)
async def atualizar_status(
    agendamento_id: int,
    status_data: AgendamentoUpdateStatus,
    provider: AgendamentoProviderInterface = Depends(get_agendamento_provider(STRATEGY))
):
    """Atualiza o status (e.g. 'em-infusao', 'concluido') e observações."""
    return await agendamento_controller.atualizar_status(agendamento_id, status_data, provider)