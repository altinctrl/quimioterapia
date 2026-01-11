from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.agendamento import Agendamento
from src.providers.interfaces.agendamento_provider_interface import AgendamentoProviderInterface


class AgendamentoSQLAlchemyProvider(AgendamentoProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_agendamentos(self, data_inicio: Optional[date] = None, data_fim: Optional[date] = None) -> List[Agendamento]:
        query = select(Agendamento).options(selectinload(Agendamento.paciente), selectinload(Agendamento.criado_por))

        if data_inicio:
            query = query.where(Agendamento.data >= data_inicio)
        if data_fim:
            query = query.where(Agendamento.data <= data_fim)

        query = query.order_by(Agendamento.data, Agendamento.horario_inicio)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obter_agendamento(self, agendamento_id: str) -> Optional[Agendamento]:
        query = select(Agendamento).where(Agendamento.id == agendamento_id).options(selectinload(Agendamento.paciente), selectinload(Agendamento.criado_por))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def criar_agendamento(self, agendamento: Agendamento) -> Agendamento:
        self.session.add(agendamento)
        await self.session.commit()

        query = select(Agendamento).where(Agendamento.id == agendamento.id).options(selectinload(Agendamento.paciente), selectinload(Agendamento.criado_por))
        result = await self.session.execute(query)
        return result.scalar_one()

    async def atualizar_agendamento(self, agendamento: Agendamento) -> Agendamento:
        await self.session.commit()

        query = select(Agendamento).where(Agendamento.id == agendamento.id).options(selectinload(Agendamento.paciente), selectinload(Agendamento.criado_por))
        result = await self.session.execute(query)
        return result.scalar_one()
