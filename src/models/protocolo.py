from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.resources.database import Base


class Protocolo(Base):
    __tablename__ = "protocolos"

    id = Column(String, primary_key=True)
    nome = Column(String, nullable=False, index=True)
    descricao = Column(String, nullable=True)
    indicacao = Column(String, nullable=True)
    duracao = Column(Integer, nullable=False)
    frequencia = Column(String)
    numero_ciclos = Column(Integer)
    grupo_infusao = Column(String)

    dias_semana_permitidos = Column(JSON, nullable=True)
    observacoes = Column(Text, nullable=True)
    precaucoes = Column(Text, nullable=True)
    ativo = Column(Boolean, default=True)

    itens = relationship("ItemProtocolo", back_populates="protocolo", cascade="all, delete-orphan")


class ItemProtocolo(Base):
    __tablename__ = "itens_protocolo"

    id = Column(Integer, primary_key=True, index=True)
    protocolo_id = Column(String, ForeignKey("protocolos.id"))

    tipo = Column(String, nullable=False)
    nome = Column(String, nullable=False)
    dose_padrao = Column(String)
    unidade_padrao = Column(String)
    via_padrao = Column(String)

    protocolo = relationship("Protocolo", back_populates="itens")
