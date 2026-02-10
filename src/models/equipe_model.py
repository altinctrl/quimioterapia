import uuid

from sqlalchemy import Column, String, Date, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from src.resources.database import Base


class Profissional(Base):
    __tablename__ = "profissionais"

    username = Column(String, ForeignKey("users.username"), primary_key=True)
    cargo = Column(String, nullable=False)
    ativo = Column(Boolean, default=True)

    usuario = relationship("User", back_populates="profissional_equipe")
    escalas = relationship("EscalaPlantao", back_populates="profissional")
    ausencias = relationship("AusenciaProfissional", back_populates="profissional")


class EscalaPlantao(Base):
    __tablename__ = "escala_plantao"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    data = Column(Date, nullable=False, index=True)
    profissional_id = Column(String, ForeignKey("profissionais.username"), nullable=False)
    funcao = Column(String, nullable=False)
    turno = Column(String, nullable=False)

    profissional = relationship("Profissional", back_populates="escalas")


class AusenciaProfissional(Base):
    __tablename__ = "ausencia_profissional"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    profissional_id = Column(String, ForeignKey("profissionais.username"), nullable=False)
    data_inicio = Column(Date, nullable=False)
    data_fim = Column(Date, nullable=False)
    motivo = Column(String, nullable=False)
    observacao = Column(Text, nullable=True)

    profissional = relationship("Profissional", back_populates="ausencias")
