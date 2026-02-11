import asyncio
import random
from datetime import date, timedelta

from faker import Faker
from sqlalchemy import text, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.aghu_model import AghuPaciente
from src.models.auth_model import User
from src.models.configuracao_model import Configuracao
from src.models.equipe_model import Profissional, EscalaPlantao, AusenciaProfissional
from src.models.protocolo_model import Protocolo
from src.resources.database import app_engine, AppSessionLocal, Base
from src.resources.database_aghu import AghuSessionLocal
from src.schemas.protocolo_schema import ProtocoloCreate
from src.scripts.seed_utils.constants import (
    TAGS_CONFIG, DILUENTES_CONFIG, CARGOS, FUNCOES, VAGAS_CONFIG, DIAS_FUNCIONAMENTO, HORARIO_ABERTURA,
    HORARIO_FECHAMENTO, NUM_PACIENTES_APP, USUARIOS_SEED, MEDICOS_SEED, EQUIPE_SEED, ESCALAS_SEED, AUSENCIAS_SEED
)
from src.scripts.seed_utils.patient_seeder import processar_jornada_paciente
from src.scripts.seed_utils.protocolos_teste import PROTOCOLOS_DATA

fake = Faker('pt_BR')


async def buscar_pacientes_aghu_aleatorios(quantidade: int) -> list[AghuPaciente]:
    print(f"Buscando {quantidade} pacientes aleatórios no AGHU...")
    async with AghuSessionLocal() as session:
        stmt = select(AghuPaciente).order_by(func.random()).limit(quantidade)
        result = await session.execute(stmt)
        pacientes = result.scalars().all()

        if not pacientes:
            raise Exception("Nenhum paciente encontrado no banco AGHU. Execute 'python seed_aghu.py' primeiro.")

        print(f"Encontrados {len(pacientes)} pacientes.")
        return list(pacientes)


async def reset_database(conn):
    tables = [
        "escala_plantao",
        "ausencia_profissional",
        "profissionais",
        "itens_prescricao",
        "prescricoes",
        "agendamentos",
        "contatos_emergencia",
        "itens_protocolo",
        "pacientes",
        "protocolos",
        "configuracoes",
        "refresh_tokens",
        "users"
    ]
    for t in tables:
        await conn.execute(text(f"DROP TABLE IF EXISTS {t} CASCADE"))
    await conn.run_sync(Base.metadata.create_all)


async def criar_usuarios_e_equipe(session: AsyncSession) -> list[User]:
    hoje = date.today()
    user_models = [User(**u) for u in (USUARIOS_SEED + MEDICOS_SEED)]
    session.add_all(user_models)
    session.add_all([Profissional(**p, ativo=True) for p in EQUIPE_SEED])

    for esc in ESCALAS_SEED:
        data_calculada = hoje + timedelta(days=esc.pop("offset"))
        session.add(EscalaPlantao(data=data_calculada, **esc))

    for aus in AUSENCIAS_SEED:
        d_inicio = hoje + timedelta(days=aus.pop("offset_inicio"))
        d_fim = hoje + timedelta(days=aus.pop("offset_fim"))
        session.add(AusenciaProfissional(
            data_inicio=d_inicio,
            data_fim=d_fim,
            **aus
        ))

    await session.commit()
    return [u for u in user_models if u.role == "medico"]


async def criar_protocolos(session: AsyncSession) -> list[Protocolo]:
    objs = []
    for p_data in PROTOCOLOS_DATA:
        protocolo_validado = ProtocoloCreate(**p_data)
        dados_finais = protocolo_validado.model_dump()
        proto = Protocolo(**dados_finais)
        session.add(proto)
        objs.append(proto)
    await session.commit()
    return objs


async def setup_app():
    print("Configurando banco principal...")
    async with app_engine.begin() as conn: await reset_database(conn)

    aghu_pacientes = await buscar_pacientes_aghu_aleatorios(NUM_PACIENTES_APP)
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

        print("Criando usuários e equipe...")
        medicos = await criar_usuarios_e_equipe(session)
        print("Criando protocolos...")
        protocolos = await criar_protocolos(session)
        print("Replicando pacientes e gerando histórico...")
        pacientes_selecionados = random.sample(aghu_pacientes, NUM_PACIENTES_APP)
        for p_aghu in pacientes_selecionados:
            await processar_jornada_paciente(session, p_aghu, protocolos, medicos)

        await session.commit()
        print("Seed concluído com sucesso!")


async def main():
    await setup_app()
    await app_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
