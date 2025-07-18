from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Admin(Base):
    __tablename__ = "admins"

    user_id: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    delete_message: Mapped[bool] = mapped_column(Boolean, default=False)
    change_token: Mapped[bool] = mapped_column(Boolean, default=False)
    change_channel: Mapped[bool] = mapped_column(Boolean, default=False)

    def __repr__(self):
        return f'User_id: {self.user_id}, Delete_message: {self.delete_message}, Change_token: {self.change_token}, Change_channel: {self.change_channel}'
