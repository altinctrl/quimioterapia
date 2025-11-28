from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ...schemas.agendamento import AgendamentoCreate, AgendamentoUpdateStatus


class AgendamentoProviderInterface(ABC):
    @abstractmethod
    async def listar_agendamentos_do_dia(self, data: str) -> List[Dict[str, Any]]:
        """Lista agendamentos de uma data específica."""
        pass

    @abstractmethod
    async def criar_agendamento(self, agendamento: AgendamentoCreate) -> Dict[str, Any]:
        """Cria um novo agendamento no banco de dados."""
        pass

    @abstractmethod
    async def atualizar_status(self, agendamento_id: int, status_data: AgendamentoUpdateStatus) -> Dict[str, Any]:
        """Atualiza o status de um agendamento."""
        pass