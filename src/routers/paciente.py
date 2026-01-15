from typing import List, Optional

from fastapi import APIRouter, Depends, Query

from src.auth.auth import auth_handler
from src.controllers import paciente_controller
from src.dependencies import get_paciente_provider, get_paciente_legacy_provider
from src.providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from src.schemas.paciente import PacienteCreate, PacienteUpdate, PacienteResponse, PacientePagination

router = APIRouter(prefix="/api/pacientes", tags=["Pacientes"], dependencies=[Depends(auth_handler.decode_token)])


@router.get("/externo/buscar", response_model=List[PacienteResponse])
async def buscar_paciente_aghu(termo: str = Query(..., min_length=3),
                               provider: PacienteProviderInterface = Depends(get_paciente_legacy_provider)):
    paginacao = await paciente_controller.listar_pacientes(provider, termo, page=1, size=50)
    return paginacao.items


@router.get("", response_model=PacientePagination)
async def listar_pacientes(termo: Optional[str] = Query(None), page: int = Query(1, ge=1),
                           size: int = Query(10, ge=1, le=100),
                           ordenacao: str = Query('recentes'),
                           provider: PacienteProviderInterface = Depends(get_paciente_provider)):
    return await paciente_controller.listar_pacientes(provider, termo, page, size, ordenacao)


@router.get("/{paciente_id}", response_model=PacienteResponse)
async def obter_paciente(paciente_id: str, provider: PacienteProviderInterface = Depends(get_paciente_provider)):
    return await paciente_controller.obter_paciente(provider, paciente_id)


@router.post("", response_model=PacienteResponse)
async def criar_paciente(dados: PacienteCreate, provider: PacienteProviderInterface = Depends(get_paciente_provider)):
    return await paciente_controller.criar_paciente(provider, dados)


@router.put("/{paciente_id}", response_model=PacienteResponse)
async def atualizar_paciente(paciente_id: str, dados: PacienteUpdate,
                             provider: PacienteProviderInterface = Depends(get_paciente_provider)):
    return await paciente_controller.atualizar_paciente(provider, paciente_id, dados)
