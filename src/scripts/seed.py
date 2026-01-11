import asyncio
import random
import uuid
from datetime import date, timedelta

from faker import Faker
from sqlalchemy import text

from src.models.agendamento import Agendamento
from src.models.aghu import AghuPaciente
from src.models.configuracao import Configuracao
from src.models.equipe import Profissional, EscalaPlantao, AusenciaProfissional
from src.models.paciente import Paciente, ContatoEmergencia
from src.models.prescricao import Prescricao, ItemPrescricao
from src.models.protocolo import Protocolo, ItemProtocolo
from src.resources.database import app_engine, aghu_engine, AppSessionLocal, AghuSessionLocal, Base

fake = Faker('pt_BR')

TAGS_CONFIG = [
    "1ª Vez de Quimio", "Mudança de Protocolo", "Redução de Dose", "Virá à Tarde", "Continuidade", "Aguarda Contínuo",
    "Laboratório Ciente", "Quimio Adiada", "Comunicado ao Paciente", "Virá Após a RDT"
]

CARGOS = ["Enfermeiro", "Técnico de Enfermagem", "Farmacêutico", "Médico", "Administrador"]

FUNCOES = ["Gestão", "Salão QT", "Triagem/Marcação", "Consulta de Enfermagem", "Apoio"]

PROTOCOLOS_DATA = [
    {
        "nome": "PEMETREXEDE + CISPLATINA",
        "duracao": 240, "grupo": "longo", "dias": [1], "freq": 21, "indicacao": "Ca Pulmão",
        "meds": [
            {"nome": "Pemetrexede", "dose": "500", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Cisplatina", "dose": "75", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Dexametasona", "dose": "4", "un": "mg", "tipo": "pre"},
            {"nome": "Ondansetrona", "dose": "8", "un": "mg", "tipo": "pre"},
        ]
    },
    {
        "nome": "VELCADE (BORTEZOMIBE)",
        "duracao": 30, "grupo": "rapido", "dias": [3], "freq": 7, "indicacao": "Mieloma Múltiplo",
        "meds": [
            {"nome": "Bortezomibe", "dose": "1.3", "un": "mg/m²", "tipo": "qt", "via": "SC"},
            {"nome": "Dexametasona", "dose": "20", "un": "mg", "tipo": "pre"},
        ]
    },
    {
        "nome": "RITUXIMABE MONOTERAPIA",
        "duracao": 300, "grupo": "longo", "dias": [5], "freq": 21, "indicacao": "Linfoma não-Hodgkin",
        "meds": [
            {"nome": "Rituximabe", "dose": "375", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Dipirona", "dose": "1", "un": "g", "tipo": "pre"},
            {"nome": "Hidrocortisona", "dose": "100", "un": "mg", "tipo": "pre"},
        ]
    },
    {
        "nome": "FOLFOX 6",
        "duracao": 240, "grupo": "medio", "dias": [1, 2, 3], "freq": 14, "indicacao": "Ca Colorretal",
        "meds": [
            {"nome": "Oxaliplatina", "dose": "85", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Leucovorina", "dose": "400", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Fluorouracil (Bolus)", "dose": "400", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Fluorouracil (Infusão)", "dose": "2400", "un": "mg/m²", "tipo": "qt", "via": "Bomba 46h"},
        ]
    },
    {
        "nome": "AC-T (DOXORRUBICINA + CICLOFOSFAMIDA)",
        "duracao": 120, "grupo": "medio", "dias": [1, 2, 3, 4, 5], "freq": 21, "indicacao": "Ca Mama",
        "meds": [
            {"nome": "Doxorrubicina", "dose": "60", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Ciclofosfamida", "dose": "600", "un": "mg/m²", "tipo": "qt"},
            {"nome": "Ondansetrona", "dose": "16", "un": "mg", "tipo": "pre"},
        ]
    }
]

STATUS_AGENDAMENTO_OPCOES = ['agendado', 'confirmado', 'em-infusao', 'concluido', 'cancelado']
MEDICOS_LISTA = ["Dr. Silva", "Dra. Santos", "Dr. Oliveira", "Dra. Costa", "Dr. Pereira"]


def encontrar_data_valida(data_base: date, dias_permitidos: list[int]) -> date:
    if not dias_permitidos:
        return data_base
    candidata = data_base
    for _ in range(14):
        dia_semana = candidata.weekday() + 1
        if dia_semana in dias_permitidos:
            return candidata
        candidata += timedelta(days=1)
    return data_base


def gerar_horario(turno: str) -> tuple[str, str]:
    if turno == "manha":
        h = random.randint(7, 10)
        m = random.choice(["00", "15", "30", "45"])
        inicio = f"{h:02d}:{m}"
        fim = f"{h + 3:02d}:{m}"
    else:
        h = random.randint(13, 16)
        m = random.choice(["00", "15", "30", "45"])
        inicio = f"{h:02d}:{m}"
        fim = f"{h + 3:02d}:{m}"
    return inicio, fim


async def setup_aghu():
    print("Configurando AGHU...")

    async with aghu_engine.begin() as conn:
        await conn.run_sync(AghuPaciente.__table__.drop, checkfirst=True)
        await conn.run_sync(AghuPaciente.__table__.create)

    pacientes = []
    n = 1000
    print(f"Gerando {n} pacientes...")
    for i in range(n):
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
        print(f"{n} pacientes inseridos.")

    return pacientes


async def setup_app(aghu_pacientes):
    print("Configurando banco de dados principal...")

    async with app_engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS escala_plantao CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS ausencia_profissional CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS profissionais CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS itens_prescricao CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS prescricoes CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS agendamentos CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS contatos_emergencia CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS itens_protocolo CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS pacientes CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS protocolos CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS configuracoes CASCADE"))

        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(text("DROP TABLE IF EXISTS aip_pacientes CASCADE"))

    async with AppSessionLocal() as session:
        print("Criando configurações...")
        conf = Configuracao(
            id=1,
            horario_abertura="07:00",
            horario_fechamento="19:00",
            dias_funcionamento=[1, 2, 3, 4, 5],
            grupos_infusao={
                "rapido": {"vagas": 16, "duracao": "< 2h"},
                "medio": {"vagas": 8, "duracao": "2h - 4h"},
                "longo": {"vagas": 4, "duracao": "> 4h"}
            },
            tags=TAGS_CONFIG,
            cargos= CARGOS,
            funcoes=FUNCOES
        )
        session.add(conf)

        print("Criando profissionais e equipe...")
        profissionais = [
            Profissional(username="usuario_teste", nome="Louro José", cargo="Administrador", ativo=True),
            Profissional(username="enf.ana", nome="Ana Maria", cargo="Enfermeiro", coren="12345-ENF", ativo=True),
            Profissional(username="tec.joao", nome="João Silva", cargo="Técnico de Enfermagem", coren="54321-TEC", ativo=True),
            Profissional(username="med.carlos", nome="Dr. Carlos", cargo="Médico", ativo=True),
        ]
        session.add_all(profissionais)

        hoje = date.today()
        escalas = [
            EscalaPlantao(data=hoje, profissional_id="enf.ana", funcao="Gestão", turno="Integral"),
            EscalaPlantao(data=hoje, profissional_id="tec.joao", funcao="Salão QT", turno="Manhã"),
        ]
        session.add_all(escalas)

        ausencia = AusenciaProfissional(
            profissional_id="enf.ana",
            data_inicio=hoje + timedelta(days=5),
            data_fim=hoje + timedelta(days=20),
            motivo="Férias"
        )
        session.add(ausencia)
        await session.commit()

        print("Criando protocolos...")
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
                    tipo=m['tipo'], nome=m['nome'], dose_padrao=m['dose'],
                    unidade_padrao=m['un'], via_padrao=m.get('via', 'IV')
                )
                p.itens.append(item)
            session.add(p)
            protocolos_objs.append(p)

        await session.commit()

        print("Migrando pacientes e gerando histórico...")
        pacientes_selecionados = random.sample(aghu_pacientes, 100)

        for p_aghu in pacientes_selecionados:
            p_app = Paciente(
                id=str(uuid.uuid4()),
                nome=p_aghu.nome,
                cpf=p_aghu.cpf,
                registro=str(p_aghu.codigo),
                data_nascimento=p_aghu.dt_nascimento,
                telefone=fake.cellphone_number(),
                email=fake.email(),
                peso=round(random.uniform(50.0, 100.0), 1),
                altura=round(random.uniform(150, 190), 0),
                observacoes_clinicas=random.choice(
                    [None, "Hipertenso", "Diabético", "Alergia a Dipirona", "Veias difíceis"])
            )
            p_app.contatos_emergencia.append(
                ContatoEmergencia(nome=fake.name(), telefone=fake.cellphone_number(), parentesco="Familiar")
            )

            protocolo = random.choice(protocolos_objs)
            ciclo_atual = random.randint(1, protocolo.numero_ciclos)
            freq_dias = int(protocolo.frequencia.split()[0])

            dias_corridos = (ciclo_atual - 1) * freq_dias
            offset_aleatorio = random.randint(-5, 5)
            data_inicio_estimada = date.today() - timedelta(days=dias_corridos) + timedelta(days=offset_aleatorio)
            data_inicio_real = encontrar_data_valida(data_inicio_estimada, protocolo.dias_semana_permitidos)

            for c in range(1, protocolo.numero_ciclos + 1):
                delta = (c - 1) * freq_dias
                data_ciclo = encontrar_data_valida(data_inicio_real + timedelta(days=delta),
                                                   protocolo.dias_semana_permitidos)

                if data_ciclo < date.today():
                    status_ag = "concluido"
                    status_presc = "concluida"
                    status_farm = "enviada"
                elif data_ciclo == date.today():
                    status_ag = random.choice(["agendado", "em-infusao"])
                    status_presc = "ativa"
                    status_farm = "pendente" if status_ag == "agendado" else "enviada"
                else:
                    status_ag = "agendado"
                    status_presc = "pendente"
                    status_farm = "pendente"

                presc = Prescricao(
                    id=str(uuid.uuid4()),
                    paciente_id=p_app.id,
                    protocolo_id=protocolo.id,
                    protocolo_nome_snapshot=protocolo.nome,
                    medico_nome=random.choice(MEDICOS_LISTA),
                    data_prescricao=data_ciclo,
                    ciclo_atual=c,
                    ciclos_total=protocolo.numero_ciclos,
                    peso=p_app.peso,
                    altura=p_app.altura,
                    status=status_presc,
                    diagnostico=protocolo.indicacao,
                    observacoes="Sem intercorrências" if status_presc == "concluida" else None
                )

                for item_proto in protocolo.itens:
                    presc.itens.append(ItemPrescricao(
                        tipo=item_proto.tipo, nome=item_proto.nome, dose=item_proto.dose_padrao,
                        unidade=item_proto.unidade_padrao, via=item_proto.via_padrao
                    ))

                turno = random.choice(["manha", "tarde"])
                h_inicio, h_fim = gerar_horario(turno)

                tags_agendamento = []
                if c == 1: tags_agendamento.append("1ª Vez de Quimio")
                if random.random() < 0.2: tags_agendamento.append(random.choice(TAGS_CONFIG))

                ag = Agendamento(
                    id=str(uuid.uuid4()),
                    paciente_id=p_app.id,
                    tipo="infusao",
                    data=data_ciclo,
                    turno=turno, horario_inicio=h_inicio, horario_fim=h_fim,
                    status=status_ag,
                    tags=list(set(tags_agendamento)),
                    observacoes="Agendamento automático via seed.",
                    criado_por_id="usuario_teste",
                    detalhes={
                        "infusao": {
                            "status_farmacia": status_farm,
                            "ciclo_atual": c,
                            "dia_ciclo": "D1"
                        }
                    }
                )

                session.add(presc)
                session.add(ag)

            session.add(p_app)

        await session.commit()
        print("Seed concluído com sucesso!")


async def main():
    aghu_pacientes = await setup_aghu()
    await setup_app(aghu_pacientes)

    await app_engine.dispose()
    await aghu_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
