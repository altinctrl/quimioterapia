from sqlalchemy import Column, Integer, String, Boolean, Text, Date, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.resources.database import Base


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(String, primary_key=True)
    paciente_id = Column(String, ForeignKey("pacientes.id"))
    tipo = Column(String, nullable=False)
    data = Column(Date, nullable=False, index=True)
    turno = Column(String, nullable=False)
    horario_inicio = Column(String, nullable=False)
    horario_fim = Column(String, nullable=False)
    encaixe = Column(Boolean, default=False)
    status = Column(String, default='agendado')
    observacoes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)
    detalhes = Column(JSON, nullable=True)

    paciente = relationship("Paciente", back_populates="agendamentos")
