from aiogram_dialog import Dialog

from dialogs.windows import *

all_dialogs = [
    Dialog(
        # Основные окна
        home_page,
        
        # Каналы
        channels,
        add_channel,
        del_channel,
        watermark_channel,
        
        # Админы
        admins,
        add_admin,
        del_admin,
        change_admin,
        
        # Токены DeepL
        add_token,
        del_token,
        statistic,
        
        # Удаление сообщений
        del_mess,
        
        # Настройки переводчика
        translator_settings,
        
        # Mistral старые настройки
        mistral_settings,
        mistral_add_api_key,
        mistral_add_agent_id,
        mistral_view_tokens,
        mistral_delete_token,
        mistral_edit_token,
        
        # Новые окна языков Mistral
        mistral_languages,
        mistral_language_view,
        mistral_add_language_name,
        mistral_add_language_key,
        mistral_add_language_agent,
        mistral_add_language_channel,
        mistral_edit_api_key,
        mistral_edit_agent_id,
        mistral_add_channel_to_lang,
        mistral_remove_channel_from_lang,
        mistral_delete_language,
    ),
]