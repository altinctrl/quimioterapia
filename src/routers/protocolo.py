from typing import List, Optional, Union

from fastapi import APIRouter, Depends, Query

from src.auth.auth import auth_handler
from src.controllers import protocolo_controller
from src.dependencies import get_protocolo_provider
from src.providers.interfaces.protocolo_provider_interface import ProtocoloProviderInterface
from src.schemas.protocolo import ProtocoloCreate, ProtocoloUpdate, ProtocoloResponse

router = APIRouter(prefix="/api/protocolos", tags=["Protocolos"], dependencies=[Depends(auth_handler.decode_token)])


@router.get("", response_model=List[ProtocoloResponse])
async def listar_protocolos(ativo: Optional[bool] = Query(None),
        provider: ProtocoloProviderInterface = Depends(get_protocolo_provider)):
    return await protocolo_controller.listar_protocolos(provider, ativo)


@router.get("/{protocolo_id}", response_model=ProtocoloResponse)
async def obter_protocolo(protocolo_id: str, provider: ProtocoloProviderInterface = Depends(get_protocolo_provider)):
    return await protocolo_controller.obter_protocolo(provider, protocolo_id)


@router.post("", response_model=Union[ProtocoloResponse, List[ProtocoloResponse]])
async def criar_protocolo(
    dados: Union[ProtocoloCreate, List[ProtocoloCreate]],
    provider: ProtocoloProviderInterface = Depends(get_protocolo_provider),
):
    if isinstance(dados, list):
        return await protocolo_controller.criar_protocolo_multi(provider, dados)
    return await protocolo_controller.criar_protocolo(provider, dados)


@router.put("/{protocolo_id}", response_model=ProtocoloResponse)
async def atualizar_protocolo(protocolo_id: str, dados: ProtocoloUpdate,
        provider: ProtocoloProviderInterface = Depends(get_protocolo_provider)):
    return await protocolo_controller.atualizar_protocolo(provider, protocolo_id, dados)


@router.delete("/{protocolo_id}")
async def deletar_protocolo(protocolo_id: str, provider: ProtocoloProviderInterface = Depends(get_protocolo_provider)):
    return await protocolo_controller.deletar_protocolo(provider, protocolo_id)
