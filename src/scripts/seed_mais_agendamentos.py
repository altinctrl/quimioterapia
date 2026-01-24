import argparse
import asyncio
import random
import uuid
from datetime import date, timedelta, datetime

from sqlalchemy import select

from src.models.agendamento import Agendamento
from src.models.equipe import Profissional
from src.models.paciente import Paciente
from src.models.prescricao import Prescricao
from src.models.protocolo import Protocolo
from src.resources.database import app_engine, AppSessionLocal
from src.schemas.agendamento import AgendamentoStatusEnum, FarmaciaStatusEnum, TipoAgendamento
from src.schemas.prescricao import (
    ItemPrescricao, BlocoPrescricao, PacienteSnapshot,
    MedicoSnapshot, ProtocoloRef, PrescricaoStatusEnum
)
from src.schemas.protocolo import TemplateCiclo, UnidadeDoseEnum

TAGS_EXTRA = [
    "1ª Vez de Quimio", "Mudança de Protocolo", "Redução de Dose", "Virá à Tarde", "Continuidade", "Aguarda Contínuo",
    "Laboratório Ciente", "Quimio Adiada", "Comunicado ao Paciente", "Virá Após a RDT"
]


def calcular_bsa(peso, altura_cm):
    if not peso or not altura_cm: return 1.7
    altura_m = altura_cm / 100
    return 0.007184 * (peso ** 0.425) * (altura_m ** 0.725)


def gerar_horario_random(turno="manha"):
    h_inicio = random.randint(8, 11) if turno == "manha" else random.randint(13, 16)
    m_inicio = random.choice([0, 15, 30])
    dt_inicio = datetime.now().replace(hour=h_inicio, minute=m_inicio, second=0, microsecond=0)
    dt_fim = dt_inicio + timedelta(hours=random.randint(2, 4))
    return dt_inicio.strftime("%H:%M"), dt_fim.strftime("%H:%M")


def criar_prescricao_payload_script(
        protocolo_model: Protocolo,
        paciente: Paciente,
        medico_obj: Profissional,
        ciclo: int
):
    bsa = calcular_bsa(paciente.peso, paciente.altura)

    raw_templates = protocolo_model.templates_ciclo
    if not isinstance(raw_templates, list):
        raw_templates = [raw_templates]

    templates = [TemplateCiclo(**t) for t in raw_templates]
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

                item_p = ItemPrescricao(
                    id_item=str(uuid.uuid4()),
                    medicamento=dados.medicamento,
                    dose_referencia=str(dados.dose_referencia),
                    unidade=dados.unidade,
                    percentual_ajuste=100.0,
                    dose_final=round(dose_calc, 2),
                    via=dados.via,
                    tempo_minutos=dados.tempo_minutos,
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
        "observacoes": "Gerado via script de carga extra."
    }

    return documento_json


async def add_agendamentos(data_fixa: date = None, quantidade: int = None):
    async with AppSessionLocal() as session:
        result_pac = await session.execute(select(Paciente))
        pacientes = result_pac.scalars().all()

        result_prot = await session.execute(select(Protocolo))
        protocolos = result_prot.scalars().all()

        result_med = await session.execute(select(Profissional).where(Profissional.cargo == 'Médico'))
        medicos = result_med.scalars().all()

        if not all([pacientes, protocolos, medicos]):
            print("Dados insuficientes (pacientes, protocolos ou médicos). Rode o seed.py primeiro.")
            return

        print(f"Gerando agendamentos extras baseados em {len(pacientes)} pacientes...")

        qtde_loop = quantidade if quantidade else 10
        novos_agendamentos = 0

        for _ in range(qtde_loop):
            paciente = random.choice(pacientes)
            prot = random.choice(protocolos)
            medico = random.choice(medicos)

            data_ag = data_fixa if data_fixa else (date.today() + timedelta(days=random.randint(0, 15)))

            ciclo = random.randint(1, prot.total_ciclos or 6)
            conteudo_prescricao = criar_prescricao_payload_script(prot, paciente, medico, ciclo)

            presc_id = str(uuid.uuid4())
            presc = Prescricao(
                id=presc_id,
                paciente_id=paciente.id,
                medico_id=medico.username,
                data_emissao=datetime.now(),
                status=PrescricaoStatusEnum.PENDENTE,
                conteudo=conteudo_prescricao
            )
            session.add(presc)

            turno = random.choice(["manha", "tarde"])
            inicio, fim = gerar_horario_random(turno)
            tags = random.sample(TAGS_EXTRA, k=random.randint(0, 2))

            checkin = False
            status_ag = AgendamentoStatusEnum.CONCLUIDO
            status_farm = FarmaciaStatusEnum.PENDENTE

            if data_ag < date.today():
                status_ag = AgendamentoStatusEnum.CONCLUIDO
                checkin = True
                status_farm = FarmaciaStatusEnum.ENVIADO
            elif data_ag == date.today():
                status_ag = random.choice([AgendamentoStatusEnum.AGENDADO,
                                           AgendamentoStatusEnum.EM_INFUSAO,
                                           AgendamentoStatusEnum.CONCLUIDO])
                checkin = status_ag != AgendamentoStatusEnum.CONCLUIDO
                status_farm = FarmaciaStatusEnum.ENVIADO if checkin else FarmaciaStatusEnum.PENDENTE

            ag = Agendamento(
                id=str(uuid.uuid4()),
                paciente_id=paciente.id,
                tipo=TipoAgendamento.INFUSAO,
                data=data_ag,
                turno=turno,
                horario_inicio=inicio,
                horario_fim=fim,
                checkin=checkin,
                status=status_ag,
                tags=tags,
                observacoes="Agendamento extra script.",
                criado_por_id="admin",
                detalhes={
                    "infusao": {
                        "prescricao_id": presc_id,
                        "status_farmacia": status_farm,
                        "ciclo_atual": ciclo,
                        "dia_ciclo": 1
                    }
                }
            )
            session.add(ag)
            novos_agendamentos += 1

        await session.commit()
        print(
            f"{novos_agendamentos} novos agendamentos criados para {data_ag.strftime('%d/%m/%Y') if data_fixa else 'datas variadas'}.")

    await app_engine.dispose()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Adiciona agendamentos extras ao banco.")
    parser.add_argument("--data", type=str, help="Data no formato YYYY-MM-DD (ex: 2024-12-25)")
    parser.add_argument("--quantidade", "-q", type=int, help="Total de agendamentos a criar")

    args = parser.parse_args()

    data_alvo = None
    if args.data:
        try:
            data_alvo = datetime.strptime(args.data, "%Y-%m-%d").date()
        except ValueError:
            print("Formato de data inválido. Use YYYY-MM-DD.")
            exit(1)

    asyncio.run(add_agendamentos(data_alvo, args.quantidade))
