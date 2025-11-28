from typing import List, Dict, Any
from ..providers.interfaces.protocolo_provider_interface import ProtocoloProviderInterface
from ..schemas.protocolo import ProtocoloCreate

async def listar_protocolos(provider: ProtocoloProviderInterface) -> List[Dict[str, Any]]:
    return await provider.listar_protocolos()

async def criar_protocolo(protocolo: ProtocoloCreate, provider: ProtocoloProviderInterface) -> Dict[str, Any]:
    return await provider.criar_protocolo(protocolo)