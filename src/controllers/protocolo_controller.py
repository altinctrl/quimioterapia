import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm.attributes import flag_modified

from src.models.protocolo import Protocolo
from src.providers.interfaces.protocolo_provider_interface import ProtocoloProviderInterface
from src.schemas.protocolo import ProtocoloCreate, ProtocoloUpdate, ProtocoloResponse


def _montar_resposta(protocolo: Protocolo) -> ProtocoloResponse:
    return ProtocoloResponse.model_validate(protocolo)


async def listar_protocolos(provider: ProtocoloProviderInterface, ativo: bool = None) -> List[ProtocoloResponse]:
    protocolos = await provider.listar_protocolos(ativo)
    return [_montar_resposta(p) for p in protocolos]


async def obter_protocolo(provider: ProtocoloProviderInterface, protocolo_id: str) -> ProtocoloResponse:
    protocolo = await provider.obter_protocolo(protocolo_id)
    if not protocolo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocolo não encontrado")
    return _montar_resposta(protocolo)


async def criar_protocolo(
        provider: ProtocoloProviderInterface,
        dados: ProtocoloCreate,
) -> ProtocoloResponse:
    novo_id = str(uuid.uuid4())
    dados_dict = dados.model_dump(mode='json')
    protocolo = Protocolo(**dados_dict, id=novo_id)
    criado = await provider.criar_protocolo(protocolo)
    return _montar_resposta(criado)


async def criar_protocolo_multi(
        provider: ProtocoloProviderInterface,
        dados: List[ProtocoloCreate],
) -> List[ProtocoloResponse]:
    protocolos = []
    for protocolo in dados:
        novo_id = str(uuid.uuid4())
        dados_dict = protocolo.model_dump(mode='json')
        protocolos.append(Protocolo(**dados_dict, id=novo_id))
    criados = await provider.criar_protocolo_multi(protocolos)
    validados = []
    for protocolo in criados:
        validados.append(ProtocoloResponse.model_validate(protocolo))
    return validados


async def atualizar_protocolo(
        provider: ProtocoloProviderInterface,
        protocolo_id: str,
        dados: ProtocoloUpdate,
) -> ProtocoloResponse:
    protocolo = await provider.obter_protocolo(protocolo_id)
    if not protocolo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocolo não encontrado")

    update_data = dados.model_dump(exclude_unset=True, mode='json')

    for key, value in update_data.items():
        setattr(protocolo, key, value)
        if key in ["templates_ciclo", "dias_semana_permitidos"]:
            flag_modified(protocolo, key)

    atualizado = await provider.atualizar_protocolo(protocolo)
    return _montar_resposta(atualizado)


async def deletar_protocolo(provider: ProtocoloProviderInterface, protocolo_id: str):
    sucesso = await provider.deletar_protocolo(protocolo_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocolo não encontrado")
    return {"message": "Protocolo removido com sucesso"}
