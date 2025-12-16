from typing import List, Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.paciente import Paciente
from src.providers.interfaces.paciente_provider_interface import PacienteProviderInterface


class PacienteDBProvider(PacienteProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_pacientes(self, termo: Optional[str] = None) -> List[Paciente]:
        query = select(Paciente).options(selectinload(Paciente.contatos_emergencia))

        if termo:
            t = f"%{termo}%"
            query = query.where(or_(Paciente.nome.ilike(t), Paciente.cpf.ilike(t), Paciente.registro.ilike(t)))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obter_paciente_por_codigo(self, codigo: str) -> Optional[Paciente]:
        query = select(Paciente).where(Paciente.id == codigo).options(selectinload(Paciente.contatos_emergencia))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def obter_paciente_por_cpf(self, cpf: str) -> Optional[Paciente]:
        query = select(Paciente).where(Paciente.cpf == cpf).options(selectinload(Paciente.contatos_emergencia))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def criar_paciente(self, paciente: Paciente) -> Paciente:
        self.session.add(paciente)
        await self.session.commit()
        query = select(Paciente).where(Paciente.id == paciente.id).options(selectinload(Paciente.contatos_emergencia))
        result = await self.session.execute(query)
        return result.scalar_one()

    async def atualizar_paciente(self, paciente: Paciente) -> Paciente:
        self.session.add(paciente)
        await self.session.commit()
        query = select(Paciente).where(Paciente.id == paciente.id).options(selectinload(Paciente.contatos_emergencia))
        result = await self.session.execute(query)
        return result.scalar_one()
