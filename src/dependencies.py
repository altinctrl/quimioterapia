import os
from typing import Callable

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.providers.implementations.agendamento_sqlalchemy_provider import AgendamentoSQLAlchemyProvider
from src.providers.implementations.configuracao_sqlalchemy_provider import ConfiguracaoSQLAlchemyProvider
from src.providers.implementations.paciente_csv_provider import PacienteCsvProvider
from src.providers.implementations.paciente_db_provider import PacienteDBProvider
from src.providers.implementations.paciente_postgres_provider import PacientePostgresProvider
from src.providers.implementations.prescricao_sqlalchemy_provider import PrescricaoSQLAlchemyProvider
from src.providers.implementations.protocolo_sqlalchemy_provider import ProtocoloSQLAlchemyProvider
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.providers.interfaces.configuracao_provider_interface import ConfiguracaoProviderInterface
from src.providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.providers.interfaces.protocolo_provider_interface import ProtocoloProviderInterface
from src.resources.database import get_aghu_db_session, get_app_db_session


def _get_paciente_postgres_provider(session: AsyncSession = Depends(get_aghu_db_session)) -> PacienteProviderInterface:
    return PacientePostgresProvider(session=session)


def _get_paciente_csv_provider() -> PacienteProviderInterface:
    csv_path = os.getenv("PACIENTE_CSV_PATH", "data/pacientes.csv")
    return PacienteCsvProvider(csv_path=csv_path)


def _get_paciente_app_db_provider(session: AsyncSession = Depends(get_app_db_session)) -> PacienteProviderInterface:
    """Provider que usa o banco local da aplicação (suporta escrita)."""
    return PacienteDBProvider(session=session)


def get_paciente_provider(strategy: str = "APP_DB") -> Callable[..., PacienteProviderInterface]:
    """
    Fábrica para PacienteProvider.
    Opções:
    - 'POSTGRES': Leitura do legado.
    - 'CSV': Mock local.
    - 'APP_DB': Banco local da aplicação (Recomendado para suportar edição de pacientes).
    """
    # Se strategy não for passado, tenta pegar do ENV, senão usa APP_DB
    if not strategy or strategy == "APP_DB":
        strategy = os.getenv("PACIENTE_PROVIDER_TYPE", "APP_DB")

    if strategy.upper() == "POSTGRES":
        return _get_paciente_postgres_provider
    elif strategy.upper() == "CSV":
        return _get_paciente_csv_provider
    else:
        return _get_paciente_app_db_provider


def get_protocolo_provider(session: AsyncSession = Depends(get_app_db_session)) -> ProtocoloProviderInterface:
    return ProtocoloSQLAlchemyProvider(session=session)


def get_agendamento_provider(session: AsyncSession = Depends(get_app_db_session)) -> AgendamentoProviderInterface:
    return AgendamentoSQLAlchemyProvider(session=session)


def get_prescricao_provider(session: AsyncSession = Depends(get_app_db_session)) -> PrescricaoProviderInterface:
    return PrescricaoSQLAlchemyProvider(session=session)


def get_configuracao_provider(session: AsyncSession = Depends(get_app_db_session)) -> ConfiguracaoProviderInterface:
    return ConfiguracaoSQLAlchemyProvider(session=session)
