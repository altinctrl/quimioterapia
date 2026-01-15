from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from src.models.agendamento import Agendamento


class AgendamentoProviderInterface(ABC):
    @abstractmethod
    async def listar_agendamentos(self, data_inicio: Optional[date] = None, data_fim: Optional[date] = None, paciente_id: Optional[str] = None) -> List[
        Agendamento]:
        pass

    @abstractmethod
    async def obter_agendamento(self, agendamento_id: str) -> Optional[Agendamento]:
        pass

    @abstractmethod
    async def criar_agendamento(self, agendamento: Agendamento) -> Agendamento:
        pass

    @abstractmethod
    async def atualizar_agendamento(self, agendamento: Agendamento) -> Agendamento:
        pass
