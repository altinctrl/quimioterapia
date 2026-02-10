from src.providers.interfaces.configuracao_provider_interface import ConfiguracaoProviderInterface
from src.schemas.configuracao_schema import ConfiguracaoUpdate, ConfiguracaoResponse


async def obter_configuracao(provider: ConfiguracaoProviderInterface) -> ConfiguracaoResponse:
    config = await provider.obter_configuracao()
    return ConfiguracaoResponse.model_validate(config)


async def atualizar_configuracao(provider: ConfiguracaoProviderInterface,
                                 dados: ConfiguracaoUpdate) -> ConfiguracaoResponse:
    config_atual = await provider.obter_configuracao()

    update_data = dados.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(config_atual, key, value)

    atualizado = await provider.salvar_configuracao(config_atual)
    return ConfiguracaoResponse.model_validate(atualizado)
