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

    paciente = relationship("Paciente", back_populates="prescricoes")
    medico = relationship("Profissional")
