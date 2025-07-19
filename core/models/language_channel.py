from sqlalchemy import String, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base


class LanguageChannel(Base):
    __tablename__ = "language_channels"

    language_id: Mapped[int] = mapped_column(ForeignKey("mistral_languages.id"), nullable=False)
    channel_id: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now())

    # Связи
    language = relationship("MistralLanguage", back_populates="language_channels")

    def __repr__(self):
        return f'Language ID: {self.language_id}, Channel: {self.channel_id}'