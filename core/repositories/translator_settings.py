from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, NoResultFound

from .base import BaseRepository
from ..db_helper import db_helper
from ..models.translator_settings import TranslatorSettings


class TranslatorSettingsRepository(BaseRepository):
    def __init__(self):
        super().__init__(model=TranslatorSettings)

    async def get_setting(self, setting_name):
        async with self.db() as session:
            try:
                query = select(self.model).filter_by(setting_name=setting_name)
                result = await session.execute(query)
                return result.scalars().one()
            except NoResultFound:
                return None

    async def set_setting(self, setting_name, setting_value):
        async with self.db() as session:
            try:
                # Попробуем обновить существующую настройку
                stmt = (
                    update(self.model)
                    .filter_by(setting_name=setting_name)
                    .values(setting_value=setting_value)
                )
                result = await session.execute(stmt)
                
                # Если строка не была обновлена, создаем новую
                if result.rowcount == 0:
                    new_setting = self.model(setting_name=setting_name, setting_value=setting_value)
                    session.add(new_setting)
                
                await session.commit()
                return True
            except SQLAlchemyError as e:
                await session.rollback()
                raise e

    async def get_current_translator(self):
        setting = await self.get_setting("current_translator")
        if setting:
            return setting.setting_value
        # По умолчанию используем deepl
        await self.set_setting("current_translator", "deepl")
        return "deepl"

    async def set_current_translator(self, translator_name):
        return await self.set_setting("current_translator", translator_name)


translator_settings_repo = TranslatorSettingsRepository()