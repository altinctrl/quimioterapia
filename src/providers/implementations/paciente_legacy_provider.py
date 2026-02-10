from typing import List, Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.aghu_model import AghuPaciente
from src.models.paciente_model import Paciente
from src.providers.interfaces.paciente_provider_interface import PacienteProviderInterface


class PacienteLegacyProvider(PacienteProviderInterface):
    """
    Lê dados do AGHU (Mock ou Real).
    Mapeia AghuPaciente -> Paciente (App Model)
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    def _map_aghu_to_app(self, aghu_p: AghuPaciente) -> Paciente:
        return Paciente(id=str(aghu_p.codigo),
            nome=aghu_p.nome, cpf=aghu_p.cpf, registro=str(aghu_p.codigo), data_nascimento=aghu_p.dt_nascimento,
            telefone=None,
            email=None)

    async def listar_pacientes(self, termo: Optional[str] = None, ordenacao: str = None, limit: int = 100) -> List[Paciente]:
        query = select(AghuPaciente).limit(limit)

        if termo:
            t = f"%{termo}%"
            try:
                cod = int(termo)
                query = query.where(
                    or_(AghuPaciente.nome.ilike(t), AghuPaciente.codigo == cod, AghuPaciente.cpf.ilike(t)))
            except ValueError:
                query = query.where(or_(AghuPaciente.nome.ilike(t), AghuPaciente.cpf.ilike(t)))

        result = await self.session.execute(query)
        aghu_pacientes = result.scalars().all()
        return [self._map_aghu_to_app(p) for p in aghu_pacientes]

    async def obter_paciente_por_codigo(self, codigo: str) -> Optional[Paciente]:
        try:
            cod_int = int(codigo)
            query = select(AghuPaciente).where(AghuPaciente.codigo == cod_int)
            result = await self.session.execute(query)
            aghu_p = result.scalar_one_or_none()
            return self._map_aghu_to_app(aghu_p) if aghu_p else None
        except ValueError:
            return None

    async def obter_paciente_por_cpf(self, cpf: str) -> Optional[Paciente]:
        query = select(AghuPaciente).where(AghuPaciente.cpf == cpf)
        result = await self.session.execute(query)
        aghu_p = result.scalar_one_or_none()
        return self._map_aghu_to_app(aghu_p) if aghu_p else None

    async def criar_paciente(self, paciente: Paciente) -> Paciente:
        raise NotImplementedError("Não é possível criar paciente diretamente no AGHU por esta API")

    async def atualizar_paciente(self, paciente: Paciente) -> Paciente:
        raise NotImplementedError("Edição no AGHU não permitida")

    async def obter_paciente_por_cpf_multi(self, cpfs: List[str]) -> List[Paciente]:
        raise NotImplementedError
