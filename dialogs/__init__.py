from aiogram_dialog import Dialog

from dialogs.windows import *

all_dialogs = [
    Dialog(
        home_page,
        channels,
        add_channel,
        del_channel,
        watermark_channel,
        admins,
        add_admin,
        del_admin,
        change_admin,
        add_token,
        del_mess,
        statistic,
        del_token,
        translator_settings,
        mistral_settings,
        mistral_add_api_key,
        mistral_add_agent_id,
        mistral_view_tokens,
        mistral_delete_token,
        mistral_edit_token,
    ),
]