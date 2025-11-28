from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ...schemas.prescricao import PrescricaoCreate

class PrescricaoProviderInterface(ABC):
    @abstractmethod
    async def criar_prescricao(self, prescricao: PrescricaoCreate) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def listar_por_paciente(self, paciente_id: int) -> List[Dict[str, Any]]:
        pass