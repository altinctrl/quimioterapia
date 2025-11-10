from fastapi import APIRouter, Depends
from typing import List

from ..controllers import paciente_controller
# Alteração: Importamos apenas a FÁBRICA
from ..dependencies import get_paciente_provider
from ..providers.interfaces.paciente_provider_interface import PacienteProviderInterface

from ..auth.auth import auth_handler

# --- PONTO ÚNICO DE CONFIGURAÇÃO PARA ESTE ROTEADOR ---
# Para usar o banco de dados em produção, altere esta linha para "postgres"
STRATEGY = "csv"
# ----------------------------------------------------

router = APIRouter(
    prefix="/api/pacientes",
    tags=["Pacientes"],
    dependencies=[Depends(auth_handler.decode_token)]
)

@router.get("", response_model=List[dict])
async def listar_pacientes(
    # A mágica acontece aqui:
    # 1. get_paciente_provider(STRATEGY) retorna a função _get_paciente_csv_provider
    # 2. FastAPI efetivamente executa Depends(_get_paciente_csv_provider)
    provider: PacienteProviderInterface = Depends(get_paciente_provider(STRATEGY))
):
    """Lista todos os pacientes da fonte de dados configurada no roteador."""
    return await paciente_controller.listar_pacientes(provider)

@router.get("/{codigo}", response_model=dict)
async def obter_paciente(
    codigo: int,
    provider: PacienteProviderInterface = Depends(get_paciente_provider(STRATEGY))
):
    """Obtém um paciente pelo código a partir da fonte de dados configurada no roteador."""
    return await paciente_controller.obter_paciente_por_codigo(codigo, provider)
