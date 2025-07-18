from sqlalchemy import update, select
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from .base import BaseRepository
from ..db_helper import db_helper
from ..models.admin import Admin


class AdminRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=Admin)

    async def get_by_userid(self, user_id):
        async with self.db() as session:
            try:
                query = select(self.model).filter_by(user_id=str(user_id))
                admin = await session.execute(query)
                result = admin.scalars().one()
                return result
            except NoResultFound:
                return None
    async def update_admin(self, admin_id, col):
        async with self.db() as session:
            # Получаем текущее значение из столбца `col`
            result = await session.execute(select(getattr(self.model, col)).filter_by(id=int(admin_id)))
            current_value = result.scalar_one_or_none()

            # Инвертируем значение
            new_value = not current_value if current_value is not None else True

            # Обновляем значение в базе данных
            stmt = (
                update(self.model)
                .filter_by(id=int(admin_id))
                .values({col: new_value})
            )

            await session.execute(stmt)
            await session.commit()



admin_repo = AdminRepository()