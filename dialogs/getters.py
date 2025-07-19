import asyncio
from functools import wraps
from typing import Any

from aiogram_dialog import DialogManager
from aiogram import types
from aiogram_dialog.widgets.common import Whenable
from sqlalchemy.util import await_only

from core.repositories.admin import admin_repo
from core.repositories.channel import channel_repo
from core.repositories.token import token_repo
from core.repositories.mistral_token import mistral_token_repo
from core.repositories.translator_settings import translator_settings_repo
from core.repositories.mistral_language import mistral_language_repo
from core.repositories.language_channel import language_channel_repo

ADMIN_USER_IDS = [6640814090, 817411344, 1097958911]


def check_admin_rights(admin, user_id, rights=None):
    # admin = await admin_repo.get_by_userid(user_id)
    if user_id in ADMIN_USER_IDS:
        return True
    if rights == "channels":
        return admin.change_channel
    if rights == "del_mess":
        return admin.delete_message
    if rights == "tokens":
        return admin.change_token


def admin_only(
    data: dict,
    widget: Any,
    dialog_manager: DialogManager,
):
    user_id = dialog_manager.event.from_user.id
    if not check_admin_rights(
        dialog_manager.dialog_data["admin"], user_id, widget.widget_id
    ):
        # await dialog_manager.event.answer(
        #     "У вас нет прав администратора.", show_alert=True
        # )
        return False
    return check_admin_rights(
        dialog_manager.dialog_data["admin"], user_id, widget.widget_id
    )


async def get_home_page(dialog_manager: DialogManager, **middleware_data):
    admin = await admin_repo.get_by_userid(dialog_manager.event.from_user.id)
    dialog_manager.dialog_data["admin"] = admin
    return {"admin": admin}


async def get_channels(dialog_manager: DialogManager, **middleware_data):
    channels = await channel_repo.get_all()
    list_channel = []

    for channel in channels:
        list_channel.append(
            (
                channel.id,
                channel.channel_name,
                "Yes" if channel.watermark == True else "No",
            )
        )
    return {"items": list_channel}


async def get_admins(dialog_manager: DialogManager, **middleware_data):
    admins = await admin_repo.get_all()
    list_admins = []

    for admin in admins:
        list_admins.append((admin.id, admin.user_id, admin.change_token))
    return {"items": list_admins}


async def get_admins_update(dialog_manager: DialogManager, **middleware_data):
    admin_id = dialog_manager.find("change_admin_id").get_value()
    admin = await admin_repo.get_by_id(int(admin_id))
    return {"items": admin}


async def get_tokens(dialog_manager: DialogManager, **middleware_data):
    tokens = await token_repo.get_all()
    on = 0
    off = 0
    for token in tokens:
        if token.status:
            on += 1
        else:
            off += 1

    return {"on": on, "off": off}


async def get_current_translator(dialog_manager: DialogManager, **middleware_data):
    current_translator = await translator_settings_repo.get_current_translator()
    return {"current_translator": current_translator}


async def get_mistral_tokens(dialog_manager: DialogManager, **middleware_data):
    tokens = await mistral_token_repo.get_all()
    list_tokens = []

    for token in tokens:
        list_tokens.append(
            (
                token.id,
                f"{token.api_key[:8]}...",
                token.agent_id,
                "Active" if token.status else "Blocked",
            )
        )
    return {"items": list_tokens}


async def get_mistral_token_for_edit(dialog_manager: DialogManager, **middleware_data):
    token_id = dialog_manager.find("mistral_token_id").get_value()
    if token_id:
        token = await mistral_token_repo.get_by_id(int(token_id))
        return {"token": token}
    return {"token": None}


# ========== НОВЫЕ ГЕТТЕРЫ ДЛЯ ЯЗЫКОВ ==========

async def get_mistral_languages(dialog_manager: DialogManager, **middleware_data):
    """Получить список всех языков Mistral"""
    languages = await mistral_language_repo.get_all()
    list_languages = []

    for language in languages:
        list_languages.append(
            (
                language.id,
                language.name,
                "✅" if language.status else "❌",
            )
        )
    return {"items": list_languages}


async def get_mistral_language_view(dialog_manager: DialogManager, **middleware_data):
    """Получить детальную информацию о языке"""
    # Получаем language_id из dialog_data, а не из виджета
    language_id = dialog_manager.dialog_data.get("language_id")
    if not language_id:
        return {"language": None, "channels": []}

    # Получаем язык
    language = await mistral_language_repo.get_by_id(int(language_id))
    if not language:
        return {"language": None, "channels": []}

    # Получаем каналы для этого языка
    channels = await language_channel_repo.get_channels_by_language(int(language_id))
    
    channel_list = []
    for channel in channels:
        channel_list.append(
            (channel.id, channel.channel_name, channel.channel_id)
        )

    return {
        "language": language,
        "channels": channel_list,
        "api_key_short": f"{language.api_key[:8]}..." if language.api_key else "N/A",
        "agent_id_short": f"{language.agent_id[:20]}..." if language.agent_id else "N/A"
    }


async def get_unassigned_channels(dialog_manager: DialogManager, **middleware_data):
    """Получить каналы, не привязанные к языкам"""
    channels = await language_channel_repo.get_unassigned_channels()
    list_channels = []

    for channel in channels:
        list_channels.append(
            (channel.channel_id, channel.channel_name)
        )
    return {"items": list_channels}


async def get_language_channels_for_removal(dialog_manager: DialogManager, **middleware_data):
    """Получить каналы конкретного языка для удаления"""
    language_id = dialog_manager.dialog_data.get("language_id")
    if not language_id:
        return {"items": []}

    channels = await language_channel_repo.get_channels_by_language(int(language_id))
    list_channels = []

    for channel in channels:
        list_channels.append(
            (channel.channel_id, channel.channel_name)
        )
    return {"items": list_channels}


async def get_all_languages_for_deletion(dialog_manager: DialogManager, **middleware_data):
    """Получить все языки для удаления"""
    languages = await mistral_language_repo.get_all()
    list_languages = []

    for language in languages:
        list_languages.append(
            (language.id, language.name)
        )
    return {"items": list_languages}