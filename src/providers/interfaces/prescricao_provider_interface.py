from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.prescricao import Prescricao


class PrescricaoProviderInterface(ABC):
    @abstractmethod
    async def listar_por_paciente(self, paciente_id: str) -> List[Prescricao]:
        pass

    @abstractmethod
    async def obter_prescricao(self, prescricao_id: str) -> Optional[Prescricao]:
        pass

    @abstractmethod
    async def criar_prescricao(self, prescricao: Prescricao) -> Prescricao:
        pass
