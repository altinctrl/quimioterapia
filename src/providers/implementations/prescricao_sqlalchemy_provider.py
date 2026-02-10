from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.prescricao_model import Prescricao
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface


class PrescricaoSQLAlchemyProvider(PrescricaoProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_por_paciente(self, paciente_id: str) -> List[Prescricao]:
        query = select(Prescricao).where(Prescricao.paciente_id == paciente_id).order_by(Prescricao.data_emissao.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def listar_por_paciente_multi(self, paciente_ids: List[str]) -> List[Prescricao]:
        if not paciente_ids:
            return []

        query = select(Prescricao).where(
            Prescricao.paciente_id.in_(paciente_ids)
        )

        query = query.order_by(Prescricao.data_emissao.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obter_prescricao(self, prescricao_id: str) -> Optional[Prescricao]:
        query = select(Prescricao).where(Prescricao.id == prescricao_id)

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def obter_prescricao_multi(self, prescricao_ids: List[str]) -> List[Prescricao]:
        if not prescricao_ids:
            return []

        query = select(Prescricao).where(Prescricao.id.in_(prescricao_ids))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def criar_prescricao(self, prescricao: Prescricao, commit: bool = True) -> Prescricao:
        self.session.add(prescricao)
        if commit:
            await self.session.commit()
            return await self.obter_prescricao(prescricao.id)
        await self.session.flush()
        return await self.obter_prescricao(prescricao.id)

    async def atualizar_prescricao(self, prescricao: Prescricao, commit: bool = True) -> Prescricao:
        if commit:
            await self.session.commit()
            return await self.obter_prescricao(prescricao.id)
        await self.session.flush()
        return await self.obter_prescricao(prescricao.id)
