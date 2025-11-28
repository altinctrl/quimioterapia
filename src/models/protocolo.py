from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..resources.database import Base

class Protocolo(Base):
    __tablename__ = "protocolos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    duracao = Column(Integer, nullable=False)
    frequencia = Column(String, nullable=False)
    restricoes = Column(String, nullable=True)

    pacientes = relationship("Paciente", back_populates="protocolo")