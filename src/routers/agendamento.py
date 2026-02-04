from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException

from src.auth.auth import auth_handler, require_groups
from src.controllers import agendamento_controller
from src.dependencies import get_agendamento_provider, get_prescricao_provider
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.schemas.agendamento import AgendamentoCreate, AgendamentoUpdate, AgendamentoResponse, \
    AgendamentoBulkUpdateList, AgendamentoPrescricaoUpdate, AgendamentoRemarcacaoRequest, \
    AgendamentoRemarcacaoLoteRequest

router = APIRouter(prefix="/api/agendamentos", tags=["Agendamentos"], dependencies=[Depends(auth_handler.decode_token)])


@router.get("", response_model=List[AgendamentoResponse])
async def listar_agendamentos(
        data_inicio: Optional[date] = Query(None),
        data_fim: Optional[date] = Query(None),
        paciente_id: Optional[str] = Query(None),
        agendamento_provider: AgendamentoProviderInterface = Depends(get_agendamento_provider),
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider)
):
    return await agendamento_controller.listar_agendamentos(
        agendamento_provider,
        prescricao_provider,
        data_inicio,
        data_fim,
        paciente_id
    )


@router.post("", response_model=AgendamentoResponse)
async def criar_agendamento(
        dados: AgendamentoCreate,
        agendamento_provider: AgendamentoProviderInterface = Depends(get_agendamento_provider),
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
        current_user: dict = Depends(auth_handler.get_current_user)
):
    user_id = current_user.get("username") or current_user.get("sub")
    user_name = current_user.get("display_name") or current_user.get("displayName")
    if not user_id: raise HTTPException(status_code=400, detail="Usuário não identificado no token.")

    return await agendamento_controller.criar_agendamento(
        agendamento_provider,
        prescricao_provider,
        dados,
        criado_por_id=user_id,
        usuario_nome=user_name
    )


@router.put("/lote", response_model=List[AgendamentoResponse])
async def atualizar_agendamentos_em_lote(
        dados: AgendamentoBulkUpdateList,
        provider: AgendamentoProviderInterface = Depends(get_agendamento_provider),
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
        current_user: dict = Depends(auth_handler.get_current_user)
):
    user_id = current_user.get("username") or current_user.get("sub")
    user_name = current_user.get("display_name") or current_user.get("displayName")
    return await agendamento_controller.atualizar_agendamentos_lote(
        provider=provider,
        prescricao_provider=prescricao_provider,
        dados_lote=dados,
        usuario_id=user_id,
        usuario_nome=user_name,
    )


@router.put("/{agendamento_id}", response_model=AgendamentoResponse)
async def atualizar_agendamento(
        agendamento_id: str,
        dados: AgendamentoUpdate,
        provider: AgendamentoProviderInterface = Depends(get_agendamento_provider),
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
        current_user: dict = Depends(auth_handler.get_current_user)
):
    user_id = current_user.get("username") or current_user.get("sub")
    user_name = current_user.get("display_name") or current_user.get("displayName")
    return await agendamento_controller.atualizar_agendamento(provider, prescricao_provider, agendamento_id, dados,
                                                              usuario_id=user_id, usuario_nome=user_name)


@router.put("/{agendamento_id}/prescricao", response_model=AgendamentoResponse)
async def trocar_prescricao_agendamento(
        agendamento_id: str,
        dados: AgendamentoPrescricaoUpdate,
        provider: AgendamentoProviderInterface = Depends(get_agendamento_provider),
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
        current_user: dict = Depends(require_groups(["Enfermagem", "Medicos", "Administradores"]))
):
    user_id = current_user.get("username") or current_user.get("sub")
    user_name = current_user.get("display_name") or current_user.get("displayName")
    return await agendamento_controller.trocar_prescricao_agendamento(
        provider,
        prescricao_provider,
        agendamento_id,
        dados,
        usuario_id=user_id,
        usuario_nome=user_name
    )


@router.post("/{agendamento_id}/remarcar", response_model=AgendamentoResponse)
async def remarcar_agendamento_endpoint(
        agendamento_id: str,
        dados: AgendamentoRemarcacaoRequest,
        provider: AgendamentoProviderInterface = Depends(get_agendamento_provider),
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
        current_user: dict = Depends(auth_handler.get_current_user)
):
    user_id = current_user.get("username") or current_user.get("sub")
    user_name = current_user.get("display_name") or current_user.get("displayName")
    return await agendamento_controller.remarcar_agendamento(
        provider, prescricao_provider, agendamento_id, dados, user_id, user_name
    )


@router.post("/remarcar-lote", response_model=List[AgendamentoResponse])
async def remarcar_lote_endpoint(
        dados: AgendamentoRemarcacaoLoteRequest,
        provider: AgendamentoProviderInterface = Depends(get_agendamento_provider),
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
        current_user: dict = Depends(auth_handler.get_current_user)
):
    user_id = current_user.get("username") or current_user.get("sub")
    user_name = current_user.get("display_name") or current_user.get("displayName")
    return await agendamento_controller.remarcar_agendamentos_lote(
        provider, prescricao_provider, dados, user_id, user_name
    )
