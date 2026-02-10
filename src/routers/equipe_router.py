from datetime import date
from typing import List

from fastapi import APIRouter, Depends

import src.controllers.equipe_controller as controller
from src.dependencies import get_equipe_provider
from src.providers.interfaces.equipe_provider_interface import EquipeProviderInterface
from src.schemas.equipe_schema import ProfissionalCreate, ProfissionalResponse, EscalaPlantaoCreate, EscalaPlantaoResponse, \
    AusenciaProfissionalCreate, AusenciaProfissionalResponse

router = APIRouter(prefix="/api/equipe", tags=["Equipe"])


@router.post("/profissionais", response_model=ProfissionalResponse)
async def criar_profissional(
        payload: ProfissionalCreate,
        provider: EquipeProviderInterface = Depends(get_equipe_provider)
):
    return await controller.criar_profissional(payload, provider)


@router.get("/profissionais", response_model=List[ProfissionalResponse])
async def listar_profissionais(
        apenas_ativos: bool = True,
        provider: EquipeProviderInterface = Depends(get_equipe_provider)
):
    return await controller.listar_profissionais(provider, apenas_ativos)


@router.put("/profissionais/{username}", response_model=ProfissionalResponse)
async def atualizar_profissional(
        username: str,
        payload: ProfissionalCreate,
        provider: EquipeProviderInterface = Depends(get_equipe_provider)
):
    return await controller.atualizar_profissional(username, payload, provider)


@router.post("/escala", response_model=EscalaPlantaoResponse)
async def adicionar_escala(
        payload: EscalaPlantaoCreate,
        provider: EquipeProviderInterface = Depends(get_equipe_provider)
):
    return await controller.adicionar_escala(payload, provider)


@router.get("/escala/{data_escala}", response_model=List[EscalaPlantaoResponse])
async def ver_escala(
        data_escala: date,
        provider: EquipeProviderInterface = Depends(get_equipe_provider)
):
    return await controller.listar_escala_dia(data_escala, provider)


@router.delete("/escala/{item_id}")
async def remover_escala(
        item_id: str,
        provider: EquipeProviderInterface = Depends(get_equipe_provider)
):
    return await controller.remover_escala(item_id, provider)


@router.post("/ausencias", response_model=AusenciaProfissionalResponse)
async def registrar_ausencia(
        payload: AusenciaProfissionalCreate,
        provider: EquipeProviderInterface = Depends(get_equipe_provider)
):
    return await controller.registrar_ausencia(payload, provider)


@router.get("/ausencias", response_model=List[AusenciaProfissionalResponse])
async def listar_ausencias(
        start: date,
        end: date,
        provider: EquipeProviderInterface = Depends(get_equipe_provider)
):
    return await controller.listar_ausencias(start, end, provider)


@router.delete("/ausencias/{ausencia_id}")
async def remover_ausencia(
        ausencia_id: str,
        provider: EquipeProviderInterface = Depends(get_equipe_provider)
):
    return await controller.remover_ausencia(ausencia_id, provider)
