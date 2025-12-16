import asyncio
import os
import random
import uuid
from datetime import date, timedelta
from typing import List

from dotenv import load_dotenv
from faker import Faker
from sqlalchemy import select, delete

# Importe o DatabaseManager existente no seu projeto
from src.resources.database import DatabaseManager

# Modelos
from src.models.aghu import AghuPaciente
from src.models.paciente import Paciente, ContatoEmergencia
from src.models.protocolo import Protocolo, ItemProtocolo
from src.models.agendamento import Agendamento
from src.models.prescricao import Prescricao, ItemPrescricao
from src.models.configuracao import Configuracao

# Tente importar Usuario/Auth, se não existir, ignora
try:
    from src.models.usuario import Usuario
    from src.auth.auth import auth_handler

    HAS_AUTH = True
except ImportError:
    HAS_AUTH = False

load_dotenv()
fake = Faker('pt_BR')

# --- DADOS DOS PROTOCOLOS (Baseado nas Regras de Agendamento) ---
PROTOCOLOS_DATA = [
    {
        "nome": "PEMETREXEDE + CISPLATINA",
        "duracao": 240,
        "grupo": "longo",
        "dias": [1],  # Segunda-feira
        "freq": 21,
        "indicacao": "Ca Pulmão",
        "meds": [
            {"nome": "Pemetrexede", "dose": "500", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Cisplatina", "dose": "75", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Dexametasona", "dose": "4", "un": "mg", "tipo": "pre"},
            {"nome": "Ondansetrona", "dose": "8", "un": "mg", "tipo": "pre"},
        ]
    },
    {
        "nome": "VELCADE (BORTEZOMIBE)",
        "duracao": 30,
        "grupo": "rapido",
        "dias": [3],  # Quarta-feira
        "freq": 7,
        "indicacao": "Mieloma Múltiplo",
        "meds": [
            {"nome": "Bortezomibe", "dose": "1.3", "un": "mg/m²", "tipo": "qt", "via": "SC"},
            {"nome": "Dexametasona", "dose": "20", "un": "mg", "tipo": "pre"},
        ]
    },
    {
        "nome": "RITUXIMABE MONOTERAPIA",
        "duracao": 300,
        "grupo": "longo",
        "dias": [5],  # Sexta-feira
        "freq": 21,
        "indicacao": "Linfoma não-Hodgkin",
        "meds": [
            {"nome": "Rituximabe", "dose": "375", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Dipirona", "dose": "1", "un": "g", "tipo": "pre"},
            {"nome": "Hidrocortisona", "dose": "100", "un": "mg", "tipo": "pre"},
        ]
    },
    {
        "nome": "FLOT",
        "duracao": 360,
        "grupo": "longo",
        "dias": [4],  # Quinta-feira
        "freq": 14,
        "indicacao": "Ca Gástrico",
        "meds": [
            {"nome": "Docetaxel", "dose": "50", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Oxaliplatina", "dose": "85", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Leucovorina", "dose": "200", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Fluorouracil", "dose": "2600", "un": "mg/m²", "tipo": "qt", "via": "Bomba Infusora"},
        ]
    },
    {
        "nome": "ABVD",
        "duracao": 180,
        "grupo": "medio",
        "dias": [1, 2, 4, 5],  # Seg, Ter, Qui, Sex (Evita Quarta)
        "freq": 14,
        "indicacao": "Linfoma de Hodgkin",
        "meds": [
            {"nome": "Doxorrubicina", "dose": "25", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Bleomicina", "dose": "10", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Vinblastina", "dose": "6", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Dacarbazina", "dose": "375", "un": "mg/m²", "tipo": "qt"},
        ]
    },
    {
        "nome": "AC-T (DOXORRUBICINA + CICLOFOSFAMIDA)",
        "duracao": 120,
        "grupo": "medio",
        "dias": [1, 2, 3, 4, 5],  # Todos
        "freq": 21,
        "indicacao": "Ca Mama",
        "meds": [
            {"nome": "Doxorrubicina", "dose": "60", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Ciclofosfamida", "dose": "600", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Ondansetrona", "dose": "16", "un": "mg", "tipo": "pre"},
            {"nome": "Dexametasona", "dose": "10", "un": "mg", "tipo": "pre"},
        ]
    },
    {
        "nome": "FOLFOX 6",
        "duracao": 240,
        "grupo": "medio",
        "dias": [1, 2, 3],  # Seg, Ter, Qua
        "freq": 14,
        "indicacao": "Ca Colorretal",
        "meds": [
            {"nome": "Oxaliplatina", "dose": "85", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Leucovorina", "dose": "400", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Fluorouracil (Bolus)", "dose": "400", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Fluorouracil (Infusão)", "dose": "2400", "un": "mg/m²", "tipo": "qt", "via": "Bomba 46h"},
        ]
    }
]


# --- HELPERS ---
def encontrar_data_valida(data_base: date, dias_permitidos: List[int]) -> date:
    """
    Encontra a data válida mais próxima (futuro ou presente) que caia num dia permitido.
    dias_permitidos: [1=Seg, ..., 5=Sex]
    python weekday: 0=Seg, ..., 6=Dom
    """
    if not dias_permitidos:
        return data_base

    candidata = data_base
    for _ in range(14):
        # Converte Python (0-6) para o nosso padrão (1-7, onde 1=Segunda)
        dia_semana = candidata.weekday() + 1
        if dia_semana in dias_permitidos:
            return candidata
        candidata += timedelta(days=1)

    return data_base


# --- FUNÇÕES DE SEED ---

async def seed_aghu(db: DatabaseManager):
    print("🏥 [AGHU] Iniciando povoamento do banco legado...")

    # Recria tabelas no banco AGHU (opcional, para garantir limpeza)
    try:
        from src.resources.database import Base
        async with db.engine.begin() as conn:
            # Atenção: Isso recria TODAS as tabelas definidas no Base no banco do AGHU
            # Idealmente o AGHU teria seu próprio Base, mas para seed funciona se AghuPaciente estiver lá.
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Aviso ao criar tabelas AGHU: {e}")

    async for session in db.get_session():
        # Limpar tabela
        await session.execute(delete(AghuPaciente))

        pacientes = []
        print("🏥 [AGHU] Gerando 1000 pacientes...")
        for i in range(1000):
            sexo = random.choice(['M', 'F'])
            nome = fake.name_male() if sexo == 'M' else fake.name_female()

            p = AghuPaciente(
                codigo=100000 + i,
                nome=nome,
                cpf=fake.cpf(),
                dt_nascimento=fake.date_of_birth(minimum_age=18, maximum_age=90),
                sexo=sexo,
                nome_mae=fake.name_female(),
                nome_pai=fake.name_male()
            )
            pacientes.append(p)

        session.add_all(pacientes)
        await session.commit()
        print(f"✅ [AGHU] 1000 Pacientes inseridos.")
        return pacientes  # Retorna para usar na migração


async def seed_clinica(db: DatabaseManager, aghu_pacientes: List[AghuPaciente]):
    print("🏥 [CLÍNICA] Iniciando seed do sistema principal...")

    # Cria tabelas
    try:
        from src.resources.database import Base
        async with db.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Aviso ao criar tabelas APP: {e}")

    async for session in db.get_session():
        # 1. Limpeza (Ordem importa por FKs)
        print("🧹 [CLÍNICA] Limpando dados antigos...")
        await session.execute(delete(ItemPrescricao))
        await session.execute(delete(Prescricao))
        await session.execute(delete(Agendamento))
        await session.execute(delete(ContatoEmergencia))
        await session.execute(delete(ItemProtocolo))
        await session.execute(delete(Paciente))
        await session.execute(delete(Protocolo))
        await session.execute(delete(Configuracao))
        if HAS_AUTH:
            await session.execute(delete(Usuario))
        await session.commit()

        # 2. Configurações
        print("⚙️ [CLÍNICA] Criando configurações...")
        conf = Configuracao(
            horario_abertura="07:00",
            horario_fechamento="19:00",
            dias_funcionamento=[1, 2, 3, 4, 5],
            grupos_infusao={
                "rapido": {"vagas": 6, "duracao": "< 2h"},
                "medio": {"vagas": 8, "duracao": "2h - 4h"},
                "longo": {"vagas": 4, "duracao": "> 4h"}
            }
        )
        session.add(conf)

        # 3. Usuários
        if HAS_AUTH:
            print("👥 [CLÍNICA] Criando usuários...")
            users = [
                Usuario(nome="Admin", email="admin@clinica.com", senha_hash=auth_handler.get_password_hash("123"),
                        role="admin", ativo=True),
                Usuario(nome="Médico", email="medico@clinica.com", senha_hash=auth_handler.get_password_hash("123"),
                        role="medico", ativo=True),
                Usuario(nome="Farmácia", email="farmacia@clinica.com", senha_hash=auth_handler.get_password_hash("123"),
                        role="farmacia", ativo=True),
                Usuario(nome="Recepção", email="recepcao@clinica.com", senha_hash=auth_handler.get_password_hash("123"),
                        role="recepcao", ativo=True),
                Usuario(nome="Enfermagem", email="enf@clinica.com", senha_hash=auth_handler.get_password_hash("123"),
                        role="enfermagem", ativo=True),
            ]
            session.add_all(users)

        # 4. Protocolos
        print("📜 [CLÍNICA] Criando protocolos...")
        protocolos_objs = []
        for p_data in PROTOCOLOS_DATA:
            p = Protocolo(
                id=str(uuid.uuid4()),
                nome=p_data['nome'],
                duracao=p_data['duracao'],
                grupo_infusao=p_data['grupo'],
                indicacao=p_data['indicacao'],
                frequencia=f"{p_data['freq']} dias",
                numero_ciclos=random.choice([4, 6, 8, 12]),
                dias_semana_permitidos=p_data['dias'],
                ativo=True,
                descricao=f"Protocolo padrão para {p_data['indicacao']}"
            )

            for m in p_data['meds']:
                item = ItemProtocolo(
                    tipo=m['tipo'],
                    nome=m['nome'],
                    dose_padrao=m['dose'],
                    unidade_padrao=m['un'],
                    via_padrao=m.get('via', 'IV')
                )
                p.itens.append(item)

            session.add(p)
            protocolos_objs.append(p)

        await session.commit()  # Commita para gerar IDs dos protocolos e usar abaixo

        # 5. Migração e Histórico
        print("🚀 [CLÍNICA] Migrando 20 pacientes e gerando histórico...")

        # Seleciona 20 do lote do AGHU
        selecionados = random.sample(aghu_pacientes, 20)
        medicos = ["Dr. Silva", "Dra. Santos", "Dr. Oliveira"]

        for p_aghu in selecionados:
            # Cria Paciente
            p_clinica = Paciente(
                id=str(uuid.uuid4()),
                nome=p_aghu.nome,
                cpf=p_aghu.cpf,
                registro=str(p_aghu.codigo),
                data_nascimento=p_aghu.dt_nascimento,
                telefone=fake.cellphone_number(),
                email=fake.email(),
                peso=round(random.uniform(50.0, 90.0), 1),
                altura=round(random.uniform(150, 190), 0),
                observacoes_clinicas=random.choice([None, "Hipertenso", "Diabético", "Alergia a Dipirona"]),
            )

            p_clinica.contatos_emergencia.append(
                ContatoEmergencia(nome=fake.name(), telefone=fake.cellphone_number(), parentesco="Familiar")
            )

            # Escolhe Protocolo e Estágio
            protocolo = random.choice(protocolos_objs)
            ciclo_atual = random.randint(2, protocolo.numero_ciclos)  # Ex: está no ciclo 3
            freq_dias = int(protocolo.frequencia.split()[0])

            # -- GERA O PASSADO --
            # Calcula data de início para que o ciclo atual seja "hoje" ou "breve"
            dias_corridos = (ciclo_atual - 1) * freq_dias
            data_inicio_estimada = date.today() - timedelta(days=dias_corridos)
            data_inicio_real = encontrar_data_valida(data_inicio_estimada, protocolo.dias_semana_permitidos)

            for c in range(1, ciclo_atual):  # Ciclos 1 até (atual-1) são CONCLUÍDOS
                delta = (c - 1) * freq_dias
                data_ciclo = encontrar_data_valida(data_inicio_real + timedelta(days=delta),
                                                   protocolo.dias_semana_permitidos)

                # Prescrição Passada
                presc = Prescricao(
                    id=str(uuid.uuid4()),
                    paciente_id=p_clinica.id,
                    protocolo_id=protocolo.id,
                    protocolo_nome_snapshot=protocolo.nome,
                    medico_nome=random.choice(medicos),
                    data_prescricao=data_ciclo,
                    ciclo_atual=c,
                    ciclos_total=protocolo.numero_ciclos,
                    peso=p_clinica.peso,
                    altura=p_clinica.altura,
                    status="concluida",
                    diagnostico=protocolo.indicacao
                )

                for item_proto in protocolo.itens:
                    presc.itens.append(ItemPrescricao(
                        tipo=item_proto.tipo, nome=item_proto.nome, dose=item_proto.dose_padrao,
                        unidade=item_proto.unidade_padrao, via=item_proto.via_padrao
                    ))

                # Agendamento Passado
                ag = Agendamento(
                    id=str(uuid.uuid4()),
                    paciente_id=p_clinica.id,
                    data=data_ciclo,
                    turno="manha", horario_inicio="08:00", horario_fim="12:00",
                    status="concluido", status_farmacia="liberado",
                    ciclo_atual=c, dia_ciclo="D1",
                    observacoes="Paciente tolerou bem."
                )

                session.add(presc)
                session.add(ag)

            # -- GERA O ATUAL (FUTURO/AGENDADO) --
            delta_atual = (ciclo_atual - 1) * freq_dias
            data_atual_base = data_inicio_real + timedelta(days=delta_atual)
            if data_atual_base < date.today(): data_atual_base = date.today()

            data_atual = encontrar_data_valida(data_atual_base, protocolo.dias_semana_permitidos)

            # Prescrição Atual (Ativa/Pendente)
            presc_atual = Prescricao(
                id=str(uuid.uuid4()),
                paciente_id=p_clinica.id,
                protocolo_id=protocolo.id,
                protocolo_nome_snapshot=protocolo.nome,
                medico_nome=random.choice(medicos),
                data_prescricao=data_atual,  # Data prevista
                ciclo_atual=ciclo_atual,
                ciclos_total=protocolo.numero_ciclos,
                peso=p_clinica.peso,
                altura=p_clinica.altura,
                status="ativa",  # Pronta para uso
                diagnostico=protocolo.indicacao
            )
            # Itens da prescrição atual
            for item_proto in protocolo.itens:
                presc_atual.itens.append(ItemPrescricao(
                    tipo=item_proto.tipo, nome=item_proto.nome, dose=item_proto.dose_padrao,
                    unidade=item_proto.unidade_padrao, via=item_proto.via_padrao
                ))

            ag_atual = Agendamento(
                id=str(uuid.uuid4()),
                paciente_id=p_clinica.id,
                data=data_atual,
                turno="manha", horario_inicio="08:00", horario_fim="12:00",
                status="agendado", status_farmacia="pendente",
                ciclo_atual=ciclo_atual, dia_ciclo="D1"
            )

            session.add(p_clinica)
            session.add(presc_atual)
            session.add(ag_atual)

        await session.commit()
        print("✅ [CLÍNICA] Seed concluído!")


async def main():
    aghu_url = os.getenv("AGHU_DB_URL")
    app_url = os.getenv("APP_DB_URL") or os.getenv("POSTGRES_DSN")

    if not aghu_url or not app_url:
        print("❌ Erro: Variáveis de ambiente AGHU_DB_URL ou APP_DB_URL não encontradas.")
        print("Verifique seu arquivo .env")
        return

    # 1. Conecta e popula AGHU
    db_aghu = DatabaseManager(aghu_url)
    pacientes_aghu = await seed_aghu(db_aghu)

    # 2. Conecta e popula CLÍNICA usando os dados do AGHU
    db_app = DatabaseManager(app_url)
    await seed_clinica(db_app, pacientes_aghu)


if __name__ == "__main__":
    asyncio.run(main())