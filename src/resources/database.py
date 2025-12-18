import json
from typing import AsyncGenerator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

try:
    from src.models.paciente import Paciente, ContatoEmergencia
    from src.models.protocolo import Protocolo, ItemProtocolo
    from src.models.agendamento import Agendamento
    from src.models.prescricao import Prescricao, ItemPrescricao
    from src.models.configuracao import Configuracao
except ImportError:
    pass

class DatabaseManager:
    """
    Manages asynchronous database connections and sessions for a specific DSN.
    """
    def __init__(self, dsn: str):
        self.engine: AsyncEngine = create_async_engine(dsn, json_serializer=lambda obj: json.dumps(obj, ensure_ascii=False), echo=False) # Set echo=False to reduce log verbosity
        self.async_session_maker = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Provides an asynchronous session for database operations.
        """
        async with self.async_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    async def close_connection(self):
        """
        Closes all connections in the engine's connection pool.
        """
        await self.engine.dispose()

async def get_aghu_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get an AGHU database session from the app state.
    """
    aghu_db_manager: DatabaseManager = request.app.state.aghu_db
    async for session in aghu_db_manager.get_session():
        yield session

async def get_app_db_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for FastAPI to get an application database session (SQLite) from the app state.
    """
    app_db_manager: DatabaseManager = request.app.state.app_db
    async for session in app_db_manager.get_session():
        yield session