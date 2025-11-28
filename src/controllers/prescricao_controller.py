from typing import List, Dict, Any
from ..providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from ..schemas.prescricao import PrescricaoCreate

async def criar_prescricao(prescricao: PrescricaoCreate, provider: PrescricaoProviderInterface) -> Dict[str, Any]:
    return await provider.criar_prescricao(prescricao)

async def listar_por_paciente(paciente_id: int, provider: PrescricaoProviderInterface) -> List[Dict[str, Any]]:
    return await provider.listar_por_paciente(paciente_id)