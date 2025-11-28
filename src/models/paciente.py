from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from ..resources.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    registro = Column(String, unique=True, index=True, nullable=False)  # Prontuário
    data_nascimento = Column(Date, nullable=False)
    telefone = Column(String, nullable=False)
    observacoes = Column(Text, nullable=True)

    protocolo_id = Column(Integer, ForeignKey("protocolos.id"), nullable=True)

    protocolo = relationship("Protocolo", back_populates="pacientes")
    agendamentos = relationship("Agendamento", back_populates="paciente")
    prescricoes = relationship("PrescricaoMedica", back_populates="paciente")