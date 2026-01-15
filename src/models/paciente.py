from sqlalchemy import Column, Integer, String, Float, Text, Date, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from src.resources.database import Base


class Paciente(Base):
    __tablename__ = "pacientes"

    id = Column(String, primary_key=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    nome = Column(String, nullable=False)
    cpf = Column(String, unique=True, index=True)
    registro = Column(String, unique=True, index=True)
    data_nascimento = Column(Date, nullable=False)
    telefone = Column(String)
    email = Column(String, nullable=True)

    peso = Column(Float, nullable=True)
    altura = Column(Float, nullable=True)
    observacoes_clinicas = Column(Text, nullable=True)

    contatos_emergencia = relationship("ContatoEmergencia", back_populates="paciente", cascade="all, delete-orphan")
    agendamentos = relationship("Agendamento", back_populates="paciente")
    prescricoes = relationship("Prescricao", back_populates="paciente")


class ContatoEmergencia(Base):
    __tablename__ = "contatos_emergencia"

    id = Column(Integer, primary_key=True, index=True)
    paciente_id = Column(String, ForeignKey("pacientes.id"))
    nome = Column(String, nullable=False)
    parentesco = Column(String)
    telefone = Column(String)

    paciente = relationship("Paciente", back_populates="contatos_emergencia")
