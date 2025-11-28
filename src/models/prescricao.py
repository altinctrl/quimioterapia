from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..resources.database import Base


class PrescricaoMedica(Base):
    __tablename__ = "prescricoes_medicas"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(Integer, ForeignKey("pacientes.id"), nullable=False)

    medico_id = Column(String, nullable=True)
    medico_nome = Column(String, nullable=False)

    data_prescricao = Column(Date, nullable=False)

    peso = Column(Float, nullable=True)
    altura = Column(Float, nullable=True)
    superficie_corporea = Column(Float, nullable=True)
    diagnostico = Column(Text, nullable=True)

    protocolo_nome = Column(String, nullable=False)
    numero_ciclo = Column(Integer, nullable=False)
    dia_ciclo = Column(String, nullable=True)
    frequencia = Column(String, nullable=True)
    observacoes_protocolo = Column(Text, nullable=True)

    pre_qt = Column(JSON, nullable=True)
    qt = Column(JSON, nullable=True)
    pos_qt = Column(JSON, nullable=True)

    tempo_total_infusao = Column(Integer, nullable=False)

    assinado = Column(Boolean, default=False)
    data_assinatura = Column(Date, nullable=True)
    hora_assinatura = Column(String, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    paciente = relationship("Paciente", back_populates="prescricoes")