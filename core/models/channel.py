from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Channel(Base):
    __tablename__ = "channels"

    channel_id: Mapped[str] = mapped_column(String, nullable=False)
    channel_name: Mapped[str] = mapped_column(String, nullable=False)
    language: Mapped[str] = mapped_column(String, nullable=False)
    link_discussion: Mapped[str] = mapped_column(String, nullable=False)
    link_invitation: Mapped[str] = mapped_column(String, nullable=False)
    watermark: Mapped[bool] = mapped_column(Boolean, default=False)
    text_discussion: Mapped[str] = mapped_column(String, nullable=False)
    text_invitation: Mapped[str] = mapped_column(String, nullable=False)
