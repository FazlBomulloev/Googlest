from sqlalchemy import update, select
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from .base import BaseRepository
from ..db_helper import db_helper
from ..models.channel import Channel


class ChannelRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=Channel)

    async def update_watermark(self, item_id):
        async with self.db() as session:
            current_value = await session.execute(select(self.model).filter_by(id=int(item_id)))
            current_value = current_value.scalars().first()
            if current_value is None:
                raise ValueError(f"Channel with id {item_id} not found")
            new_value = not current_value.watermark
            try:
                stmt = (
                    update(self.model)
                    .filter_by(id=int(item_id))
                    .values(watermark=new_value)
                )
                await session.execute(stmt)
                await session.commit()
                return stmt
            except SQLAlchemyError as e:
                return e

    async def get_by_channel_id(self, channel_id):
        async with self.db() as session:
            try:
                query = select(self.model).filter_by(channel_id=channel_id)
                admin = await session.execute(query)
                result = admin.scalars().first()
                return result
            except NoResultFound:
                return None


channel_repo = ChannelRepository()
