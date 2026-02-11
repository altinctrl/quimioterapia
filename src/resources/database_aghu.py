import os
from typing import AsyncGenerator

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

load_dotenv()

AGHU_DB_URL = os.getenv("AGHU_DB_URL")

aghu_engine = create_async_engine(AGHU_DB_URL, echo=False)

AghuSessionLocal = async_sessionmaker(
    bind=aghu_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

AghuBase = declarative_base()


async def get_aghu_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AghuSessionLocal() as session:
        yield session
