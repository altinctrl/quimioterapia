from fastapi import APIRouter, Depends
from typing import List

from ..controllers import prescricao_controller
from ..dependencies import get_prescricao_provider
from ..providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from ..schemas.prescricao import PrescricaoCreate, PrescricaoResponse
from ..auth.auth import auth_handler

STRATEGY = "POSTGRES"

router = APIRouter(
    prefix="/api/prescricoes",
    tags=["Prescrições"],
    dependencies=[Depends(auth_handler.decode_token)]
)

@router.post("", response_model=PrescricaoResponse)
async def criar(
    prescricao: PrescricaoCreate,
    provider: PrescricaoProviderInterface = Depends(get_prescricao_provider(STRATEGY))
):
    return await prescricao_controller.criar_prescricao(prescricao, provider)

@router.get("/paciente/{paciente_id}", response_model=List[PrescricaoResponse])
async def listar_por_paciente(
    paciente_id: int,
    provider: PrescricaoProviderInterface = Depends(get_prescricao_provider(STRATEGY))
):
    return await prescricao_controller.listar_por_paciente(paciente_id, provider)