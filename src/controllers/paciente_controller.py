import uuid
from math import ceil
from typing import List

from fastapi import HTTPException, status

from src.models.paciente_model import Paciente, ContatoEmergencia
from src.providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from src.schemas.paciente_schema import PacienteCreate, PacienteUpdate, PacienteResponse, PacientePagination, \
    PacienteImportResponse


async def listar_pacientes(
    provider: PacienteProviderInterface,
    termo: str = None,
    page: int = 1,
    size: int = 10,
    ordenacao: str = 'recentes'
) -> PacientePagination:
    todos_pacientes = await provider.listar_pacientes(termo, ordenacao)

    total = len(todos_pacientes)
    total_pages = ceil(total / size)

    start = (page - 1) * size
    end = start + size
    paginated_items = todos_pacientes[start:end]

    items_resp = [PacienteResponse.model_validate(p) for p in paginated_items]

    return PacientePagination(items=items_resp, total=total, page=page, size=size, pages=total_pages)


async def obter_paciente(provider: PacienteProviderInterface, paciente_id: str) -> PacienteResponse:
    paciente = await provider.obter_paciente_por_codigo(paciente_id)
    if not paciente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")
    return PacienteResponse.model_validate(paciente)


async def criar_paciente(provider: PacienteProviderInterface, dados: PacienteCreate) -> PacienteResponse:
    paciente_existente = await provider.obter_paciente_por_cpf(dados.cpf)

    if paciente_existente:
        return PacienteResponse.model_validate(paciente_existente)

    novo_id = str(uuid.uuid4())

    paciente_dict = dados.model_dump(exclude={"contatos_emergencia"})
    paciente = Paciente(**paciente_dict, id=novo_id)

    for contato in dados.contatos_emergencia:
        paciente.contatos_emergencia.append(ContatoEmergencia(**contato.model_dump()))

    criado = await provider.criar_paciente(paciente)
    return PacienteResponse.model_validate(criado)


async def atualizar_paciente(provider: PacienteProviderInterface, paciente_id: str,
                             dados: PacienteUpdate) -> PacienteResponse:
    paciente = await provider.obter_paciente_por_codigo(paciente_id)
    if not paciente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

    update_data = dados.model_dump(exclude_unset=True)

    if "contatos_emergencia" in update_data:
        contatos_data = update_data.pop("contatos_emergencia")
        paciente.contatos_emergencia.clear()
        for c in contatos_data:
            paciente.contatos_emergencia.append(ContatoEmergencia(**c))

    for key, value in update_data.items():
        setattr(paciente, key, value)

    atualizado = await provider.atualizar_paciente(paciente)
    return PacienteResponse.model_validate(atualizado)


async def buscar_pacientes_externos(
        legacy_provider: PacienteProviderInterface,
        local_provider: PacienteProviderInterface,
        termo: str,
        limit: int = 100,
) -> List[PacienteImportResponse]:
    pacientes_legados = await legacy_provider.listar_pacientes(termo, limit=limit)
    if not pacientes_legados: return []

    cpfs_externos = [p.cpf for p in pacientes_legados if p.cpf]
    pacientes_locais = await local_provider.obter_paciente_por_cpf_multi(cpfs_externos)
    mapa_local = {p.cpf: p.id for p in pacientes_locais}

    resultado = []
    for p_legado in pacientes_legados:
        id_local = mapa_local.get(p_legado.cpf)
        ja_cadastrado = id_local is not None
        resultado.append(PacienteImportResponse(
            id=id_local if ja_cadastrado else None,
            nome=p_legado.nome,
            cpf=p_legado.cpf,
            registro=p_legado.registro,
            data_nascimento=p_legado.data_nascimento
        ))

    return resultado
