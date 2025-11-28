from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..resources.database import Base

class Poltrona(Base):
    __tablename__ = "poltronas"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer, nullable=False)
    tipo = Column(String, nullable=False)
    disponivel = Column(Boolean, default=True)

    agendamentos = relationship("Agendamento", back_populates="poltrona")