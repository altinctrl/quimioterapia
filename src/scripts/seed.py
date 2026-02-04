import asyncio
import random
import uuid
from datetime import date, timedelta, datetime
from typing import Optional

from faker import Faker
from sqlalchemy import text

from src.models.agendamento import Agendamento
from src.models.aghu import AghuPaciente
from src.models.auth_model import RefreshToken
from src.models.configuracao import Configuracao
from src.models.equipe import Profissional, EscalaPlantao, AusenciaProfissional
from src.models.paciente import Paciente, ContatoEmergencia
from src.models.prescricao import Prescricao
from src.models.protocolo import Protocolo
from src.resources.database import app_engine, aghu_engine, AppSessionLocal, AghuSessionLocal, Base
from src.schemas.agendamento import AgendamentoCreate, DetalhesAgendamento, TipoAgendamento, AgendamentoStatusEnum, \
    FarmaciaStatusEnum, TipoConsulta, TipoProcedimento
from src.schemas.equipe import MotivoAusenciaEnum
from src.schemas.prescricao import ProtocoloRef, PacienteSnapshot, BlocoPrescricao, ItemPrescricao, \
    PrescricaoStatusEnum, MedicoSnapshot
from src.schemas.protocolo import ProtocoloCreate, TemplateCiclo, UnidadeDoseEnum
from src.scripts.const_protocolos_teste import PROTOCOLOS_DATA

fake = Faker('pt_BR')

TAGS_CONFIG = [
    "1ª Vez de Quimio", "Mudança de Protocolo", "Redução de Dose", "Virá à Tarde", "Continuidade", "Aguarda Contínuo",
    "Laboratório Ciente", "Quimio Adiada", "Comunicado ao Paciente", "Virá Após a RDT"
]

DILUENTES_CONFIG = [
    "Soro Fisiológico 0,9% 50ml",
    "Soro Fisiológico 0,9% 100ml",
    "Soro Fisiológico 0,9% 250ml",
    "Soro Fisiológico 0,9% 500ml",
    "Soro Fisiológico 0,9% 1000ml",
    "Glicose 5% 50ml",
    "Glicose 5% 100ml",
    "Glicose 5% 250ml",
    "Glicose 5% 500ml",
    "Glicose 5% 1000ml",
    "Água para Injeção 10ml",
    "Sem Diluente (Bolus)"
]

CARGOS = ["Enfermeiro", "Técnico de Enfermagem", "Farmacêutico", "Médico", "Administrador"]
FUNCOES = ["Gestão", "Salão QT", "Triagem/Marcação", "Consulta de Enfermagem", "Apoio"]
MEDICOS_USERNAMES = ["med.carlos", "med.fernanda", "med.roberto"]


def calcular_bsa(peso, altura_cm):
    if not peso or not altura_cm: return 1.7
    altura_m = altura_cm / 100
    return 0.007184 * (peso ** 0.425) * (altura_m ** 0.725)


def encontrar_data_valida(data_base: date, dias_permitidos: list[int] = None) -> date:
    candidata = data_base
    permitidos = dias_permitidos if dias_permitidos else [1, 2, 3, 4, 5]

    for _ in range(31):
        if candidata.weekday() in permitidos:
            return candidata
        candidata += timedelta(days=1)

    return candidata


def gerar_horario(turno: str, duracao_minutos: int) -> tuple[str, str]:
    h_inicio = random.randint(8, 12) if turno == "manha" else random.randint(13, 17)
    m_inicio = random.choice([0, 15, 30, 45])
    dt_inicio = datetime.combine(date.today(), datetime.min.time()).replace(hour=h_inicio, minute=m_inicio)
    dt_fim = dt_inicio + timedelta(minutes=duracao_minutos)

    return dt_inicio.strftime("%H:%M"), dt_fim.strftime("%H:%M")


