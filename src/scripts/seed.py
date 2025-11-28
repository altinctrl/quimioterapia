import asyncio
import sys
import os

sys.path.append(os.getcwd())

from sqlalchemy import select, delete
from src.resources.database import DatabaseManager
from src.models.protocolo import Protocolo
from src.models.paciente import Paciente
from src.models.poltrona import Poltrona
from src.models.agendamento import Agendamento
from src.models.prescricao import PrescricaoMedica
from datetime import datetime, date

DSN = "postgresql+asyncpg://user:password@localhost:5432/db_quimio"


async def seed():
    print("Iniciando conexão com o banco...")
    db = DatabaseManager(DSN)

    async for session in db.get_session():
        print("Limpando dados antigos...")
        await session.execute(delete(Agendamento))
        await session.execute(delete(PrescricaoMedica))
        await session.execute(delete(Paciente))
        await session.execute(delete(Protocolo))
        await session.execute(delete(Poltrona))
        await session.commit()

        print("Inserindo Protocolos...")
        protocolos_data = [
            {"id": 1, "nome": 'FOLFOX', "duracao": 180, "frequencia": '14 dias'},
            {"id": 2, "nome": 'AC-T', "duracao": 120, "frequencia": '21 dias'},
            {"id": 3, "nome": 'Paclitaxel', "duracao": 240, "frequencia": '7 dias'},
            {"id": 4, "nome": 'Carboplatina', "duracao": 90, "frequencia": '21 dias'},
            {"id": 5, "nome": 'Rituximab', "duracao": 300, "frequencia": '28 dias'},
        ]

        protocolos_map = {}
        for p_data in protocolos_data:
            p = Protocolo(**p_data)
            session.add(p)
            protocolos_map[str(p_data["id"])] = p

        await session.flush()

        print("Inserindo Pacientes...")
        pacientes_data = [
            {"nome": 'Maria Silva Santos', "registro": '12345-6', "data_nascimento": date(1965, 3, 15),
             "telefone": '(11) 98765-4321', "protocolo_id": 1},
            {"nome": 'João Carlos Oliveira', "registro": '12346-7', "data_nascimento": date(1958, 7, 22),
             "telefone": '(11) 98765-4322', "protocolo_id": 2},
            {"nome": 'Ana Paula Costa', "registro": '12347-8', "data_nascimento": date(1972, 11, 10),
             "telefone": '(11) 98765-4323', "protocolo_id": 3},
            {"nome": 'Carlos Eduardo Pereira', "registro": '12348-9', "data_nascimento": date(1960, 5, 18),
             "telefone": '(11) 98765-4324', "protocolo_id": 1},
            {"nome": 'Fernanda Lima Souza', "registro": '12349-0', "data_nascimento": date(1968, 9, 25),
             "telefone": '(11) 98765-4325', "protocolo_id": 4},
            {"nome": 'Roberto Alves Martins', "registro": '12350-1', "data_nascimento": date(1955, 2, 14),
             "telefone": '(11) 98765-4326', "protocolo_id": 5},
            {"nome": 'Juliana Rodrigues', "registro": '12351-2', "data_nascimento": date(1975, 6, 30),
             "telefone": '(11) 98765-4327', "protocolo_id": 2},
            {"nome": 'Pedro Henrique Silva', "registro": '12352-3', "data_nascimento": date(1963, 12, 8),
             "telefone": '(11) 98765-4328', "protocolo_id": 3},
        ]

        pacientes_inseridos = []
        for pac in pacientes_data:
            novo_paciente = Paciente(**pac)
            session.add(novo_paciente)
            pacientes_inseridos.append(novo_paciente)

        await session.flush()

        paciente_map = {p.registro: p.id for p in pacientes_inseridos}

        print("Inserindo Poltronas...")
        poltronas_map = {}

        for i in range(1, 11):
            p = Poltrona(numero=i, tipo='poltrona', disponivel=True)
            session.add(p)
            await session.flush()
            poltronas_map[f'p{i}'] = p.id

        for i in range(11, 17):
            idx_leito = i - 10
            p = Poltrona(numero=i, tipo='leito', disponivel=True)
            session.add(p)
            await session.flush()
            poltronas_map[f'l{idx_leito}'] = p.id

        print("Inserindo Agendamentos...")
        hoje = date.today()

        agendamentos_data = [
            {"paciente_registro": '12345-6', "data": hoje, "turno": 'manha', "horario_inicio": '07:00',
             "horario_fim": '10:00', "poltrona_orig": 'p1', "status": 'em-infusao', "encaixe": False,
             "status_farmacia": 'enviada', "hora_inicio_real": '07:15'},
            {"paciente_registro": '12346-7', "data": hoje, "turno": 'manha', "horario_inicio": '08:00',
             "horario_fim": '10:00', "poltrona_orig": 'p2', "status": 'aguardando-medicamento', "encaixe": False,
             "status_farmacia": 'em-preparacao'},
            {"paciente_registro": '12347-8', "data": hoje, "turno": 'manha', "horario_inicio": '07:00',
             "horario_fim": '11:00', "poltrona_orig": 'l1', "status": 'aguardando-exame', "encaixe": False,
             "status_farmacia": 'pendente'},
            {"paciente_registro": '12348-9', "data": hoje, "turno": 'tarde', "horario_inicio": '13:00',
             "horario_fim": '16:00', "poltrona_orig": 'p3', "status": 'agendado', "encaixe": False,
             "status_farmacia": 'pendente'},
            {"paciente_registro": '12349-0', "data": hoje, "turno": 'tarde', "horario_inicio": '14:00',
             "horario_fim": '15:30', "poltrona_orig": 'p4', "status": 'agendado', "encaixe": False,
             "status_farmacia": 'pendente'},
            {"paciente_registro": '12350-1', "data": hoje, "turno": 'manha', "horario_inicio": '09:00',
             "horario_fim": '14:00', "poltrona_orig": 'l2', "status": 'em-triagem', "encaixe": True,
             "status_farmacia": 'pronta'},
            {"paciente_registro": '12351-2', "data": hoje, "turno": 'tarde', "horario_inicio": '15:00',
             "horario_fim": '17:00', "poltrona_orig": 'p5', "status": 'agendado', "encaixe": False,
             "status_farmacia": 'pendente'},
        ]

        for ag in agendamentos_data:
            pac_id = paciente_map.get(ag["paciente_registro"])
            polt_id = poltronas_map.get(ag["poltrona_orig"])

            if pac_id and polt_id:
                novo_ag = Agendamento(
                    paciente_id=pac_id,
                    poltrona_id=polt_id,
                    data=ag["data"],
                    turno=ag["turno"],
                    horario_inicio=ag["horario_inicio"],
                    horario_fim=ag["horario_fim"],
                    status=ag["status"],
                    status_farmacia=ag["status_farmacia"],
                    encaixe=ag["encaixe"],
                    hora_inicio_real=ag.get("hora_inicio_real")
                )
                session.add(novo_ag)

        await session.commit()
        print("Dados inseridos com sucesso!")


if __name__ == "__main__":
    asyncio.run(seed())