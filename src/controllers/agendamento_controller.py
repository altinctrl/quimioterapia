from typing import List, Dict, Any
from ..providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from ..schemas.agendamento import AgendamentoCreate, AgendamentoUpdateStatus

async def listar_agendamentos_do_dia(data: str, provider: AgendamentoProviderInterface) -> List[Dict[str, Any]]:
    return await provider.listar_agendamentos_do_dia(data)

async def criar_agendamento(agendamento: AgendamentoCreate, provider: AgendamentoProviderInterface) -> Dict[str, Any]:
    return await provider.criar_agendamento(agendamento)

async def atualizar_status(id: int, status: AgendamentoUpdateStatus, provider: AgendamentoProviderInterface) -> Dict[str, Any]:
    return await provider.atualizar_status(id, status)