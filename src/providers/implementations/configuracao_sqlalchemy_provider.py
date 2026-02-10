from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.configuracao_model import Configuracao
from src.providers.interfaces.configuracao_provider_interface import ConfiguracaoProviderInterface


class ConfiguracaoSQLAlchemyProvider(ConfiguracaoProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def obter_configuracao(self) -> Configuracao:
        query = select(Configuracao).where(Configuracao.id == 1)
        result = await self.session.execute(query)
        config = result.scalar_one_or_none()

        if not config:
            config = Configuracao(id=1)
            self.session.add(config)
            await self.session.commit()
            await self.session.refresh(config)

        return config

    async def salvar_configuracao(self, configuracao: Configuracao) -> Configuracao:
        if configuracao.id != 1:
            configuracao.id = 1

        self.session.add(configuracao)
        await self.session.merge(configuracao)
        await self.session.commit()
        await self.session.refresh(configuracao)
        return configuracao
