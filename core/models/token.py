from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Token(Base):
    __tablename__ = "tokens"

    token:Mapped[str] = mapped_column(String, nullable=False, unique=True)
    status: Mapped[bool] = mapped_column(Boolean, default=True)
    time: Mapped[str] = mapped_column(String, nullable=True)
