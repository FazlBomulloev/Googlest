import io
from typing import Any

from aiogram.types import (
    Message,
    CallbackQuery,
    InputFile,
    BufferedInputFile,
    FSInputFile,
)
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from core.repositories.admin import admin_repo
from core.repositories.channel import channel_repo
from core.repositories.message import message_repo
from core.repositories.token import token_repo
from core.repositories.mistral_token import mistral_token_repo
from core.repositories.translator_settings import translator_settings_repo
from dialogs.getters import admin_only
from dialogs.states import Wizard
from utils.translator import translate


async def add_channel(
    message: Message, widget: Any, dialog_manager: DialogManager, data
):
    channel_info = dialog_manager.find("channel_add_info").get_value()
    channel_info = channel_info.split(",")
    text_disc = await translate("Доступ к дискуссии", channel_info[0].split(" ")[1])
    text_inv = await translate("Подписаться на канал", channel_info[0].split(" ")[1])
    await channel_repo.create(
        channel_id=channel_info[0].split(" ")[0],
        channel_name=channel_info[1],
        language=channel_info[0].split(" ")[1],
        link_discussion=channel_info[2].strip(),
        link_invitation=channel_info[3].strip(),
        text_discussion=text_disc,
        text_invitation=text_inv,
    )
    await dialog_manager.switch_to(state=Wizard.channels)


async def del_channel(
    message: Message, widget: Any, dialog_manager: DialogManager, data
):
    channel_del_id = dialog_manager.find("channel_del_id").get_value()
    await channel_repo.del_by_id(channel_del_id)
    await dialog_manager.switch_to(state=Wizard.del_channel)


async def update_watermark(
    message: Message, widget: Any, dialog_manager: DialogManager, data
):
    channel_wm_id = dialog_manager.find("change_watermark_id").get_value()
    await channel_repo.update_watermark(channel_wm_id)
    await dialog_manager.switch_to(state=Wizard.watermark_channel)


""" ADMINS """


async def add_admin(message: Message, widget: Any, dialog_manager: DialogManager, data):
    admin_info = dialog_manager.find("admin_add_info").get_value()
    await admin_repo.create(
        user_id=admin_info,
    )
    await dialog_manager.switch_to(state=Wizard.admins)


async def del_admin(message: Message, widget: Any, dialog_manager: DialogManager, data):
    admin_del_id = dialog_manager.find("admin_del_id").get_value()
    await admin_repo.del_by_id(admin_del_id)
    await dialog_manager.switch_to(state=Wizard.admins)


async def change_admin(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager
):
    admin_id = dialog_manager.find("change_admin_id").get_value()
    if widget.widget_id == "Del_mess":
        await admin_repo.update_admin(admin_id, "delete_message")
    elif widget.widget_id == "Change_token":
        await admin_repo.update_admin(admin_id, "change_token")
    elif widget.widget_id == "Change_channel":
        await admin_repo.update_admin(admin_id, "change_channel")


"""TOKENS"""


async def add_token(message: Message, widget: Any, dialog_manager: DialogManager, data):
    token = dialog_manager.find("token_deepl_add").get_value()
    await token_repo.create(token=token)


async def del_token(message: Message, widget: Any, dialog_manager: DialogManager, data):
    token_id = dialog_manager.find("id_token_deepl_del").get_value()
    await token_repo.del_token_by_id(token_id)


async def downl_tokens(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager
):
    mess = ""
    tokens = await token_repo.get_all()
    file = io.BytesIO()

    for i in tokens:
        mess += f"{i.id}. {i.token}\n"

    # Преобразуем строку в байты и записываем в BytesIO
    file.write(mess.encode("utf-8"))
    file.seek(0)

    await dialog_manager.event.bot.send_document(
        callback.from_user.id,
        document=BufferedInputFile(file.read(), "tokens.txt"),
    )
    await dialog_manager.switch_to(
        state=Wizard.add_token, show_mode=ShowMode.DELETE_AND_SEND
    )


"""DEL MESS"""


async def del_message(
    message: Message, widget: Any, dialog_manager: DialogManager, data
):
    message_id = dialog_manager.find("del_mess_id").get_value()
    mess = await message_repo.del_mess_by_id(message_id)
    if mess:
        for i in mess:
            if "," in i.message_id:
                mess_ids = i.message_id.split(",")
                if type(mess_ids) is list:
                    mess_ids.remove("")
                    for f in mess_ids:
                        await message.bot.delete_message(i.channel_id, f)
            else:
                await message.bot.delete_message(i.channel_id, i.message_id)
        await message.reply(f"Сообщение с id: {message_id} удалено")


"""TRANSLATOR"""


async def change_translator(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager
):
    current_translator = await translator_settings_repo.get_current_translator()
    new_translator = "mistral" if current_translator == "deepl" else "deepl"
    await translator_settings_repo.set_current_translator(new_translator)
    
    await callback.answer(f"Изменено на {new_translator.upper()}", show_alert=True)
    await dialog_manager.switch_to(state=Wizard.translator_settings)


"""MISTRAL TOKENS"""


async def add_mistral_api_key(
    message: Message, widget: Any, dialog_manager: DialogManager, data
):
    api_key = dialog_manager.find("mistral_api_key_input").get_value()
    dialog_manager.dialog_data["temp_api_key"] = api_key
    await dialog_manager.switch_to(state=Wizard.mistral_add_agent_id)


async def add_mistral_agent_id(
    message: Message, widget: Any, dialog_manager: DialogManager, data
):
    agent_id = dialog_manager.find("mistral_agent_id_input").get_value()
    api_key = dialog_manager.dialog_data.get("temp_api_key")
    
    if api_key:
        await mistral_token_repo.create(
            api_key=api_key,
            agent_id=agent_id,
            status=True
        )
        dialog_manager.dialog_data.pop("temp_api_key", None)
        await dialog_manager.switch_to(state=Wizard.mistral_settings)
    else:
        await message.reply("Ошибка: API ключ не найден")


async def del_mistral_token(
    message: Message, widget: Any, dialog_manager: DialogManager, data
):
    token_id = dialog_manager.find("mistral_token_del_id").get_value()
    token = await mistral_token_repo.get_by_id(int(token_id))
    if token:
        await mistral_token_repo.del_token_by_id(token_id)
        await message.reply(f"API key {token.api_key[:8]}... был удален")
    await dialog_manager.switch_to(state=Wizard.mistral_view_tokens)


async def edit_mistral_agent_id(
    message: Message, widget: Any, dialog_manager: DialogManager, data
):
    # Простая реализация - пользователь вводит "ID_токена новый_agent_id"
    input_text = dialog_manager.find("mistral_agent_id_edit").get_value()
    try:
        parts = input_text.split(" ", 1)
        if len(parts) == 2:
            token_id, new_agent_id = parts
            token = await mistral_token_repo.get_by_id(int(token_id))
            if token:
                await mistral_token_repo.update_agent_id(token.api_key, new_agent_id)
                await message.reply("ID агента изменен")
            else:
                await message.reply("Токен не найден")
        else:
            await message.reply("Формат: ID_токена новый_agent_id")
    except Exception as e:
        await message.reply(f"Ошибка: {str(e)}")
    
    await dialog_manager.switch_to(state=Wizard.mistral_view_tokens)