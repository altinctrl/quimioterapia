import asyncio
import os
from datetime import date

from dotenv import load_dotenv

from src.models.agendamento import Agendamento
from src.models.configuracao import Configuracao
from src.models.paciente import Paciente, ContatoEmergencia
from src.models.prescricao import Prescricao, ItemPrescricao
from src.models.protocolo import Protocolo, ItemProtocolo
from src.resources.database import DatabaseManager

load_dotenv()


async def seed_data():
    print("Iniciando Seed do Banco de Dados...")

    dsn = os.getenv("APP_DB_URL")
    if not dsn:
        if os.getenv("PACIENTE_PROVIDER_TYPE") == "POSTGRES":
            dsn = os.getenv("POSTGRES_DSN")
        else:
            dsn = "sqlite+aiosqlite:///app.db"

    print(f"Conectando em: {dsn}")
    db_manager = DatabaseManager(dsn)

    # Recriar tabelas (Opcional: cuidado em produção!)
    # async with db_manager.engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)

    async for session in db_manager.get_session():
        try:
            print("Configurando parâmetros da clínica...")
            config = Configuracao(id=1, horario_abertura="07:00", horario_fechamento="19:00",
                                  dias_funcionamento=[1, 2, 3, 4, 5],
                                  grupos_infusao={"rapido": {"vagas": 4, "duracao": "< 2h"},
                                                  "medio": {"vagas": 8, "duracao": "2h - 4h"},
                                                  "longo": {"vagas": 4, "duracao": "> 4h"}})
            await session.merge(config)

            print("Criando Protocolos...")
            prot1 = Protocolo(id="prot-1", nome="FOLFOX 6", duracao=180, frequencia="14 dias", numero_ciclos=12,
                              grupo_infusao="medio", indicacao="Câncer Colorretal")
            session.add(prot1)
            session.add(ItemProtocolo(protocolo_id="prot-1", tipo="pre", nome="Ondansetrona", dose_padrao="8",
                                      unidade_padrao="mg", via_padrao="IV"))
            session.add(ItemProtocolo(protocolo_id="prot-1", tipo="qt", nome="Oxaliplatina", dose_padrao="85",
                                      unidade_padrao="mg/m²", via_padrao="IV"))

            prot2 = Protocolo(id="prot-2", nome="Paclitaxel Semanal", duracao=60, frequencia="7 dias", numero_ciclos=12,
                              grupo_infusao="rapido", indicacao="Mama / Ovário")
            session.add(prot2)
            session.add(ItemProtocolo(protocolo_id="prot-2", tipo="pre", nome="Dexametasona", dose_padrao="10",
                                      unidade_padrao="mg", via_padrao="IV"))
            session.add(ItemProtocolo(protocolo_id="prot-2", tipo="qt", nome="Paclitaxel", dose_padrao="80",
                                      unidade_padrao="mg/m²", via_padrao="IV"))

            print("Criando Pacientes...")
            pac1 = Paciente(id="pac-1", nome="Maria Silva Santos", cpf="123.456.789-01", registro="HC123456",
                            data_nascimento=date(1965, 3, 15), telefone="(11) 99999-9999", peso=68.0, altura=165.0,
                            observacoes_clinicas="Veias difíceis.")
            pac2 = Paciente(id="pac-2", nome="João Carlos Oliveira", cpf="234.567.890-12", registro="HC123457",
                            data_nascimento=date(1958, 7, 22), telefone="(11) 88888-8888", peso=82.0, altura=175.0,
                            observacoes_clinicas="Alergia a Dipirona.")
            session.add_all([pac1, pac2])

            session.add(ContatoEmergencia(paciente_id="pac-1", nome="José", parentesco="Esposo", telefone="999"))

            print("Criando Agendamentos...")
            hoje = date.today()

            ag1 = Agendamento(id="ag-1", paciente_id="pac-1", data=hoje, turno="manha", horario_inicio="08:00",
                              horario_fim="11:00", status="em-infusao", status_farmacia="enviada", ciclo_atual=4,
                              dia_ciclo="D1", horario_previsao_entrega="08:30")

            ag2 = Agendamento(id="ag-2", paciente_id="pac-2", data=hoje, turno="tarde", horario_inicio="13:00",
                              horario_fim="14:00", status="agendado", status_farmacia="pendente", ciclo_atual=2,
                              dia_ciclo="D8")

            session.add_all([ag1, ag2])

            print("Criando Prescrições...")
            presc1 = Prescricao(id="pres-1", paciente_id="pac-1", protocolo_id="prot-1",
                                protocolo_nome_snapshot="FOLFOX 6", medico_nome="Dr. Oncologista", data_prescricao=hoje,
                                ciclo_atual=4, ciclos_total=12, peso=68.0, altura=165.0, superficie_corporea=1.76,
                                diagnostico="Câncer de Cólon", status="ativa")
            session.add(presc1)
            session.add(ItemPrescricao(prescricao_id="pres-1", tipo="pre", nome="Ondansetrona", dose="8 mg", via="IV"))
            session.add(ItemPrescricao(prescricao_id="pres-1", tipo="qt", nome="Oxaliplatina", dose="150 mg", via="IV",
                                       tempo_infusao=120, veiculo="SF", volume_veiculo="500ml"))

            await session.commit()
            print("Seed concluído com sucesso!")

        except Exception as e:
            print(f"Erro no seed: {e}")
            await session.rollback()
        finally:
            await db_manager.close_connection()


if __name__ == "__main__":
    asyncio.run(seed_data())
