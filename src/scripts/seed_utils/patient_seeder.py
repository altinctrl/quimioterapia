import random
import uuid
from datetime import date, timedelta, datetime

from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.agendamento_model import Agendamento
from src.models.auth_model import User
from src.models.paciente_model import Paciente, ContatoEmergencia
from src.models.prescricao_model import Prescricao
from src.models.protocolo_model import Protocolo
from src.schemas.agendamento_schema import (
    AgendamentoCreate, DetalhesAgendamento, TipoAgendamento, AgendamentoStatusEnum, FarmaciaStatusEnum, TipoConsulta,
    TipoProcedimento
)
from src.schemas.prescricao_schema import PrescricaoStatusEnum
from src.scripts.seed_utils.builders import (
    criar_prescricao_payload, criar_historico_status_inicial, criar_historico_agendamento,
    criar_historico_alteracao_agendamento
)
from src.scripts.seed_utils.constants import TAGS_CONFIG
from src.scripts.seed_utils.helpers import encontrar_data_valida, gerar_horario

fake = Faker('pt_BR')


def instanciar_paciente_app(p_aghu) -> Paciente:
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
        observacoes_clinicas=random.choice([None, "Hipertenso", "Diabético", "Alergia a Dipirona", "Veias difíceis"])
    )
    p_app.contatos_emergencia.append(
        ContatoEmergencia(nome=fake.name(), telefone=fake.cellphone_number(), parentesco="Familiar")
    )
    return p_app


def _criar_agendamentos_infusao(
        session: AsyncSession,
        paciente: Paciente,
        prescricao: Prescricao,
        protocolo: Protocolo,
        data_base_ciclo: date,
        ciclo_num: int,
        dias_infusao: list[int]
):
    for dia_num in dias_infusao:
        data_ag = encontrar_data_valida(
            data_base_ciclo + timedelta(days=dia_num - 1),
            protocolo.dias_semana_permitidos
        )

        hoje = date.today()
        checkin = False

        if data_ag < hoje:
            status_ag = AgendamentoStatusEnum.CONCLUIDO
            checkin = True
            status_farm = FarmaciaStatusEnum.ENVIADO
        elif data_ag == hoje:
            status_ag = random.choice([
                AgendamentoStatusEnum.AGENDADO,
                AgendamentoStatusEnum.EM_INFUSAO,
                AgendamentoStatusEnum.CONCLUIDO
            ])
            checkin = status_ag != AgendamentoStatusEnum.AGENDADO
            status_farm = FarmaciaStatusEnum.AGENDADO if checkin else FarmaciaStatusEnum.ENVIADO
        else:
            status_ag = AgendamentoStatusEnum.AGENDADO
            status_farm = FarmaciaStatusEnum.AGENDADO

        inicio, fim = gerar_horario(random.choice(["manha", "tarde"]), protocolo.tempo_total_minutos)

        tags = []
        if ciclo_num == 1 and dia_num == 1:
            tags.append("1ª Vez de Quimio")
        if random.random() < 0.1:
            tags.append(random.choice(TAGS_CONFIG))

        detalhes_input = {
            "infusao": {
                "prescricao_id": prescricao.id,
                "status_farmacia": status_farm,
                "ciclo_atual": ciclo_num,
                "dia_ciclo": dia_num
            }
        }

        ag_validator = AgendamentoCreate(
            paciente_id=paciente.id,
            tipo=TipoAgendamento.INFUSAO,
            data=data_ag,
            turno="manha",
            horario_inicio=inicio,
            horario_fim=fim,
            checkin=checkin,
            status=status_ag,
            tags=list(set(tags)),
            observacoes=f"Ciclo {ciclo_num} Dia {dia_num} - Seed",
            detalhes=DetalhesAgendamento(**detalhes_input)
        )

        detalhes_json = ag_validator.detalhes.model_dump(mode='json', exclude_none=True)
        detalhes_json["historico_prescricoes"] = [{
            "data": datetime.now().isoformat(),
            "usuario_id": "seed",
            "usuario_nome": "Seed",
            "prescricao_id_anterior": None,
            "prescricao_id_nova": prescricao.id,
            "motivo": "Seed"
        }]

        ag = Agendamento(
            id=str(uuid.uuid4()),
            criado_por_id="enf.ana",
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
            historico_alteracoes=[
                criar_historico_alteracao_agendamento("status", "status", None, ag_validator.status)
            ]
        )
        session.add(ag)
        prescricao.historico_agendamentos.append(criar_historico_agendamento(ag.id, ag.status))


