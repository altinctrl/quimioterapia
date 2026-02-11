from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.providers.implementations.agendamento_sqlalchemy_provider import AgendamentoSQLAlchemyProvider
from src.providers.implementations.auth_sqlalchemy_provider import AuthSqlAlchemyProvider
from src.providers.implementations.configuracao_sqlalchemy_provider import ConfiguracaoSQLAlchemyProvider
from src.providers.implementations.equipe_sqlalchemy_provider import EquipeSqlAlchemyProvider
from src.providers.implementations.paciente_sqlalchemy_provider import PacienteSQLAlchemyProvider
from src.providers.implementations.paciente_legacy_provider import PacienteLegacyProvider
from src.providers.implementations.prescricao_sqlalchemy_provider import PrescricaoSQLAlchemyProvider
from src.providers.implementations.protocolo_sqlalchemy_provider import ProtocoloSQLAlchemyProvider
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from src.providers.interfaces.auth_provider_interface import AuthProviderInterface
from src.providers.interfaces.configuracao_provider_interface import ConfiguracaoProviderInterface
from src.providers.interfaces.equipe_provider_interface import EquipeProviderInterface
from src.providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from src.providers.interfaces.protocolo_provider_interface import ProtocoloProviderInterface
from src.resources.database import get_app_db_session
from src.resources.database_aghu import get_aghu_db_session


def get_paciente_legacy_provider(session: AsyncSession = Depends(get_aghu_db_session)) -> PacienteProviderInterface:
    return PacienteLegacyProvider(session=session)


def get_paciente_provider(session: AsyncSession = Depends(get_app_db_session)) -> PacienteProviderInterface:
    return PacienteSQLAlchemyProvider(session=session)


def get_protocolo_provider(session: AsyncSession = Depends(get_app_db_session)) -> ProtocoloProviderInterface:
    return ProtocoloSQLAlchemyProvider(session=session)


def get_agendamento_provider(session: AsyncSession = Depends(get_app_db_session)) -> AgendamentoProviderInterface:
    return AgendamentoSQLAlchemyProvider(session=session)


def get_prescricao_provider(session: AsyncSession = Depends(get_app_db_session)) -> PrescricaoProviderInterface:
    return PrescricaoSQLAlchemyProvider(session=session)


def get_configuracao_provider(session: AsyncSession = Depends(get_app_db_session)) -> ConfiguracaoProviderInterface:
    return ConfiguracaoSQLAlchemyProvider(session=session)


async def get_equipe_provider(db: AsyncSession = Depends(get_app_db_session)) -> EquipeProviderInterface:
    return EquipeSqlAlchemyProvider(db)


async def get_auth_provider(session: AsyncSession = Depends(get_app_db_session)) -> AuthProviderInterface:
    return AuthSqlAlchemyProvider(session)
