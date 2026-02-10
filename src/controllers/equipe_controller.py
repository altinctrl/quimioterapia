from datetime import date

from fastapi import HTTPException, status

from src.providers.interfaces.equipe_provider_interface import EquipeProviderInterface
from src.schemas.equipe import (
    ProfissionalCreate,
    EscalaPlantaoCreate,
    AusenciaProfissionalCreate
)


async def criar_profissional(
        dados: ProfissionalCreate,
        provider: EquipeProviderInterface
):
    novo_prof = await provider.promover_usuario_a_profissional(dados)

    if not novo_prof:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado. O profissional deve fazer login no sistema ao menos uma vez antes de ser adicionado à equipe."
        )
    return novo_prof


async def listar_profissionais(
        provider: EquipeProviderInterface,
        apenas_ativos: bool = True
):
    return await provider.listar_profissionais(apenas_ativos)


async def atualizar_profissional(
        username: str,
        dados: ProfissionalCreate,
        provider: EquipeProviderInterface
):
    profissional = await provider.atualizar_profissional(username, dados)
    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profissional não encontrado."
        )
    return profissional


async def adicionar_escala(
        escala: EscalaPlantaoCreate,
        provider: EquipeProviderInterface
):
    profissional = await provider.buscar_profissional_por_username(escala.profissional_id)
    if not profissional:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Profissional informado não existe."
        )

    return await provider.adicionar_item_escala(escala)


async def listar_escala_dia(
        data: date,
        provider: EquipeProviderInterface
):
    return await provider.listar_escala_dia(data)


async def remover_escala(
        item_id: str,
        provider: EquipeProviderInterface
):
    sucesso = await provider.remover_item_escala(item_id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item de escala não encontrado."
        )
    return {"status": "removido"}


async def registrar_ausencia(
        ausencia: AusenciaProfissionalCreate,
        provider: EquipeProviderInterface
):
    if ausencia.data_fim < ausencia.data_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A data final não pode ser anterior à data inicial."
        )

    return await provider.registrar_ausencia(ausencia)


async def listar_ausencias(
        start: date,
        end: date,
        provider: EquipeProviderInterface
):
    return await provider.listar_ausencias_periodo(start, end)


async def remover_ausencia(
        ausencia_id: str,
        provider: EquipeProviderInterface
):
    sucesso = await provider.remover_ausencia(ausencia_id)
    if not sucesso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ausência não encontrada."
        )
    return {"status": "removida"}
