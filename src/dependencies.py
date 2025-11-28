import os
from typing import Callable
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from .providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from .providers.interfaces.poltrona_provider_interface import PoltronaProviderInterface
from .providers.interfaces.protocolo_provider_interface import ProtocoloProviderInterface
from .providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface

from .providers.implementations.paciente_postgres_provider import PacientePostgresProvider
from .providers.implementations.agendamento_postgres_provider import AgendamentoPostgresProvider
from .providers.implementations.poltrona_postgres_provider import PoltronaPostgresProvider
from .providers.implementations.protocolo_postgres_provider import ProtocoloPostgresProvider
from .providers.implementations.prescricao_postgres_provider import PrescricaoPostgresProvider

from .providers.implementations.paciente_csv_provider import PacienteCsvProvider
from .resources.database import get_aghu_db_session, get_app_db_session


def _get_paciente_postgres_provider(
    session: AsyncSession = Depends(get_aghu_db_session)
) -> PacienteProviderInterface:
    return PacientePostgresProvider(session=session)

def _get_paciente_csv_provider() -> PacienteProviderInterface:
    csv_path = os.getenv("PACIENTE_CSV_PATH", "data/pacientes.csv")
    return PacienteCsvProvider(csv_path=csv_path)

def get_paciente_provider(strategy: str) -> Callable[..., PacienteProviderInterface]:
    if strategy.upper() == "POSTGRES":
        return _get_paciente_postgres_provider
    elif strategy.upper() == "CSV":
        return _get_paciente_csv_provider
    else:
        raise ValueError(f"Estratégia desconhecida para Paciente: {strategy}")


def _get_agendamento_postgres_provider(
    session: AsyncSession = Depends(get_app_db_session)
) -> AgendamentoProviderInterface:
    return AgendamentoPostgresProvider(session=session)

def get_agendamento_provider(strategy: str) -> Callable[..., AgendamentoProviderInterface]:
    if strategy.upper() == "POSTGRES":
        return _get_agendamento_postgres_provider
    raise ValueError(f"Estratégia desconhecida para Agendamento: {strategy}")


def _get_poltrona_postgres_provider(
    session: AsyncSession = Depends(get_app_db_session)
) -> PoltronaProviderInterface:
    return PoltronaPostgresProvider(session=session)

def get_poltrona_provider(strategy: str) -> Callable[..., PoltronaProviderInterface]:
    if strategy.upper() == "POSTGRES":
        return _get_poltrona_postgres_provider
    raise ValueError(f"Estratégia desconhecida para Poltrona: {strategy}")


def _get_protocolo_postgres_provider(
    session: AsyncSession = Depends(get_app_db_session)
) -> ProtocoloProviderInterface:
    return ProtocoloPostgresProvider(session=session)

def get_protocolo_provider(strategy: str) -> Callable[..., ProtocoloProviderInterface]:
    if strategy.upper() == "POSTGRES":
        return _get_protocolo_postgres_provider
    raise ValueError(f"Estratégia desconhecida para Protocolo: {strategy}")


def _get_prescricao_postgres_provider(
    session: AsyncSession = Depends(get_app_db_session)
) -> PrescricaoProviderInterface:
    return PrescricaoPostgresProvider(session=session)

def get_prescricao_provider(strategy: str) -> Callable[..., PrescricaoProviderInterface]:
    if strategy.upper() == "POSTGRES":
        return _get_prescricao_postgres_provider
    raise ValueError(f"Estratégia desconhecida para Prescrição: {strategy}")