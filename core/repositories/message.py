from sqlalchemy import update, select, delete
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from .base import BaseRepository
from ..db_helper import db_helper
from ..models.message import Message


class MessageRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=Message)

    async def del_mess_by_id(self, mess_id):
        async with self.db() as session:
            query = await session.execute(select(self.model).filter_by(main_message_id=str(mess_id)))
            await session.execute(delete(Message).filter_by(main_message_id=str(mess_id)))
            await session.commit()
            return query.scalars().all()

    async def get_by_id_all(self, item_id):
        async with self.db() as session:
            try:
                query = select(self.model).filter_by(main_message_id=str(item_id))
                admin = await session.execute(query)
                result = admin.scalars().all()
                return result
            except NoResultFound:
                return None

message_repo = MessageRepository()