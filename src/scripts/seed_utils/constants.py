import csv
from pathlib import Path

from src.schemas.equipe_schema import MotivoAusenciaEnum

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"


def load_csv_list(filename: str) -> list[str]:
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return []
    with open(filepath, mode='r', encoding='utf-8') as f:
        reader = csv.reader(f, quotechar='"')
        return [row[0] for row in reader if row]


NUM_PACIENTES_AGHU = 1000
NUM_PACIENTES_APP = 100
DIAS_FUNCIONAMENTO = [1, 2, 3, 4, 5]  # Seg-Sex
HORARIO_ABERTURA = "07:00"
HORARIO_FECHAMENTO = "19:00"

TAGS_CONFIG = load_csv_list("tags.csv")
DILUENTES_CONFIG = load_csv_list("diluentes.csv")

CARGOS = ["Enfermeiro", "Técnico de Enfermagem"]
FUNCOES = ["Gestão", "Salão QT", "Triagem/Marcação", "Consulta de Enfermagem", "Apoio"]

VAGAS_CONFIG = {
    "infusao_rapido": 16,
    "infusao_medio": 8,
    "infusao_longo": 4,
    "infusao_extra_longo": 4,
    "consultas": 10,
    "procedimentos": 10
}

USUARIOS_SEED = [
    {
        "username": "admin",
        "display_name": "Louro José",
        "role": "admin",
        "registro_profissional": "CRM-TEST 99999",
        "tipo_registro": "CRM",
        "groups": ["admins"]
    },
    {
        "username": "enf.ana",
        "display_name": "Ana Maria",
        "role": "enfermeiro",
        "registro_profissional": "123456",
        "tipo_registro": "COREN",
        "groups": ["enfermeiros"]
    },
    {
        "username": "tec.joao",
        "display_name": "João Silva",
        "role": "tecnico",
        "registro_profissional": "987654",
        "tipo_registro": "COREN",
        "groups": ["tecnicos"]
    }
]

MEDICOS_SEED = [
    {
        "username": "med.carlos",
        "display_name": "Dr. Carlos Alberto",
        "role": "medico",
        "registro_profissional": "CRM-UF 12345",
        "tipo_registro": "CRM",
        "groups": ["medicos"]
    },
    {
        "username": "med.fernanda",
        "display_name": "Dra. Fernanda Ramos",
        "role": "medico",
        "registro_profissional": "CRM-UF 67890",
        "tipo_registro": "CRM",
        "groups": ["medicos"]
    },
    {
        "username": "med.roberto",
        "display_name": "Dr. Roberto Marinho",
        "role": "medico",
        "registro_profissional": "CRM-UF 54321",
        "tipo_registro": "CRM",
        "groups": ["medicos"]
    }
]

EQUIPE_SEED = [
    {"username": "enf.ana", "cargo": "Enfermeiro"},
    {"username": "tec.joao", "cargo": "Técnico de Enfermagem"}
]

ESCALAS_SEED = [
    {"offset": 0, "profissional_id": "enf.ana", "funcao": "Gestão", "turno": "Integral"},
    {"offset": 0, "profissional_id": "tec.joao", "funcao": "Salão QT", "turno": "Manhã"},
    {"offset": 1, "profissional_id": "tec.joao", "funcao": "Salão QT", "turno": "Tarde"},
]

AUSENCIAS_SEED = [
    {
        "profissional_id": "enf.ana",
        "offset_inicio": 5,
        "offset_fim": 20,
        "motivo": MotivoAusenciaEnum.LTS
    }
]
