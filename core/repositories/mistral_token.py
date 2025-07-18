from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from .base import BaseRepository
from ..db_helper import db_helper
from ..models.mistral_token import MistralToken


class MistralTokenRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=MistralToken)

    async def update_time(self, api_key, time=None):
        async with self.db() as session:
            try:
                stmt = (
                    update(self.model)
                    .filter_by(api_key=api_key)
                    .values(time=time)
                )
                await session.execute(stmt)
                await session.commit()
                return stmt
            except SQLAlchemyError as e:
                return e

    async def update_status(self, api_key, status):
        async with self.db() as session:
            try:
                stmt = (
                    update(self.model)
                    .filter_by(api_key=api_key)
                    .values(status=status)
                )
                await session.execute(stmt)
                await session.commit()
                return stmt
            except SQLAlchemyError as e:
                return e

    async def get_by_api_key(self, api_key):
        async with self.db() as session:
            try:
                query = select(self.model).filter_by(api_key=api_key)
                result = await session.execute(query)
                return result.scalars().one()
            except NoResultFound:
                return None

    async def del_token(self, api_key):
        async with self.db() as session:
            await session.execute(delete(self.model).filter_by(api_key=api_key))
            await session.commit()
            return True

    async def del_token_by_id(self, token_id):
        async with self.db() as session:
            await session.execute(delete(self.model).filter_by(id=int(token_id)))
            await session.commit()
            return True

    async def update_agent_id(self, api_key, agent_id):
        async with self.db() as session:
            try:
                stmt = (
                    update(self.model)
                    .filter_by(api_key=api_key)
                    .values(agent_id=agent_id)
                )
                await session.execute(stmt)
                await session.commit()
                return stmt
            except SQLAlchemyError as e:
                return e


mistral_token_repo = MistralTokenRepository()