import asyncio

from aiogram_dialog import setup_dialogs


from aiogram import Dispatcher, Bot

from core.config import settings

from aiogram.fsm.storage.memory import MemoryStorage

from dialogs import all_dialogs
from routers.main_menu import menu_router

from utils.translator import check_deepl, check_mistral


storage = MemoryStorage()


dp = Dispatcher(storage=storage)
bot = Bot(token=settings.ADMIN_BOT)

setup_dialogs(dp)

dp.include_routers(menu_router)

dp.include_routers(*all_dialogs)


async def main():
    await asyncio.gather(
        dp.start_polling(bot),
        check_deepl(),
        check_mistral(),
    )

if __name__ == "__main__":
    asyncio.run(main())