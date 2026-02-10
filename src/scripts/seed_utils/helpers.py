import random
from datetime import date, timedelta, datetime


def calcular_bsa(peso: float, altura_cm: float) -> float:
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
