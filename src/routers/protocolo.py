from fastapi import APIRouter, Depends
from typing import List

from ..controllers import protocolo_controller
from ..dependencies import get_protocolo_provider
from ..providers.interfaces.protocolo_provider_interface import ProtocoloProviderInterface
from ..schemas.protocolo import ProtocoloCreate, ProtocoloResponse
from ..auth.auth import auth_handler

STRATEGY = "POSTGRES"

router = APIRouter(
    prefix="/api/protocolos",
    tags=["Protocolos"],
    dependencies=[Depends(auth_handler.decode_token)]
)

@router.get("", response_model=List[ProtocoloResponse])
async def listar(
    provider: ProtocoloProviderInterface = Depends(get_protocolo_provider(STRATEGY))
):
    return await protocolo_controller.listar_protocolos(provider)

@router.post("", response_model=ProtocoloResponse)
async def criar(
    protocolo: ProtocoloCreate,
    provider: ProtocoloProviderInterface = Depends(get_protocolo_provider(STRATEGY))
):
    return await protocolo_controller.criar_protocolo(protocolo, provider)