from typing import List, Optional

from sqlalchemy import select, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.paciente import Paciente
from src.models.prescricao import Prescricao
from src.providers.interfaces.paciente_provider_interface import PacienteProviderInterface


class PacienteSQLAlchemyProvider(PacienteProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_pacientes(self, termo: Optional[str] = None, ordenacao: str = None, limit: int = 100) -> List[Paciente]:
        subquery_protocolo = (
            select(Prescricao.conteudo['protocolo', 'nome'].astext)
            .where(Prescricao.paciente_id == Paciente.id)
            .order_by(desc(Prescricao.data_emissao))
            .limit(1)
            .correlate(Paciente)
            .scalar_subquery()
        )

        query = select(Paciente, subquery_protocolo.label("ultimo_protocolo_nome")).limit(limit).options(
            selectinload(Paciente.contatos_emergencia)
        )
        if termo:
            t = f"%{termo}%"
            query = query.where(or_(Paciente.nome.ilike(t), Paciente.cpf.ilike(t), Paciente.registro.ilike(t)))

        if ordenacao and ordenacao == 'nome_asc':
            query = query.order_by(Paciente.nome.asc())
        elif ordenacao and ordenacao == 'nome_desc':
            query = query.order_by(Paciente.registro.desc())
        elif ordenacao and ordenacao == 'registro':
            query = query.order_by(Paciente.registro.asc())
        else:
            query = query.order_by(Paciente.created_at.desc())

        result = await self.session.execute(query)

        pacientes = []
        for row in result.all():
            paciente = row[0]
            nome_protocolo = row[1]
            paciente.protocolo_ultima_prescricao = nome_protocolo
            pacientes.append(paciente)

        return pacientes

    async def obter_paciente_por_codigo(self, codigo: str) -> Optional[Paciente]:
        query = select(Paciente).where(Paciente.id == codigo).options(selectinload(Paciente.contatos_emergencia))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def obter_paciente_por_cpf(self, cpf: str) -> Optional[Paciente]:
        query = select(Paciente).where(Paciente.cpf == cpf).options(selectinload(Paciente.contatos_emergencia))
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def obter_paciente_por_cpf_multi(self, cpfs: List[str]) -> List[Paciente]:
        if not cpfs: return []
        query = select(Paciente).where(Paciente.cpf.in_(cpfs))
        result = await self.session.execute(query)
        return list(result.scalars().all())

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
