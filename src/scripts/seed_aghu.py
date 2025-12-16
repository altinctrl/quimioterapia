import asyncio
import os
import random

from dotenv import load_dotenv
from faker import Faker

from src.models.aghu import AghuPaciente
from src.resources.database import DatabaseManager

load_dotenv()
fake = Faker('pt_BR')


async def seed_aghu():
    aghu_url = os.getenv("AGHU_DB_URL")
    if not aghu_url:
        print("AGHU_DB_URL não configurada.")
        return

    print(f"Gerando 1000 pacientes no banco AGHU ({aghu_url})...")

    db = DatabaseManager(aghu_url)

    async with db.engine.begin() as conn:
        from src.resources.database import Base
        await conn.run_sync(Base.metadata.create_all)

    async for session in db.get_session():
        pacientes = []
        try:
            for i in range(1000):
                cpf = fake.cpf()

                p = AghuPaciente(codigo=100000 + i, nome=fake.name(), cpf=cpf,
                    dt_nascimento=fake.date_of_birth(minimum_age=18, maximum_age=90), sexo=random.choice(['M', 'F']),
                    nome_mae=fake.name_female(), nome_pai=fake.name_male())
                pacientes.append(p)

            session.add_all(pacientes)
            await session.commit()
            print("1000 Pacientes mock inseridos com sucesso!")

        except Exception as e:
            print(f"Erro ao inserir: {e}")
            await session.rollback()
        finally:
            await db.close_connection()


if __name__ == "__main__":
    asyncio.run(seed_aghu())
