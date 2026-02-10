from datetime import date

from fastapi import APIRouter, Depends

from src.auth.auth import auth_handler
from src.controllers import relatorio_controller
from src.dependencies import get_agendamento_provider, get_prescricao_provider, get_equipe_provider
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.providers.interfaces.equipe_provider_interface import EquipeProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface

router = APIRouter(prefix="/api/relatorios", tags=["Relatórios"], dependencies=[Depends(auth_handler.decode_token)])

@router.get("/fim-plantao")
async def relatorio_fim_plantao(
        data_inicio: date,
        data_fim: date = None,
        agendamento_provider: AgendamentoProviderInterface = Depends(get_agendamento_provider),
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider),
        equipe_provider: EquipeProviderInterface = Depends(get_equipe_provider)
):
    if not data_fim: data_fim = data_inicio
    return await relatorio_controller.gerar_relatorio_fim_plantao(
        data_inicio,
        data_fim,
        agendamento_provider,
        prescricao_provider,
        equipe_provider
    )

@router.get("/medicacoes")
async def relatorio_medicacoes(
        data_inicio: date,
        data_fim: date = None,
        agendamento_provider: AgendamentoProviderInterface = Depends(get_agendamento_provider),
        prescricao_provider: PrescricaoProviderInterface = Depends(get_prescricao_provider)
):
    if not data_fim: data_fim = data_inicio
    return await relatorio_controller.gerar_relatorio_medicacoes(
        data_inicio,
        data_fim,
        agendamento_provider,
        prescricao_provider
    )
