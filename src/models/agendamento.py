from sqlalchemy import Column, Integer, String, Date, Boolean, ForeignKey, Time, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..resources.database import Base


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(Integer, primary_key=True, index=True)

    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)
    poltrona_id = Column(Integer, ForeignKey("poltronas.id"), nullable=False)

    data = Column(Date, nullable=False)
    turno = Column(String, nullable=False)
    horario_inicio = Column(String, nullable=False)
    horario_fim = Column(String, nullable=False)

    status = Column(String, default="agendado", index=True)
    status_farmacia = Column(String, default="pendente")
    encaixe = Column(Boolean, default=False)

    hora_inicio_real = Column(String, nullable=True)
    hora_fim_real = Column(String, nullable=True)
    intercorrencias = Column(Text, nullable=True)

    created_at = Column(DateTime, server_default=func.now())

    paciente = relationship("Paciente", back_populates="agendamentos")
    poltrona = relationship("Poltrona", back_populates="agendamentos")