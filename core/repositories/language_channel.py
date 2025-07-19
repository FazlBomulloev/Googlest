from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..db_helper import db_helper
from ..models.language_channel import LanguageChannel
from ..models.channel import Channel


class LanguageChannelRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=LanguageChannel)

    async def add_channel_to_language(self, language_id: int, channel_id: str):
        """Привязать канал к языку"""
        async with self.db() as session:
            try:
                # Проверяем, не существует ли уже такая связь
                existing = await session.execute(
                    select(self.model).filter_by(
                        language_id=language_id, 
                        channel_id=channel_id
                    )
                )
                if existing.scalars().first():
                    return False  # Связь уже существует

                new_link = self.model(
                    language_id=language_id,
                    channel_id=channel_id
                )
                session.add(new_link)
                await session.commit()
                await session.refresh(new_link)
                return new_link
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def remove_channel_from_language(self, language_id: int, channel_id: str):
        """Отвязать канал от языка"""
        async with self.db() as session:
            try:
                await session.execute(
                    delete(self.model).filter_by(
                        language_id=language_id,
                        channel_id=channel_id
                    )
                )
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def get_channels_by_language(self, language_id: int):
        """Получить все каналы для языка"""
        async with self.db() as session:
            try:
                query = (
                    select(Channel)
                    .join(self.model)
                    .filter(self.model.language_id == language_id)
                )
                result = await session.execute(query)
                return result.scalars().all()
            except NoResultFound:
                return []

    async def get_language_by_channel(self, channel_id: str):
        """Получить язык по ID канала"""
        async with self.db() as session:
            try:
                query = select(self.model).filter_by(channel_id=channel_id)
                result = await session.execute(query)
                return result.scalars().first()
            except NoResultFound:
                return None

    async def get_unassigned_channels(self):
        """Получить каналы, не привязанные ни к одному языку"""
        async with self.db() as session:
            try:
                # Подзапрос для получения всех привязанных каналов
                assigned_channels_subquery = select(self.model.channel_id).distinct()
                
                # Основной запрос - каналы, которых нет в подзапросе
                query = (
                    select(Channel)
                    .filter(~Channel.channel_id.in_(assigned_channels_subquery))
                )
                result = await session.execute(query)
                return result.scalars().all()
            except NoResultFound:
                return []


language_channel_repo = LanguageChannelRepository()