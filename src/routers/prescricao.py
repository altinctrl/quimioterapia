from typing import List

from fastapi import APIRouter, Depends

from src.auth.auth import auth_handler
from src.controllers import prescricao_controller
from src.dependencies import get_prescricao_provider, get_paciente_provider
from src.providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.schemas.prescricao import PrescricaoCreate, PrescricaoResponse

router = APIRouter(prefix="/api/prescricoes", tags=["Prescrições"], dependencies=[Depends(auth_handler.decode_token)])


@router.get("/paciente/{paciente_id}", response_model=List[PrescricaoResponse])
async def listar_prescricoes_por_paciente(paciente_id: str,
        provider: PrescricaoProviderInterface = Depends(get_prescricao_provider)):
    return await prescricao_controller.listar_prescricoes(provider, paciente_id)


@router.post("", response_model=PrescricaoResponse)
async def criar_prescricao(dados: PrescricaoCreate,
        provider: PrescricaoProviderInterface = Depends(get_prescricao_provider)):
    return await prescricao_controller.criar_prescricao(provider, dados)


@router.get("/{prescricao_id}/pdf")
async def gerar_pdf(prescricao_id: str,
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
        paciente_provider: PacienteProviderInterface = Depends(get_paciente_provider())):
    return await prescricao_controller.gerar_pdf_prescricao(prescricao_id, prescricao_provider, paciente_provider)
