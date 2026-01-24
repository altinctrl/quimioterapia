from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.protocolo import Protocolo
from src.providers.interfaces.protocolo_provider_interface import ProtocoloProviderInterface


class ProtocoloSQLAlchemyProvider(ProtocoloProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_protocolos(self, ativo: Optional[bool] = None) -> List[Protocolo]:
        query = select(Protocolo)
        if ativo is not None:
            query = query.where(Protocolo.ativo == ativo)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def obter_protocolo(self, protocolo_id: str) -> Optional[Protocolo]:
        query = select(Protocolo).where(Protocolo.id == protocolo_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def criar_protocolo(self, protocolo: Protocolo) -> Protocolo:
        self.session.add(protocolo)
        await self.session.commit()
        query = select(Protocolo).where(Protocolo.id == protocolo.id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def criar_protocolo_multi(self, protocolos: List[Protocolo]) -> List[Protocolo]:
        self.session.add_all(protocolos)
        await self.session.commit()
        for p in protocolos:
            await self.session.refresh(p)
        return protocolos

    async def atualizar_protocolo(self, protocolo: Protocolo) -> Protocolo:
        self.session.add(protocolo)
        await self.session.commit()
        query = select(Protocolo).where(Protocolo.id == protocolo.id)
        result = await self.session.execute(query)
        return result.scalar_one()

    async def deletar_protocolo(self, protocolo_id: str) -> bool:
        protocolo = await self.obter_protocolo(protocolo_id)
        if protocolo:
            await self.session.delete(protocolo)
            await self.session.commit()
            return True
        return False
