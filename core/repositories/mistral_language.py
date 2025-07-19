from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from sqlalchemy.orm import selectinload

from .base import BaseRepository
from ..db_helper import db_helper
from ..models.mistral_language import MistralLanguage
from ..models.language_channel import LanguageChannel


class MistralLanguageRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=MistralLanguage)

    async def get_by_name(self, name: str):
        async with self.db() as session:
            try:
                query = select(self.model).filter_by(name=name)
                result = await session.execute(query)
                return result.scalars().one()
            except NoResultFound:
                return None

    async def get_with_channels(self, language_id: int):
        """Получить язык с привязанными каналами"""
        async with self.db() as session:
            try:
                query = (
                    select(self.model)
                    .options(selectinload(self.model.language_channels))
                    .filter_by(id=language_id)
                )
                result = await session.execute(query)
                return result.scalars().one()
            except NoResultFound:
                return None

    async def update_api_key(self, language_id: int, api_key: str):
        async with self.db() as session:
            try:
                stmt = (
                    update(self.model)
                    .filter_by(id=language_id)
                    .values(api_key=api_key)
                )
                await session.execute(stmt)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def update_agent_id(self, language_id: int, agent_id: str):
        async with self.db() as session:
            try:
                stmt = (
                    update(self.model)
                    .filter_by(id=language_id)
                    .values(agent_id=agent_id)
                )
                await session.execute(stmt)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def update_status(self, language_id: int, status: bool):
        async with self.db() as session:
            try:
                stmt = (
                    update(self.model)
                    .filter_by(id=language_id)
                    .values(status=status)
                )
                await session.execute(stmt)
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def get_by_channel_id(self, channel_id: str):
        """Получить язык по ID канала"""
        async with self.db() as session:
            try:
                query = (
                    select(self.model)
                    .join(LanguageChannel)
                    .filter(LanguageChannel.channel_id == channel_id)
                )
                result = await session.execute(query)
                return result.scalars().first()
            except NoResultFound:
                return None


mistral_language_repo = MistralLanguageRepository()