def criar_prescricao_payload(protocolo_model: Protocolo, paciente: Paciente, medico_obj: Profissional, ciclo: int):
    bsa = calcular_bsa(paciente.peso, paciente.altura)
    templates = [TemplateCiclo(**t) for t in protocolo_model.templates_ciclo]
    template = templates[0]

    blocos_prescricao = []

    for bloco in template.blocos:
        itens_presc = []
        for item_bloco in bloco.itens:
            if item_bloco.tipo == 'medicamento_unico':
                dados = item_bloco.dados

                dose_calc = dados.dose_referencia
                if dados.unidade == UnidadeDoseEnum.MG_M2:
                    dose_calc = dados.dose_referencia * bsa
                elif dados.unidade == UnidadeDoseEnum.MG_KG:
                    dose_calc = dados.dose_referencia * paciente.peso

                diluicao_padrao = ""
                if hasattr(dados, 'configuracao_diluicao') and dados.configuracao_diluicao:
                    config = dados.configuracao_diluicao
                    diluicao_padrao = getattr(config, 'selecionada', "") or ""
                    if not diluicao_padrao and hasattr(config, 'opcoes_permitidas') and config.opcoes_permitidas:
                        diluicao_padrao = config.opcoes_permitidas[0]

                item_p = ItemPrescricao(
                    id_item=str(uuid.uuid4()),
                    medicamento=dados.medicamento,
                    dose_referencia=str(dados.dose_referencia),
                    unidade=dados.unidade,
                    dose_teorica=round(dose_calc, 2),
                    percentual_ajuste=100.0,
                    dose_final=round(dose_calc, 2),
                    via=dados.via,
                    tempo_minutos=dados.tempo_minutos,
                    diluicao_final=diluicao_padrao,
                    dias_do_ciclo=dados.dias_do_ciclo,
                    notas_especificas=dados.notas_especificas
                )
                itens_presc.append(item_p)

        if itens_presc:
            bloco_p = BlocoPrescricao(
                ordem=bloco.ordem,
                categoria=bloco.categoria,
                itens=itens_presc
            )
            blocos_prescricao.append(bloco_p)

    paciente_snapshot = PacienteSnapshot(
        nome=paciente.nome,
        prontuario=paciente.registro,
        nascimento=paciente.data_nascimento,
        sexo=paciente.sexo,
        peso=paciente.peso,
        altura=paciente.altura,
        sc=round(bsa, 2)
    )

    medico_snapshot = MedicoSnapshot(
        nome=medico_obj.nome,
        crm_uf=medico_obj.registro if medico_obj.registro else "CRM-UF 00000"
    )

    protocolo_ref = ProtocoloRef(
        nome=protocolo_model.nome,
        ciclo_atual=ciclo
    )

    documento_json = {
        "data_emissao": datetime.now().isoformat(),
        "paciente": paciente_snapshot.model_dump(mode='json'),
        "medico": medico_snapshot.model_dump(mode='json'),
        "protocolo": protocolo_ref.model_dump(mode='json'),
        "blocos": [b.model_dump(mode='json') for b in blocos_prescricao],
        "diagnostico": "Gerado via seed com validação Pydantic."
    }

    return documento_json


def criar_historico_status_inicial(status_atual: str):
    return [{
        "data": datetime.now().isoformat(),
        "usuario_id": "seed",
        "usuario_nome": "Seed",
        "status_anterior": status_atual,
        "status_novo": status_atual,
        "motivo": "Seed inicial"
    }]


def criar_historico_agendamento(presc_id: str, status_agendamento):
    status_val = status_agendamento.value if hasattr(status_agendamento, 'value') else str(status_agendamento)
    return {
        "data": datetime.now().isoformat(),
        "agendamento_id": presc_id,
        "status_agendamento": status_val,
        "usuario_id": "seed",
        "usuario_nome": "Seed",
        "observacoes": "Agendamento criado via seed"
    }


