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

ADMIN_USER_IDS = [6640814090, 817411344]


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
                channel.language,
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
