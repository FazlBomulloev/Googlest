from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class TranslatorSettings(Base):
    __tablename__ = "translator_settings"

    setting_name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    setting_value: Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        return f'Setting: {self.setting_name} = {self.setting_value}'