from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class MistralToken(Base):
    __tablename__ = "mistral_tokens"

    api_key: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    agent_id: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    time: Mapped[str] = mapped_column(String, nullable=True)

    def __repr__(self):
        return f'API Key: {self.api_key[:8]}..., Agent ID: {self.agent_id}, Status: {self.status}'