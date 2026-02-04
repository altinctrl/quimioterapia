from sqlalchemy import Column, String, DateTime, func, JSON
from src.resources.database import Base

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token = Column(String, primary_key=True)
    username = Column(String, index=True, nullable=False)
    email = Column(String)
    display_name = Column(String)
    groups = Column(JSON, nullable=False)
    role = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
