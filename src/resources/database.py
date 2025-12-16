import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

APP_DB_URL = os.getenv("APP_DB_URL", "postgresql+asyncpg://user:password@localhost/db_quimio")
AGHU_DB_URL = os.getenv("AGHU_DB_URL", "postgresql+asyncpg://user:password@localhost/db_aghu")

app_engine = create_async_engine(APP_DB_URL, echo=False)
aghu_engine = create_async_engine(AGHU_DB_URL, echo=False)

AppSessionLocal = async_sessionmaker(
    bind=app_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

AghuSessionLocal = async_sessionmaker(
    bind=aghu_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

Base = declarative_base()


async def get_app_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AppSessionLocal() as session:
        yield session


async def get_aghu_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AghuSessionLocal() as session:
        yield session
