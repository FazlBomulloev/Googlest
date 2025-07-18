from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from core.db_helper import db_helper


class BaseRepository:
    def __init__(self, model, db=db_helper.session_getter):
        self.db = db
        self.model = model

    async def create(self, **kwargs):
        async with self.db() as session:
            try:
                new_instance = self.model(**kwargs)
                session.add(new_instance)
                await session.commit()
                await session.refresh(new_instance)
                return new_instance
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def get_all(self):
        async with self.db() as session:
            query = (await session.execute(select(self.model))).scalars().all()
            return query

    async def get_by_id(self, item_id):
        async with self.db() as session:
            try:
                query = select(self.model).filter_by(id=item_id)
                admin = await session.execute(query)
                result = admin.scalars().one()
                return result
            except NoResultFound:
                return None

    async def del_by_id(self, item_id):
        async with self.db() as session:
            try:
                await session.execute(
                    delete(self.model).where(self.model.id == int(item_id))
                )
                await session.commit()
            except SQLAlchemyError as e:
                await session.rollback()
                raise e
