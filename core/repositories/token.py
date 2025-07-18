from sqlalchemy import select, update, delete
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from .base import BaseRepository
from ..db_helper import db_helper
from ..models.token import Token


class TokenRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=Token)

    async def update_time(self, token, time=None):
        async with self.db() as session:
            try:
                stmt = (
                    update(self.model)
                    .filter_by(token=token)
                    .values(time=time)
                )
                await session.execute(stmt)
                await session.commit()
                return stmt
            except SQLAlchemyError as e:
                return e

    async def update_status(self, token, status):
        async with self.db() as session:
            try:
                stmt = (
                    update(self.model)
                    .filter_by(token=token)
                    .values(status=status)
                )
                await session.execute(stmt)
                await session.commit()
                return stmt
            except SQLAlchemyError as e:
                return e

    async def get_time_by_token(self, token):
        async with self.db() as session:
            try:
                query = select(self.model).filter_by(token=token)
                admin = await session.execute(query)
                result = admin.scalars().one()
                return result
            except NoResultFound:
                return None

    async def del_token(self, token):
        async with self.db() as session:
            await session.execute(delete(self.model).filter_by(token=token))
            await session.commit()
            return True

    async def del_token_by_id(self, token_id):
        async with self.db() as session:
            await session.execute(delete(self.model).filter_by(id=int(token_id)))
            await session.commit()
            return True


token_repo = TokenRepository()