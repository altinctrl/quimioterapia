from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ...schemas.protocolo import ProtocoloCreate


class ProtocoloProviderInterface(ABC):
    @abstractmethod
    async def listar_protocolos(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    async def obter_protocolo(self, id: int) -> Dict[str, Any]:
        pass

    @abstractmethod
    async def criar_protocolo(self, protocolo: ProtocoloCreate) -> Dict[str, Any]:
        pass