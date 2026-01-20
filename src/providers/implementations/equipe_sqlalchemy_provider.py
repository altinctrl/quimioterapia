from datetime import date
from typing import List, Optional

from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload

from src.models.equipe import Profissional, EscalaPlantao, AusenciaProfissional
from src.providers.interfaces.equipe_provider_interface import EquipeProviderInterface
from src.schemas.equipe import ProfissionalCreate, EscalaPlantaoCreate, AusenciaProfissionalCreate


class EquipeSqlAlchemyProvider(EquipeProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def criar_profissional(self, profissional: ProfissionalCreate) -> Profissional:
        db_profissional = Profissional(
            username=profissional.username,
            nome=profissional.nome,
            cargo=profissional.cargo,
            registro=profissional.registro,
            ativo=profissional.ativo
        )
        self.session.add(db_profissional)
        await self.session.commit()
        await self.session.refresh(db_profissional)
        return db_profissional

    async def buscar_profissional_por_username(self, username: str) -> Optional[Profissional]:
        stmt = select(Profissional).where(Profissional.username == username)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def listar_profissionais(self, apenas_ativos: bool = True) -> List[Profissional]:
        stmt = select(Profissional)
        if apenas_ativos:
            stmt = stmt.where(Profissional.ativo == True)

        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def atualizar_profissional(self, username: str, dados: ProfissionalCreate) -> Optional[Profissional]:
        db_prof = await self.buscar_profissional_por_username(username)
        if not db_prof:
            return None

        db_prof.nome = dados.nome
        db_prof.cargo = dados.cargo
        db_prof.registro = dados.registro
        db_prof.ativo = dados.ativo

        await self.session.commit()
        await self.session.refresh(db_prof)
        return db_prof

    async def adicionar_item_escala(self, escala: EscalaPlantaoCreate) -> EscalaPlantao:
        db_escala = EscalaPlantao(
            data=escala.data,
            profissional_id=escala.profissional_id,
            funcao=escala.funcao,
            turno=escala.turno
        )
        self.session.add(db_escala)
        await self.session.commit()
        await self.session.refresh(db_escala)
        stmt = select(EscalaPlantao).options(joinedload(EscalaPlantao.profissional)).where(
            EscalaPlantao.id == db_escala.id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def listar_escala_dia(self, data: date) -> List[EscalaPlantao]:
        stmt = (
            select(EscalaPlantao)
            .options(joinedload(EscalaPlantao.profissional))
            .where(EscalaPlantao.data == data)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def remover_item_escala(self, item_id: str) -> bool:
        stmt = select(EscalaPlantao).where(EscalaPlantao.id == item_id)
        result = await self.session.execute(stmt)
        item = result.scalars().first()

        if item:
            await self.session.delete(item)
            await self.session.commit()
            return True
        return False

    async def registrar_ausencia(self, ausencia: AusenciaProfissionalCreate) -> AusenciaProfissional:
        db_ausencia = AusenciaProfissional(
            profissional_id=ausencia.profissional_id,
            data_inicio=ausencia.data_inicio,
            data_fim=ausencia.data_fim,
            motivo=ausencia.motivo,
            observacao=ausencia.observacao
        )
        self.session.add(db_ausencia)
        await self.session.commit()
        await self.session.refresh(db_ausencia)

        stmt = select(AusenciaProfissional).options(joinedload(AusenciaProfissional.profissional)).where(
            AusenciaProfissional.id == db_ausencia.id
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def listar_ausencias_periodo(self, data_inicio: date, data_fim: date) -> List[AusenciaProfissional]:
        stmt = (
            select(AusenciaProfissional)
            .options(joinedload(AusenciaProfissional.profissional))
            .where(
                and_(
                    AusenciaProfissional.data_inicio <= data_fim,
                    AusenciaProfissional.data_fim >= data_inicio
                )
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def remover_ausencia(self, ausencia_id: str) -> bool:
        stmt = select(AusenciaProfissional).where(AusenciaProfissional.id == ausencia_id)
        result = await self.session.execute(stmt)
        item = result.scalars().first()

        if item:
            await self.session.delete(item)
            await self.session.commit()
            return True
        return False
