import uuid
from datetime import datetime

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from src.resources.database import Base


class Prescricao(Base):
    __tablename__ = "prescricoes"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    paciente_id = Column(String, ForeignKey("pacientes.id"), nullable=False, index=True)
    medico_id = Column(String, ForeignKey("profissionais.username"), nullable=False)
    data_emissao = Column(DateTime, default=datetime.now)
    status = Column(String, default="pendente")
    conteudo = Column(JSONB, nullable=False)
    historico_status = Column(JSONB, nullable=True, default=list)
    historico_agendamentos = Column(JSONB, nullable=True, default=list)
    prescricao_substituta_id = Column(String, ForeignKey("prescricoes.id"), nullable=True)
    prescricao_original_id = Column(String, ForeignKey("prescricoes.id"), nullable=True)

    paciente = relationship("Paciente", back_populates="prescricoes")
    medico = relationship("Profissional")
