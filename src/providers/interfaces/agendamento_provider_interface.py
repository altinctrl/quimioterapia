from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from src.models.agendamento import Agendamento


class AgendamentoProviderInterface(ABC):
    @abstractmethod
    async def listar_agendamentos(
            self,
            data_inicio: Optional[date] = None,
            data_fim: Optional[date] = None,
            paciente_id: Optional[str] = None,
    ) -> List[Agendamento]:
        pass

    @abstractmethod
    async def obter_agendamento(
            self, agendamento_id: str,
    ) -> Optional[Agendamento]:
        pass

    @abstractmethod
    async def buscar_por_id_multi(self, ids: List[str]) -> List[Agendamento]:
        pass

    @abstractmethod
    async def buscar_por_prescricao_e_dia(
            self,
            prescricao_id: str,
            dia_ciclo: int,
    ) -> List[Agendamento]:
        pass

    @abstractmethod
    async def listar_por_prescricao(
            self,
            prescricao_id: str,
            incluir_concluidos: bool = True,
    ) -> List[Agendamento]:
        pass

    @abstractmethod
    async def criar_agendamento(
            self, agendamento: Agendamento,
            commit: bool = True,
    ) -> Agendamento:
        pass

    @abstractmethod
    async def atualizar_agendamento(
            self, agendamento: Agendamento,
            commit: bool = True,
    ) -> Agendamento:
        pass

    @abstractmethod
    async def atualizar_agendamento_multi(self, agendamentos: List[Agendamento]) -> List[Agendamento]:
        pass
