from sqlalchemy import Column, Integer, String, Boolean, Text, Date, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.resources.database import Base


class Agendamento(Base):
    __tablename__ = "agendamentos"

    id = Column(String, primary_key=True)
    paciente_id = Column(String, ForeignKey("pacientes.id"))

    data = Column(Date, nullable=False, index=True)
    turno = Column(String, nullable=False)
    horario_inicio = Column(String, nullable=False)
    horario_fim = Column(String, nullable=False)

    ciclo_atual = Column(Integer)
    dia_ciclo = Column(String)
    encaixe = Column(Boolean, default=False)

    status = Column(String, default='agendado')
    status_farmacia = Column(String, default='pendente')

    tempo_estimado_preparo = Column(Integer, nullable=True)
    horario_previsao_entrega = Column(String, nullable=True)

    observacoes = Column(Text, nullable=True)
    tags = Column(JSON, nullable=True)

    paciente = relationship("Paciente", back_populates="agendamentos")
