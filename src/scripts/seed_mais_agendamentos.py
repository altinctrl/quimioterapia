import argparse
import asyncio
import random
import uuid
from datetime import date, timedelta, datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.agendamento import Agendamento
from src.models.paciente import Paciente
from src.models.prescricao import Prescricao, ItemPrescricao
from src.models.protocolo import Protocolo
from src.resources.database import app_engine, AppSessionLocal

TAGS_EXTRA = [
    "Encaixe", "Virá à Tarde", "Laboratório Pendente",
    "Aguarda Medicação", "Prioridade", "Retorno Médico"
]


def gerar_horario_random():
    h = random.randint(7, 16)
    m = random.choice(["00", "30"])
    return f"{h:02d}:{m}", f"{h + 2:02d}:{m}"


async def add_agendamentos(data_fixa: date = None, quantidade: int = None):
    async with AppSessionLocal() as session:
        result_pac = await session.execute(select(Paciente))
        pacientes = result_pac.scalars().all()

        result_prot = await session.execute(select(Protocolo).options(selectinload(Protocolo.itens)))
        protocolos = result_prot.scalars().all()

        if not pacientes or not protocolos:
            print("Nenhum paciente ou protocolo encontrado. Rode o seed.py primeiro.")
            return

        print(f"Encontrados {len(pacientes)} pacientes. Gerando agendamentos...")

        pool_pacientes = random.choices(pacientes, k=quantidade) if quantidade else [p for p in pacientes if
                                                                                     random.random() < 0.4]
        novos_agendamentos = 0
        for paciente in pool_pacientes:
            prot = random.choice(protocolos)
            data_ag = data_fixa if data_fixa else (date.today() + timedelta(days=random.randint(1, 15)))
            inicio, fim = gerar_horario_random()
            tags = random.sample(TAGS_EXTRA, k=random.randint(0, 2))

            ciclo = random.randint(1, 12)
            ag = Agendamento(
                id=str(uuid.uuid4()),
                paciente_id=paciente.id,
                tipo="infusao",
                data=data_ag,
                turno="manha" if int(inicio[:2]) < 12 else "tarde",
                horario_inicio=inicio,
                horario_fim=fim,
                status="agendado",
                encaixe=random.choice([True, False]),
                tags=tags,
                observacoes="Agendamento extra gerado via script.",
                criado_por_id="usuario_teste",
                detalhes={
                    "infusao": {
                        "status_farmacia": "pendente",
                        "ciclo_atual": ciclo,
                        "dia_ciclo": "D1"
                    }
                }
            )

            presc = Prescricao(
                id=str(uuid.uuid4()),
                paciente_id=paciente.id,
                protocolo_id=prot.id,
                protocolo_nome_snapshot=prot.nome,
                medico_nome="Médico Plantonista",
                data_prescricao=data_ag,
                ciclo_atual=ag.ciclo_atual,
                ciclos_total=prot.numero_ciclos,
                peso=paciente.peso,
                altura=paciente.altura,
                status="ativa",
                diagnostico=prot.indicacao
            )

            for item_p in prot.itens:
                presc.itens.append(ItemPrescricao(
                    tipo=item_p.tipo, nome=item_p.nome, dose=item_p.dose_padrao,
                    unidade=item_p.unidade_padrao, via=item_p.via_padrao
                ))

            session.add(ag)
            session.add(presc)
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
