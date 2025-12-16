import uuid
from math import ceil

from fastapi import HTTPException, status

from src.models.paciente import Paciente, ContatoEmergencia
from src.providers.interfaces.paciente_provider_interface import PacienteProviderInterface
from src.schemas.paciente import PacienteCreate, PacienteUpdate, PacienteResponse, PacientePagination


async def listar_pacientes(provider: PacienteProviderInterface, termo: str = None, page: int = 1,
        size: int = 10) -> PacientePagination:
    todos_pacientes = await provider.listar_pacientes(termo)

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
