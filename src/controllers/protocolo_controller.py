import uuid
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm.attributes import flag_modified

from src.models.protocolo import Protocolo, ItemProtocolo
from src.providers.interfaces.protocolo_provider_interface import ProtocoloProviderInterface
from src.schemas.protocolo import ProtocoloCreate, ProtocoloUpdate, ProtocoloResponse


def _montar_resposta(protocolo: Protocolo) -> ProtocoloResponse:
    resp = ProtocoloResponse.model_validate(protocolo)
    resp_dict = resp.model_dump()

    if protocolo.itens:
        resp_dict['medicamentos'] = [i for i in protocolo.itens if i.tipo == 'qt']
        resp_dict['pre_medicacoes'] = [i for i in protocolo.itens if i.tipo == 'pre']
        resp_dict['pos_medicacoes'] = [i for i in protocolo.itens if i.tipo == 'pos']
    else:
        resp_dict['medicamentos'] = []
        resp_dict['pre_medicacoes'] = []
        resp_dict['pos_medicacoes'] = []

    return ProtocoloResponse(**resp_dict)


async def listar_protocolos(provider: ProtocoloProviderInterface, ativo: bool = None) -> List[ProtocoloResponse]:
    protocolos = await provider.listar_protocolos(ativo)
    return [_montar_resposta(p) for p in protocolos]


async def obter_protocolo(provider: ProtocoloProviderInterface, protocolo_id: str) -> ProtocoloResponse:
    protocolo = await provider.obter_protocolo(protocolo_id)
    if not protocolo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocolo não encontrado")
    return _montar_resposta(protocolo)


async def criar_protocolo(provider: ProtocoloProviderInterface, dados: ProtocoloCreate) -> ProtocoloResponse:
    novo_id = str(uuid.uuid4())

    protocolo_dict = dados.model_dump(
        exclude={"medicamentos", "pre_medicacoes", "pos_medicacoes", "dias_semana_permitidos"})

    protocolo = Protocolo(**protocolo_dict, id=novo_id)

    if dados.dias_semana_permitidos is not None:
        protocolo.dias_semana_permitidos = list(dados.dias_semana_permitidos)

    itens_map = {"qt": dados.medicamentos, "pre": dados.pre_medicacoes, "pos": dados.pos_medicacoes}

    for tipo, lista in itens_map.items():
        for item in lista:
            novo_item = ItemProtocolo(**item.model_dump(), tipo=tipo)
            protocolo.itens.append(novo_item)

    criado = await provider.criar_protocolo(protocolo)
    return _montar_resposta(criado)


async def atualizar_protocolo(provider: ProtocoloProviderInterface, protocolo_id: str,
                              dados: ProtocoloUpdate) -> ProtocoloResponse:
    protocolo = await provider.obter_protocolo(protocolo_id)
    if not protocolo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocolo não encontrado")

    update_data = dados.model_dump(exclude_unset=True,
        exclude={"medicamentos", "pre_medicacoes", "pos_medicacoes", "dias_semana_permitidos"})

    for key, value in update_data.items():
        setattr(protocolo, key, value)

    if dados.dias_semana_permitidos is not None:
        nova_lista = list(dados.dias_semana_permitidos)
        protocolo.dias_semana_permitidos = nova_lista
        flag_modified(protocolo, "dias_semana_permitidos")

    if any(x is not None for x in [dados.medicamentos, dados.pre_medicacoes, dados.pos_medicacoes]):

        def atualizar_tipo(novos_dados, tipo_alvo):
            if novos_dados is not None:
                protocolo.itens = [i for i in protocolo.itens if i.tipo != tipo_alvo]
                for item_data in novos_dados:
                    protocolo.itens.append(ItemProtocolo(**item_data.model_dump(), tipo=tipo_alvo))

        atualizar_tipo(dados.medicamentos, "qt")
        atualizar_tipo(dados.pre_medicacoes, "pre")
        atualizar_tipo(dados.pos_medicacoes, "pos")

    atualizado = await provider.atualizar_protocolo(protocolo)
    return _montar_resposta(atualizado)


async def deletar_protocolo(provider: ProtocoloProviderInterface, protocolo_id: str):
    sucesso = await provider.deletar_protocolo(protocolo_id)
    if not sucesso:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Protocolo não encontrado")
    return {"message": "Protocolo removido com sucesso"}
