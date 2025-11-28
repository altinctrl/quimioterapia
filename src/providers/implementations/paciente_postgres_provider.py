from typing import List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from ..interfaces.paciente_provider_interface import PacienteProviderInterface
from ...models.paciente import Paciente


class PacientePostgresProvider(PacienteProviderInterface):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def listar_pacientes(self) -> List[Dict[str, Any]]:
        result = await self.session.execute(select(Paciente).limit(100))
        pacientes = result.scalars().all()

        return [
            {
                "id": str(p.id),
                "nome": p.nome,
                "registro": p.registro,
                "dataNascimento": p.data_nascimento,
                "telefone": p.telefone,
                "protocoloId": str(p.protocolo_id) if p.protocolo_id else None,
                "observacoes": p.observacoes or ""
            }
            for p in pacientes
        ]

    async def obter_paciente_por_codigo(self, codigo: int) -> Dict[str, Any]:
        paciente = await self.session.get(Paciente, codigo)

        if not paciente:
            stmt = select(Paciente).where(Paciente.registro == str(codigo))
            result = await self.session.execute(stmt)
            paciente = result.scalars().first()

            if not paciente:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Paciente não encontrado")

        return {
            "id": str(paciente.id),
            "nome": paciente.nome,
            "registro": paciente.registro,
            "dataNascimento": paciente.data_nascimento,
            "telefone": paciente.telefone,
            "protocoloId": str(paciente.protocolo_id) if paciente.protocolo_id else None,
            "observacoes": paciente.observacoes or ""
        }