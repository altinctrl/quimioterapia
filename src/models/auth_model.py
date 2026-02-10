from sqlalchemy import Column, String, DateTime, func, JSON, ForeignKey
from sqlalchemy.orm import relationship

from src.resources.database import Base


class User(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    email = Column(String, nullable=True)
    display_name = Column(String, nullable=True)
    groups = Column(JSON, default=[])
    role = Column(String)
    registro_profissional = Column(String, nullable=True)
    tipo_registro = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    refresh_tokens = relationship("RefreshToken", back_populates="usuario", cascade="all, delete-orphan")
    profissional_equipe = relationship("Profissional", uselist=False, back_populates="usuario",
                                       cascade="all, delete-orphan")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token = Column(String, primary_key=True)
    username = Column(String, ForeignKey("users.username"), nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    usuario = relationship("User", back_populates="refresh_tokens")
