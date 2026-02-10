from sqlalchemy import Column, Integer, String, Date

from src.resources.database import Base


class AghuPaciente(Base):
    __tablename__ = "aip_pacientes"

    codigo = Column(Integer, primary_key=True)
    nome = Column(String, nullable=False)
    cpf = Column(String)
    dt_nascimento = Column(Date)
    sexo = Column(String)
    nome_mae = Column(String)
    nome_pai = Column(String)
