from abc import ABC, abstractmethod
from typing import List, Dict, Any


class PoltronaProviderInterface(ABC):
    @abstractmethod
    async def listar_poltronas(self) -> List[Dict[str, Any]]:
        """Lista todas as poltronas e leitos cadastrados."""
        pass

    @abstractmethod
    async def obter_poltrona(self, poltrona_id: int) -> Dict[str, Any]:
        pass