def _criar_ciclo_completo(
        session: AsyncSession,
        paciente: Paciente,
        protocolo: Protocolo,
        medico: User,
        ciclo_num: int,
        data_inicio_ciclo: date
):
    data_fim_ciclo = data_inicio_ciclo + timedelta(days=protocolo.duracao_ciclo_dias)
    hoje = date.today()

    if data_fim_ciclo < hoje:
        status_presc = PrescricaoStatusEnum.CONCLUIDA
    elif data_inicio_ciclo <= hoje <= data_fim_ciclo:
        status_presc = PrescricaoStatusEnum.EM_CURSO
    else:
        status_presc = PrescricaoStatusEnum.PENDENTE

    conteudo_json = criar_prescricao_payload(protocolo, paciente, medico, ciclo_num)

    data_emissao = datetime.combine(data_inicio_ciclo, datetime.min.time())
    if status_presc != PrescricaoStatusEnum.PENDENTE:
        data_emissao = datetime.now()

    presc = Prescricao(
        id=str(uuid.uuid4()),
        paciente_id=paciente.id,
        medico_id=medico.username,
        data_emissao=data_emissao,
        status=status_presc,
        conteudo=conteudo_json,
        historico_status=criar_historico_status_inicial(status_presc.value),
        historico_agendamentos=[]
    )
    session.add(presc)

    dias_infusao = set()
    for bloco in conteudo_json['blocos']:
        for item in bloco['itens']:
            for d in item['dias_do_ciclo']:
                dias_infusao.add(d)

    _criar_agendamentos_infusao(
        session, paciente, presc, protocolo,
        data_inicio_ciclo, ciclo_num, sorted(dias_infusao)
    )


def gerar_eventos_extras(session: AsyncSession, paciente: Paciente):
    hoje = date.today()

    for _ in range(5):
        data_evt = encontrar_data_valida(hoje + timedelta(days=random.randint(-30, 30)))
        passado = data_evt < hoje

        status = AgendamentoStatusEnum.CONCLUIDO if passado else AgendamentoStatusEnum.AGENDADO
        inicio, fim = gerar_horario(random.choice(["manha", "tarde"]), 30)

        if random.random() > 0.5:
            tipo = TipoAgendamento.CONSULTA
            detalhe_key = "consulta"
            detalhe_val = {"tipo_consulta": random.choice(list(TipoConsulta)).value}
        else:
            tipo = TipoAgendamento.PROCEDIMENTO
            detalhe_key = "procedimento"
            detalhe_val = {"tipo_procedimento": random.choice(list(TipoProcedimento)).value}

        ag = Agendamento(
            id=str(uuid.uuid4()),
            criado_por_id="enf.ana",
            paciente_id=paciente.id,
            tipo=tipo,
            data=data_evt,
            turno="manha",
            horario_inicio=inicio,
            horario_fim=fim,
            checkin=passado,
            status=status,
            detalhes={detalhe_key: detalhe_val},
            historico_alteracoes=[
                criar_historico_alteracao_agendamento("status", "status", None, status.value)
            ]
        )
        session.add(ag)


async def processar_jornada_paciente(
        session: AsyncSession,
        p_aghu,
        protocolos: list[Protocolo],
        medicos: list[User]
):
    paciente = instanciar_paciente_app(p_aghu)
    session.add(paciente)

    protocolo = random.choice(protocolos)
    medico = random.choice(medicos)

    ciclo_atual_simulado = random.randint(1, protocolo.total_ciclos)
    dias_corridos = (ciclo_atual_simulado - 1) * protocolo.duracao_ciclo_dias

    offset_aleatorio = random.randint(-5, 5)
    data_inicio_tratamento = encontrar_data_valida(
        date.today() - timedelta(days=dias_corridos) + timedelta(days=offset_aleatorio),
        protocolo.dias_semana_permitidos
    )

    for c in range(1, protocolo.total_ciclos + 1):
        delta_dias = (c - 1) * protocolo.duracao_ciclo_dias
        data_inicio_ciclo = encontrar_data_valida(
            data_inicio_tratamento + timedelta(days=delta_dias),
            protocolo.dias_semana_permitidos
        )
        _criar_ciclo_completo(session, paciente, protocolo, medico, c, data_inicio_ciclo)

    gerar_eventos_extras(session, paciente)
