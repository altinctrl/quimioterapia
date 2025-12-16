from abc import ABC, abstractmethod

from src.models.configuracao import Configuracao


class ConfiguracaoProviderInterface(ABC):
    @abstractmethod
    async def obter_configuracao(self) -> Configuracao:
        pass

    @abstractmethod
    async def salvar_configuracao(self, configuracao: Configuracao) -> Configuracao:
        pass