def criar_historico_alteracao_agendamento(tipo: str, campo: str, valor_antigo: Optional[str], valor_novo: Optional[str]):
    return {
        "data": datetime.now().isoformat(),
        "usuario_id": "seed",
        "usuario_nome": "Seed",
        "tipo_alteracao": tipo,
        "campo": campo,
        "valor_antigo": valor_antigo,
        "valor_novo": valor_novo,
        "motivo": "Seed inicial"
    }


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
        await conn.execute(text("DROP TABLE IF EXISTS refresh_tokens CASCADE"))

        await conn.run_sync(Base.metadata.create_all)

        await conn.execute(text("DROP TABLE IF EXISTS aip_pacientes CASCADE"))

    async with AppSessionLocal() as session:
        print("Criando configurações...")
        conf = Configuracao(
            id=1,
            horario_abertura="07:00",
            horario_fechamento="19:00",
            dias_funcionamento=[1, 2, 3, 4, 5],
            vagas={
                "infusao_rapido": 16,
                "infusao_medio": 8,
                "infusao_longo": 4,
                "infusao_extra_longo": 4,
                "consultas": 10,
                "procedimentos": 10
            },
            tags=TAGS_CONFIG,
            cargos=CARGOS,
            funcoes=FUNCOES,
            diluentes=DILUENTES_CONFIG,
        )
        session.add(conf)

        print("Criando profissionais e equipe...")
        profissionais = [
            Profissional(username="admin", nome="Louro José", cargo="Administrador", ativo=True),
            Profissional(username="enf.ana", nome="Ana Maria", cargo="Enfermeiro", registro="123456-ENF/UF",
                         ativo=True),
            Profissional(username="tec.joao", nome="João Silva", cargo="Técnico de Enfermagem", registro="987654-TE/UF",
                         ativo=True),
        ]
        medicos_objs = []
        for m in MEDICOS_USERNAMES:
            p = Profissional(
                username=m,
                nome=f"Dr(a). {m.split('.')[1].title()}",
                cargo="Médico",
                registro=f"CRM-UF {random.randint(10000, 99999)}",
                ativo=True)
            profissionais.append(p)
            medicos_objs.append(p)

        session.add_all(profissionais)
        await session.commit()

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
            motivo=MotivoAusenciaEnum.LTS
        )
        session.add(ausencia)
        await session.commit()

        print("Criando protocolos...")
        protocolos_objs = []
        for p_data in PROTOCOLOS_DATA:
            try:
                proto_validator = ProtocoloCreate(**p_data)
            except Exception as e:
                print(f"ERRO DE VALIDAÇÃO NO PROTOCOLO {p_data['nome']}: {e}")
                raise e

            protocolo = Protocolo(
                id=str(uuid.uuid4()),
                nome=proto_validator.nome,
                indicacao=proto_validator.indicacao,
                fase=proto_validator.fase,
                linha=proto_validator.linha,
                total_ciclos=proto_validator.total_ciclos,
                duracao_ciclo_dias=proto_validator.duracao_ciclo_dias,
                tempo_total_minutos=proto_validator.tempo_total_minutos,
                dias_semana_permitidos=proto_validator.dias_semana_permitidos,
                ativo=proto_validator.ativo,
                observacoes=proto_validator.observacoes,
                precaucoes=proto_validator.precaucoes,
                templates_ciclo=proto_validator.model_dump(include={'templates_ciclo'}, mode='json')['templates_ciclo']
            )
            session.add(protocolo)
            protocolos_objs.append(protocolo)
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
                sexo=p_aghu.sexo,
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
            session.add(p_app)

            protocolo = random.choice(protocolos_objs)
            medico = random.choice(medicos_objs)
            ciclo_atual = random.randint(1, protocolo.total_ciclos)
            dias_por_ciclo = protocolo.duracao_ciclo_dias

            dias_corridos = (ciclo_atual - 1) * dias_por_ciclo
            offset_aleatorio = random.randint(-5, 5)
            data_inicio_estimada = date.today() - timedelta(days=dias_corridos) + timedelta(days=offset_aleatorio)
            data_inicio_tratamento = encontrar_data_valida(data_inicio_estimada, protocolo.dias_semana_permitidos)

            for c in range(1, protocolo.total_ciclos + 1):
                delta_dias_ciclo = (c - 1) * dias_por_ciclo
                data_ciclo = encontrar_data_valida(
                    data_inicio_tratamento + timedelta(days=delta_dias_ciclo), protocolo.dias_semana_permitidos)

                data_fim_ciclo = data_ciclo + timedelta(days=protocolo.duracao_ciclo_dias)
                if data_fim_ciclo < date.today():
                    status_presc = PrescricaoStatusEnum.CONCLUIDA
                elif data_ciclo <= date.today() <= data_fim_ciclo:
                    status_presc = PrescricaoStatusEnum.EM_CURSO
                else:
                    status_presc = PrescricaoStatusEnum.PENDENTE

                conteudo_json = criar_prescricao_payload(protocolo, p_app, medico, c)
                hora_emissao = datetime.now() - timedelta(
                    days=random.randint(0, 2),
                    hours=random.randint(0, 5),
                    minutes=random.randint(0, 59)
                )
                presc = Prescricao(
                    id=str(uuid.uuid4()),
                    paciente_id=p_app.id,
                    medico_id=medico.username,
                    data_emissao=datetime.combine(
                        data_ciclo,
                        datetime.min.time()) if status_presc == PrescricaoStatusEnum.PENDENTE else hora_emissao,
                    status=status_presc,
                    conteudo=conteudo_json,
                    historico_status=criar_historico_status_inicial(status_presc.value if hasattr(status_presc, 'value') else str(status_presc)),
                    historico_agendamentos=[]
                )
                session.add(presc)

                dias_infusao = set()
                for bloco in conteudo_json['blocos']:
                    for item in bloco['itens']:
                        for d in item['dias_do_ciclo']:
                            dias_infusao.add(d)

                for dia_num in sorted(dias_infusao):
                    data_ag = encontrar_data_valida(data_ciclo + timedelta(days=dia_num - 1),
                                                    protocolo.dias_semana_permitidos)

                    status_ag = AgendamentoStatusEnum.AGENDADO
                    checkin = False
                    status_farm = FarmaciaStatusEnum.AGENDADO

                    if data_ag < date.today():
                        status_ag = AgendamentoStatusEnum.CONCLUIDO
                        checkin = True
                        status_farm = FarmaciaStatusEnum.ENVIADO
                    elif data_ag == date.today():
                        status_ag = random.choice([
                            AgendamentoStatusEnum.AGENDADO,
                            AgendamentoStatusEnum.EM_INFUSAO,
                            AgendamentoStatusEnum.CONCLUIDO,
                        ])
                        checkin = True if status_ag != AgendamentoStatusEnum.AGENDADO else False
                        status_farm = FarmaciaStatusEnum.AGENDADO if checkin else FarmaciaStatusEnum.ENVIADO

                    inicio, fim = gerar_horario(random.choice(["manha", "tarde"]), protocolo.tempo_total_minutos)

                    tags = []
                    if c == 1 and dia_num == 1:
                        tags.append("1ª Vez de Quimio")
                    if random.random() < 0.1:
                        tags.append(random.choice(TAGS_CONFIG))

                    detalhes_input = {
                        "infusao": {
                            "prescricao_id": presc.id,
                            "status_farmacia": status_farm,
                            "ciclo_atual": c,
                            "dia_ciclo": dia_num
                        }
                    }

                    ag_validator = AgendamentoCreate(
                        paciente_id=p_app.id,
                        tipo=TipoAgendamento.INFUSAO,
                        data=data_ag,
                        turno="manha",
                        horario_inicio=inicio,
                        horario_fim=fim,
                        checkin=checkin,
                        status=status_ag,
                        tags=list(set(tags)),
                        observacoes=f"Ciclo {c} Dia {dia_num} - Seed",
                        detalhes=DetalhesAgendamento(**detalhes_input)
                    )

                    historico_alteracoes = [
                        criar_historico_alteracao_agendamento(
                            "status",
                            "status",
                            None,
                            status_ag.value if hasattr(status_ag, 'value') else str(status_ag)
                        )
                    ]

                    detalhes_json = ag_validator.detalhes.model_dump(mode='json', exclude_none=True)
                    detalhes_json["historico_prescricoes"] = [{
                        "data": datetime.now().isoformat(),
                        "usuario_id": "seed",
                        "usuario_nome": "Seed",
                        "prescricao_id_anterior": None,
                        "prescricao_id_nova": presc.id,
                        "motivo": "Agendamento criado via seed"
                    }]

                    ag = Agendamento(
                        id=str(uuid.uuid4()),
                        criado_por_id="admin",
                        paciente_id=ag_validator.paciente_id,
                        tipo=ag_validator.tipo,
                        data=ag_validator.data,
                        turno=ag_validator.turno,
                        horario_inicio=ag_validator.horario_inicio,
                        horario_fim=ag_validator.horario_fim,
                        checkin=ag_validator.checkin,
                        status=ag_validator.status,
                        tags=ag_validator.tags,
                        observacoes=ag_validator.observacoes,
                        detalhes=detalhes_json,
                        historico_alteracoes=historico_alteracoes
                    )
                    session.add(ag)

                    presc.historico_agendamentos.append(criar_historico_agendamento(ag.id, ag.status))

            for _ in range(10):
                tipo_cons = random.choice(list(TipoConsulta))
                data_cons = encontrar_data_valida(date.today() + timedelta(days=random.randint(-30, 30)))
                inicio, fim = gerar_horario(random.choice(["manha", "tarde"]), 30)

                ag_cons = Agendamento(
                    id=str(uuid.uuid4()),
                    criado_por_id="admin",
                    paciente_id=p_app.id,
                    tipo=TipoAgendamento.CONSULTA,
                    data=data_cons,
                    turno="manha",
                    horario_inicio=inicio,
                    horario_fim=fim,
                    checkin=True if data_cons < date.today() else False,
                    status=AgendamentoStatusEnum.CONCLUIDO if data_cons < date.today() else AgendamentoStatusEnum.AGENDADO,
                    detalhes={"consulta": {"tipo_consulta": tipo_cons.value}},
                    historico_alteracoes=[
                        criar_historico_alteracao_agendamento(
                            "status",
                            "status",
                            None,
                            (AgendamentoStatusEnum.CONCLUIDO if data_cons < date.today() else AgendamentoStatusEnum.AGENDADO).value
                        )
                    ]
                )
                session.add(ag_cons)

            for _ in range(10):
                tipo_proc = random.choice(list(TipoProcedimento))
                data_proc = encontrar_data_valida(date.today() + timedelta(days=random.randint(-30, 30)))
                inicio, fim = gerar_horario(random.choice(["manha", "tarde"]), 60)

                ag_proc = Agendamento(
                    id=str(uuid.uuid4()),
                    criado_por_id="admin",
                    paciente_id=p_app.id,
                    tipo=TipoAgendamento.PROCEDIMENTO,
                    data=data_proc,
                    turno="manha",
                    horario_inicio=inicio,
                    horario_fim=fim,
                    checkin=True if data_proc < date.today() else False,
                    status=AgendamentoStatusEnum.CONCLUIDO if data_proc < date.today() else AgendamentoStatusEnum.AGENDADO,
                    detalhes={"procedimento": {"tipo_procedimento": tipo_proc.value}},
                    historico_alteracoes=[
                        criar_historico_alteracao_agendamento(
                            "status",
                            "status",
                            None,
                            (AgendamentoStatusEnum.CONCLUIDO if data_proc < date.today() else AgendamentoStatusEnum.AGENDADO).value
                        )
                    ]
                )
                session.add(ag_proc)

        await session.commit()
        print("Seed concluído com sucesso!")


async def main():
    aghu_pacientes = await setup_aghu()
    await setup_app(aghu_pacientes)

    await app_engine.dispose()
    await aghu_engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
