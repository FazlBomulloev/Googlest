from aiogram.fsm.state import StatesGroup, State


class Wizard(StatesGroup):
    home_page = State()

    channels = State()
    add_channel = State()
    del_channel = State()
    watermark_channel = State()

    admins = State()
    add_admin = State()
    del_admin = State()
    update_admin = State()

    add_token = State()
    del_token = State()
    statistic = State()

    del_mess = State()
