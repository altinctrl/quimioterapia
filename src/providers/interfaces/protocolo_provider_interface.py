from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.protocolo_model import Protocolo


class ProtocoloProviderInterface(ABC):
    @abstractmethod
    async def listar_protocolos(self, ativo: Optional[bool] = None) -> List[Protocolo]:
        pass

    @abstractmethod
    async def obter_protocolo(self, protocolo_id: str) -> Optional[Protocolo]:
        pass

    @abstractmethod
    async def criar_protocolo(self, protocolo: Protocolo) -> Protocolo:
        pass

    @abstractmethod
    async def criar_protocolo_multi(self, protocolo: List[Protocolo]) -> List[Protocolo]:
        pass

    @abstractmethod
    async def atualizar_protocolo(self, protocolo: Protocolo) -> Protocolo:
        pass

    @abstractmethod
    async def deletar_protocolo(self, protocolo_id: str) -> bool:
        pass
