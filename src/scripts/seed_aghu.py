import asyncio
import random

from faker import Faker
from sqlalchemy import text

from src.models.aghu_model import AghuPaciente
from src.resources.database_aghu import aghu_engine, AghuSessionLocal, AghuBase
from src.scripts.seed_utils.constants import NUM_PACIENTES_AGHU

fake = Faker('pt_BR')


async def setup_aghu():
    print("Configurando AGHU...")

    async with aghu_engine.begin() as conn:
        await conn.execute(text(f"DROP TABLE IF EXISTS aip_pacientes CASCADE"))
        await conn.run_sync(AghuBase.metadata.create_all)

    pacientes = []
    print(f"Gerando {NUM_PACIENTES_AGHU} pacientes simulados...")

    for i in range(NUM_PACIENTES_AGHU):
        sexo = random.choice(['M', 'F'])
        nome = fake.name_male() if sexo == 'M' else fake.name_female()
        p = AghuPaciente(
            codigo=200000 + i,
            nome=nome,
            cpf=fake.cpf(),
            dt_nascimento=fake.date_of_birth(minimum_age=18, maximum_age=90),
            sexo=sexo,
            nome_mae=fake.name_female(),
            nome_pai=fake.name_male()
        )
        pacientes.append(p)

    async with AghuSessionLocal() as session:
        session.add_all(pacientes)
        await session.commit()
        print(f"Sucesso: {len(pacientes)} pacientes inseridos no AGHU.")


async def main():
    await setup_aghu()
    await aghu_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
