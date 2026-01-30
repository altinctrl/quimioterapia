from sqlalchemy import Column, Integer, String, Text, Boolean, JSON
from sqlalchemy.dialects.postgresql import JSONB

from src.resources.database import Base


class Protocolo(Base):
    __tablename__ = "protocolos"

    id = Column(String, primary_key=True)
    nome = Column(String, nullable=False, index=True)
    indicacao = Column(String, nullable=True)
    tipo_terapia = Column(String, nullable=True)
    tempo_total_minutos = Column(Integer, nullable=False)
    duracao_ciclo_dias = Column(Integer, nullable=False)
    total_ciclos = Column(Integer, nullable=True)
    fase = Column(String, nullable=True)
    linha = Column(Integer, nullable=True)
    dias_semana_permitidos = Column(JSON, nullable=True)
    observacoes = Column(Text, nullable=True)
    precaucoes = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)

    templates_ciclo = Column(JSONB, nullable=False)
