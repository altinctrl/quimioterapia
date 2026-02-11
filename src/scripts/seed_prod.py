import asyncio

from src.models.agendamento_model import Agendamento
from src.models.auth_model import User, RefreshToken
from src.models.configuracao_model import Configuracao
from src.models.equipe_model import Profissional, EscalaPlantao, AusenciaProfissional
from src.models.paciente_model import Paciente
from src.models.prescricao_model import Prescricao
from src.models.protocolo_model import Protocolo
from src.resources.database import app_engine, AppSessionLocal, Base
from src.scripts.seed_utils.constants import (
    TAGS_CONFIG, DILUENTES_CONFIG, CARGOS, FUNCOES, VAGAS_CONFIG, DIAS_FUNCIONAMENTO, HORARIO_ABERTURA,
    HORARIO_FECHAMENTO
)

__all__ = [
    "User", "RefreshToken", "Profissional", "EscalaPlantao", "AusenciaProfissional", "Paciente", "Prescricao",
    "Agendamento", "Protocolo", "Configuracao"
]


async def setup_app():
    print("Configurando banco de dados...")
    async with app_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AppSessionLocal() as session:
        print("Criando configurações...")
        session.add(Configuracao(
            id=1,
            horario_abertura=HORARIO_ABERTURA,
            horario_fechamento=HORARIO_FECHAMENTO,
            dias_funcionamento=DIAS_FUNCIONAMENTO,
            vagas=VAGAS_CONFIG,
            tags=TAGS_CONFIG,
            cargos=CARGOS,
            funcoes=FUNCOES,
            diluentes=DILUENTES_CONFIG,
        ))

        await session.commit()
        print("Seed concluído com sucesso!")


async def main():
    await setup_app()
    await app_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
