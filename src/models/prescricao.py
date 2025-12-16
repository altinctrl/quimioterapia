from sqlalchemy import Column, Integer, String, Float, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.resources.database import Base


class Prescricao(Base):
    __tablename__ = "prescricoes"

    id = Column(String, primary_key=True)
    paciente_id = Column(String, ForeignKey("pacientes.id"))
    protocolo_id = Column(String, ForeignKey("protocolos.id"), nullable=True)
    protocolo_nome_snapshot = Column(String)

    medico_nome = Column(String, nullable=False)
    # medico_id = Column(String, nullable=True) # Futuro: Ligar à tabela de usuários

    data_prescricao = Column(Date, default=func.now())
    created_at = Column(DateTime, server_default=func.now())

    ciclo_atual = Column(Integer)
    ciclos_total = Column(Integer)

    peso = Column(Float)
    altura = Column(Float)
    superficie_corporea = Column(Float)
    diagnostico = Column(Text)

    status = Column(String, default='ativa')
    observacoes = Column(Text, nullable=True)

    paciente = relationship("Paciente", back_populates="prescricoes")
    itens = relationship("ItemPrescricao", back_populates="prescricao", cascade="all, delete-orphan")


class ItemPrescricao(Base):
    __tablename__ = "itens_prescricao"

    id = Column(Integer, primary_key=True, index=True)
    prescricao_id = Column(String, ForeignKey("prescricoes.id"))

    tipo = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    dose = Column(String)
    unidade = Column(String)
    via = Column(String)

    tempo_infusao = Column(Integer, nullable=True)
    veiculo = Column(String, nullable=True)
    volume_veiculo = Column(String, nullable=True)

    ordem = Column(Integer, default=0)
    observacoes = Column(String, nullable=True)

    prescricao = relationship("Prescricao", back_populates="itens")
