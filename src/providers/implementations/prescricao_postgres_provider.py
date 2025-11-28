from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ...models.prescricao import PrescricaoMedica
from ..interfaces.prescricao_provider_interface import PrescricaoProviderInterface
from ...schemas.prescricao import PrescricaoCreate


class PrescricaoPostgresProvider(PrescricaoProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def criar_prescricao(self, prescricao_schema: PrescricaoCreate) -> Dict[str, Any]:
        dados = prescricao_schema.model_dump()

        nova_prescricao = PrescricaoMedica(**dados)

        self.session.add(nova_prescricao)
        await self.session.commit()
        await self.session.refresh(nova_prescricao)

        return {c.name: getattr(nova_prescricao, c.name) for c in nova_prescricao.__table__.columns}

    async def listar_por_paciente(self, paciente_id: int) -> List[Dict[str, Any]]:
        stmt = select(PrescricaoMedica).where(PrescricaoMedica.paciente_id == paciente_id).order_by(
            PrescricaoMedica.created_at.desc())
        result = await self.session.execute(stmt)
        prescricoes = result.scalars().all()

        lista_retorno = []
        for p in prescricoes:
            p_dict = {c.name: getattr(p, c.name) for c in p.__table__.columns}
            lista_retorno.append(p_dict)

        return lista_retorno