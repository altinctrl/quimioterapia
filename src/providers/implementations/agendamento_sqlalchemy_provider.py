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

    async def commit(self):
        await self.session.commit()

    async def listar_agendamentos(self, data_inicio: Optional[date] = None, data_fim: Optional[date] = None, paciente_id: Optional[str] = None) -> List[Agendamento]:
        query = select(Agendamento).options(selectinload(Agendamento.paciente), selectinload(Agendamento.criado_por))

        if data_inicio:
            query = query.where(Agendamento.data >= data_inicio)
        if data_fim:
            query = query.where(Agendamento.data <= data_fim)
        if paciente_id:
            query = query.where(Agendamento.paciente_id == paciente_id)

        query = query.order_by(Agendamento.data, Agendamento.horario_inicio)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obter_agendamento(self, agendamento_id: str) -> Optional[Agendamento]:
        query = select(Agendamento).where(Agendamento.id == agendamento_id).options(selectinload(Agendamento.paciente), selectinload(Agendamento.criado_por))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def buscar_por_id_multi(self, ids: List[str]) -> List[Agendamento]:
        query = select(Agendamento).where(Agendamento.id.in_(ids)).options(selectinload(Agendamento.paciente), selectinload(Agendamento.criado_por))
        result = await self.session.execute(query)
        return result.scalars().all()


    async def buscar_por_prescricao_e_dia(self, prescricao_id: str, dia_ciclo: int) -> List[Agendamento]:
        query = select(Agendamento).where(
            Agendamento.detalhes['infusao']['prescricao_id'].astext == prescricao_id,
            Agendamento.detalhes['infusao']['dia_ciclo'].as_integer() == dia_ciclo
        )

        result = await self.session.execute(query)
        return result.scalars().all()


    async def listar_por_prescricao(self, prescricao_id: str, incluir_concluidos: bool = True) -> List[Agendamento]:
        query = select(Agendamento).where(
            Agendamento.detalhes['infusao']['prescricao_id'].as_string() == prescricao_id
        )

        if not incluir_concluidos:
            query = query.where(Agendamento.status != 'concluido')

        result = await self.session.execute(query)
        return result.scalars().all()


    async def criar_agendamento(self, agendamento: Agendamento, commit: bool = True) -> Agendamento:
        self.session.add(agendamento)
        if commit:
            await self.session.commit()
        else:
            await self.session.flush()

        query = select(Agendamento).where(Agendamento.id == agendamento.id).options(selectinload(Agendamento.paciente), selectinload(Agendamento.criado_por))
        result = await self.session.execute(query)
        return result.scalar_one()

    async def atualizar_agendamento(self, agendamento: Agendamento, commit: bool = True) -> Agendamento:
        if commit:
            await self.session.commit()
        else:
            await self.session.flush()

        query = select(Agendamento).where(Agendamento.id == agendamento.id).options(selectinload(Agendamento.paciente), selectinload(Agendamento.criado_por))
        result = await self.session.execute(query)
        return result.scalar_one()

    async def atualizar_agendamento_multi(self, agendamentos: List[Agendamento]) -> List[Agendamento]:
        await self.session.commit()
        ids = [a.id for a in agendamentos]
        return await self.buscar_por_id_multi(ids)
