from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.prescricao import Prescricao
from src.providers.interfaces.prescricao_provider_interface import PrescricaoProviderInterface


class PrescricaoSQLAlchemyProvider(PrescricaoProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_por_paciente(self, paciente_id: str) -> List[Prescricao]:
        query = select(Prescricao).where(Prescricao.paciente_id == paciente_id).options(
            selectinload(Prescricao.itens)).order_by(Prescricao.data_prescricao.desc())

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obter_prescricao(self, prescricao_id: str) -> Optional[Prescricao]:
        query = select(Prescricao).where(Prescricao.id == prescricao_id).options(selectinload(Prescricao.itens))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def criar_prescricao(self, prescricao: Prescricao) -> Prescricao:
        self.session.add(prescricao)
        await self.session.commit()
        return await self.obter_prescricao(prescricao.id)
