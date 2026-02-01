from typing import List

from fastapi import APIRouter, Depends

from src.auth.auth import auth_handler, require_groups
from src.controllers import prescricao_controller
from src.dependencies import get_prescricao_provider, get_equipe_provider, get_agendamento_provider
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.providers.interfaces.equipe_provider_interface import EquipeProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.schemas.prescricao import PrescricaoCreate, PrescricaoResponse, PrescricaoStatusUpdate, PrescricaoSubstituicaoCreate

router = APIRouter(prefix="/api/prescricoes", tags=["Prescrições"], dependencies=[Depends(auth_handler.decode_token)])


@router.get("/paciente/{paciente_id}", response_model=List[PrescricaoResponse])
async def listar_prescricoes_por_paciente(
        paciente_id: str,
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
):
    return await prescricao_controller.listar_prescricoes_por_paciente(prescricao_provider, paciente_id)


@router.post("", response_model=PrescricaoResponse)
async def criar_prescricao(
        dados: PrescricaoCreate,
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
        equipe_provider: EquipeProviderInterface = Depends(get_equipe_provider),
        current_user: dict = Depends(require_groups(["Medicos", "Administradores"]))
):
    return await prescricao_controller.criar_prescricao(prescricao_provider, equipe_provider, dados)


@router.post("/substituir", response_model=PrescricaoResponse)
async def criar_prescricao_substituicao(
                dados: PrescricaoSubstituicaoCreate,
                prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
                equipe_provider: EquipeProviderInterface = Depends(get_equipe_provider),
                agendamento_provider: AgendamentoProviderInterface = Depends(get_agendamento_provider),
                current_user: dict = Depends(require_groups(["Medicos", "Administradores"]))
):
        user_id = current_user.get("username") or current_user.get("sub")
        user_name = current_user.get("display_name") or current_user.get("displayName")

        return await prescricao_controller.criar_prescricao_substituicao_atomic(
                prescricao_provider,
                equipe_provider,
                agendamento_provider,
                dados,
                usuario_id=user_id,
                usuario_nome=user_name
        )


# TODO: Criar endpoint para atualizar status da prescrição
@router.put("/{prescricao_id}/status", response_model=PrescricaoResponse)
async def atualizar_status_prescricao(
                prescricao_id: str,
                dados: PrescricaoStatusUpdate,
                prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
                agendamento_provider: AgendamentoProviderInterface = Depends(get_agendamento_provider),
                current_user: dict = Depends(require_groups(["Medicos", "Administradores"]))
):
        user_id = current_user.get("username") or current_user.get("sub")
        user_name = current_user.get("display_name") or current_user.get("displayName")

        return await prescricao_controller.atualizar_status_prescricao(
                prescricao_provider,
                agendamento_provider,
                prescricao_id,
                dados,
                usuario_id=user_id,
                usuario_nome=user_name
        )


@router.get("/{prescricao_id}/pdf")
async def gerar_pdf(
        prescricao_id: str,
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
):
    return await prescricao_controller.gerar_pdf_prescricao(prescricao_id, prescricao_provider)
