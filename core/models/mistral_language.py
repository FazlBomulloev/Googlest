from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base


class MistralLanguage(Base):
    __tablename__ = "mistral_languages"

    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    api_key: Mapped[str] = mapped_column(String, nullable=False)
    agent_id: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    # Связь с каналами через промежуточную таблицу
    language_channels = relationship("LanguageChannel", back_populates="language", cascade="all, delete-orphan")

    def __repr__(self):
        return f'Language: {self.name}, Agent: {self.agent_id[:20]}..., Status: {self.status}'