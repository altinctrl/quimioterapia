from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from ..interfaces.protocolo_provider_interface import ProtocoloProviderInterface
from ...models.protocolo import Protocolo
from ...schemas.protocolo import ProtocoloCreate

class ProtocoloPostgresProvider(ProtocoloProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_protocolos(self) -> List[Dict[str, Any]]:
        result = await self.session.execute(select(Protocolo))
        protocolos = result.scalars().all()
        return [{c.name: getattr(p, c.name) for c in p.__table__.columns} for p in protocolos]

    async def obter_protocolo(self, id: int) -> Dict[str, Any]:
        protocolo = await self.session.get(Protocolo, id)
        if not protocolo:
            raise HTTPException(status_code=404, detail="Protocolo não encontrado")
        return {c.name: getattr(protocolo, c.name) for c in protocolo.__table__.columns}

    async def criar_protocolo(self, protocolo_schema: ProtocoloCreate) -> Dict[str, Any]:
        novo_protocolo = Protocolo(**protocolo_schema.model_dump())
        self.session.add(novo_protocolo)
        await self.session.commit()
        await self.session.refresh(novo_protocolo)
        return {c.name: getattr(novo_protocolo, c.name) for c in novo_protocolo.__table__.columns}