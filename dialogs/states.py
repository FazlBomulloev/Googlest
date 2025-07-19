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
    
    # Translator settings
    translator_settings = State()
    
    # Mistral settings
    mistral_settings = State()
    mistral_add_api_key = State()
    mistral_add_agent_id = State()
    mistral_view_tokens = State()
    mistral_delete_token = State()
    mistral_edit_token = State()
    
    # Mistral Languages - новые состояния
    mistral_languages = State()                    # Список языков
    mistral_language_view = State()               # Просмотр конкретного языка
    mistral_add_language_name = State()           # Ввод названия языка
    mistral_add_language_key = State()            # Ввод API key
    mistral_add_language_agent = State()          # Ввод Agent ID
    mistral_add_language_channel = State()        # Выбор канала для нового языка
    mistral_edit_api_key = State()                # Редактирование API key
    mistral_edit_agent_id = State()               # Редактирование Agent ID
    mistral_add_channel_to_lang = State()         # Добавить канал к языку
    mistral_remove_channel_from_lang = State()    # Удалить канал из языка
    mistral_delete_language = State()             # Удаление языка