from sqlalchemy import Column, Integer, String, JSON

from src.resources.database import Base


class Configuracao(Base):
    __tablename__ = "configuracoes"

    id = Column(Integer, primary_key=True)
    horario_abertura = Column(String, default="07:00")
    horario_fechamento = Column(String, default="19:00")
    dias_funcionamento = Column(JSON, default=[1, 2, 3, 4, 5])
    grupos_infusao = Column(JSON)
    tags = Column(JSON, default=[])
    cargos = Column(JSON, default=[])
    funcoes = Column(JSON, default=[])
