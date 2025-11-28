from typing import List, Dict, Any
from ..providers.interfaces.poltrona_provider_interface import PoltronaProviderInterface

async def listar_poltronas(provider: PoltronaProviderInterface) -> List[Dict[str, Any]]:
    return await provider.listar_poltronas()