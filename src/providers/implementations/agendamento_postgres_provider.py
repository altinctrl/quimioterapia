import os
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from ..interfaces.agendamento_provider_interface import AgendamentoProviderInterface
from ...schemas.agendamento import AgendamentoCreate, AgendamentoUpdateStatus
from ...models.agendamento import Agendamento


def get_sql_query(file_path: str) -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file_path = os.path.join(base_dir, '..', 'sql', file_path)
    try:
        with open(sql_file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        raise RuntimeError(f"Arquivo SQL não encontrado em: {sql_file_path}")


class AgendamentoPostgresProvider(AgendamentoProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_agendamentos_do_dia(self, data: str) -> List[Dict[str, Any]]:
        query_string = get_sql_query("agendamento/listar_por_data.sql")
        query = text(query_string)

        data_obj = datetime.strptime(data, "%Y-%m-%d").date()

        result = await self.session.execute(query, {"data": data_obj})
        agendamentos = result.mappings().all()
        return [dict(ag) for ag in agendamentos]

    async def criar_agendamento(self, agendamento_schema: AgendamentoCreate) -> Dict[str, Any]:
        novo_agendamento = Agendamento(**agendamento_schema.model_dump())

        self.session.add(novo_agendamento)
        await self.session.commit()
        await self.session.refresh(novo_agendamento)

        return {c.name: getattr(novo_agendamento, c.name) for c in novo_agendamento.__table__.columns}

    async def atualizar_status(self, agendamento_id: int, status_data: AgendamentoUpdateStatus) -> Dict[str, Any]:
        agendamento = await self.session.get(Agendamento, agendamento_id)
        if not agendamento:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agendamento não encontrado")

        agendamento.status = status_data.status
        if status_data.observacoes:
            agendamento.observacoes = status_data.observacoes

        await self.session.commit()
        await self.session.refresh(agendamento)
        return {c.name: getattr(agendamento, c.name) for c in agendamento.__table__.columns}