import os
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from ..interfaces.poltrona_provider_interface import PoltronaProviderInterface
from ...models.poltrona import Poltrona


def get_sql_query(file_path: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(base_dir, '..', 'sql', file_path)
    try:
        with open(sql_file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise RuntimeError(f"Arquivo SQL não encontrado em: {sql_file_path}")


class PoltronaPostgresProvider(PoltronaProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_poltronas(self) -> List[Dict[str, Any]]:
        query_string = get_sql_query("poltrona/listar_todas.sql")
        query = text(query_string)

        result = await self.session.execute(query)
        poltronas = result.mappings().all()
        return [dict(p) for p in poltronas]

    async def obter_poltrona(self, poltrona_id: int) -> Dict[str, Any]:
        poltrona = await self.session.get(Poltrona, poltrona_id)
        if not poltrona:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poltrona não encontrada")
        return {c.name: getattr(poltrona, c.name) for c in poltrona.__table__.columns}