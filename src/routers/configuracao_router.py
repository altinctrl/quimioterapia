from fastapi import APIRouter, Depends

from src.auth.auth_handler import auth_handler
from src.controllers import configuracao_controller
from src.dependencies import get_configuracao_provider
from src.providers.interfaces.configuracao_provider_interface import ConfiguracaoProviderInterface
from src.schemas.configuracao_schema import ConfiguracaoUpdate, ConfiguracaoResponse

router = APIRouter(prefix="/api/configuracoes", tags=["Configurações"],
    dependencies=[Depends(auth_handler.decode_token)])


@router.get("", response_model=ConfiguracaoResponse)
async def obter_configuracao(provider: ConfiguracaoProviderInterface = Depends(get_configuracao_provider)):
    return await configuracao_controller.obter_configuracao(provider)


@router.put("", response_model=ConfiguracaoResponse)
async def atualizar_configuracao(dados: ConfiguracaoUpdate,
        provider: ConfiguracaoProviderInterface = Depends(get_configuracao_provider)):
    return await configuracao_controller.atualizar_configuracao(provider, dados)
