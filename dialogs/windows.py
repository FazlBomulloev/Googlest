import operator

from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    SwitchTo,
    Group,
    Row,
    Back,
    Url,
    ListGroup,
    Checkbox,
    Select,
    ScrollingGroup,
)
from aiogram_dialog.widgets.text import Const, Format, List

from dialogs.getters import (
    get_channels,
    get_admins,
    get_admins_update,
    admin_only,
    get_home_page,
    get_tokens,
    get_current_translator,
    get_mistral_tokens,
    get_mistral_languages,
    get_mistral_language_view,
    get_unassigned_channels,
    get_language_channels_for_removal,
    get_all_languages_for_deletion,
)
from dialogs.handlers import (
    add_channel,
    del_channel,
    update_watermark,
    add_admin,
    del_admin,
    change_admin,
    add_token,
    downl_tokens,
    del_message,
    del_token,
    change_translator,
    add_mistral_api_key,
    add_mistral_agent_id,
    del_mistral_token,
    edit_mistral_agent_id,
    view_language,
    add_language_name,
    add_language_key,
    add_language_agent,
    add_language_complete,
    edit_language_api_key,
    edit_language_agent_id,
    add_channel_to_language,
    remove_channel_from_language,
    delete_language,
)
from dialogs.states import Wizard

home_page = Window(
    Format("Hello"),
    SwitchTo(
        Const("Удалить сообщение"),
        id="del_mess",
        when=admin_only,
        state=Wizard.del_mess,
    ),
    Group(
        Row(
            SwitchTo(Const("Статистика"), id="statistics", state=Wizard.statistic),
            SwitchTo(
                Const("Токены"),
                id="tokens",
                state=Wizard.add_token,
                when=admin_only,
            ),
        ),
    ),
    Group(
        Row(
            SwitchTo(
                Const("Каналы"),
                id="channels",
                state=Wizard.channels,
                when=admin_only,
            ),
            SwitchTo(
                Const("Админы"),
                id="admins",
                state=Wizard.admins,
                when=admin_only,
            ),
        ),
    ),
    Group(
        Row(
            SwitchTo(
                Const("Изменить переводчик"),
                id="translator_settings",
                state=Wizard.translator_settings,
                when=admin_only,
            ),
            SwitchTo(
                Const("Настроить Mistral"),
                id="mistral_settings",
                state=Wizard.mistral_settings,
                when=admin_only,
            ),
        ),
    ),
    state=Wizard.home_page,
    getter=get_home_page,
    parse_mode="html",
)

"""УДАЛЕНИЕ СООБЩЕНИЙ"""

del_mess = Window(
    Const("Del mess for message_id"),
    TextInput(id="del_mess_id", on_success=del_message),
    SwitchTo(Const("Назад"), id="back_del_mess", state=Wizard.home_page),
    state=Wizard.del_mess,
)

"""РАБОТА С КАНАЛАМИ"""

channels = Window(
    Const("List_channel:\n"),
    List(
        Format("{item[0]} - {item[1]} | Watermark: {item[2]}"),
        items="items",
    ),
    Row(
        SwitchTo(Const("Добавить канал"), id="add_channel", state=Wizard.add_channel),
        SwitchTo(Const("Удалить канал"), id="del_channel", state=Wizard.del_channel),
    ),
    SwitchTo(
        Const("Водяной знак"), id="change_watermark", state=Wizard.watermark_channel
    ),
    SwitchTo(Const("Назад"), id="back_channel", state=Wizard.home_page),
    getter=get_channels,
    state=Wizard.channels,
    parse_mode="html",
)

add_channel = Window(
    Const(
        "Отправьте id канала\n"
        "(-1001111111, Псевдоним, Ссылка на обсуждение чата, Ссылка приглашения в канал)"
    ),
    TextInput(id="channel_add_info", on_success=add_channel),
    SwitchTo(Const("Назад"), id="back_channel", state=Wizard.channels),
    state=Wizard.add_channel,
    parse_mode="html",
)

del_channel = Window(
    Const("List_channel for del:\n"),
    List(
        Format("{item[0]} - {item[1]} | Watermark: {item[2]}"),
        items="items",
    ),
    TextInput(id="channel_del_id", on_success=del_channel),
    SwitchTo(Const("Назад"), id="back_channel", state=Wizard.channels),
    getter=get_channels,
    state=Wizard.del_channel,
    parse_mode="html",
)

watermark_channel = Window(
    Const("List_channel for watermark:\n"),
    List(
        Format("{item[0]} - {item[1]} | Watermark: {item[2]}"),
        items="items",
    ),
    TextInput(id="change_watermark_id", on_success=update_watermark),
    SwitchTo(Const("Назад"), id="back_channel", state=Wizard.channels),
    getter=get_channels,
    state=Wizard.watermark_channel,
    parse_mode="html",
)

"""РАБОТА С ТОКЕНАМИ"""

add_token = Window(
    Const("Add token for deepl"),
    TextInput(id="token_deepl_add", on_success=add_token),
    Button(Const("Скачать токены"), id="download_tokens", on_click=downl_tokens),
    SwitchTo(Const("Удалить токен"), id="del_token", state=Wizard.del_token),
    SwitchTo(Const("Назад"), id="home_page", state=Wizard.home_page),
    getter=get_channels,
    state=Wizard.add_token,
    parse_mode="html",
)

del_token = Window(
    Const("Отправьте id токена для удаления"),
    TextInput(id="id_token_deepl_del", on_success=del_token),
    SwitchTo(Const("Назад"), id="back_add_token", state=Wizard.add_token),
    state=Wizard.del_token,
)

statistic = Window(
    Format("Рабочих токенов - {on}\nТокены на удаление - {off}"),
    SwitchTo(Const("Назад"), id="home_page", state=Wizard.home_page),
    getter=get_tokens,
    state=Wizard.statistic,
)

"""РАБОТА С АДМИНАМИ"""

admins = Window(
    Const("List admins"),
    List(
        Format("{item[0]} - {item[1]}"),
        items="items",
    ),
    Row(
        SwitchTo(Const("Добавить админа"), id="add_admin", state=Wizard.add_admin),
        SwitchTo(Const("Удалить админа"), id="del_admin", state=Wizard.del_admin),
    ),
    TextInput(
        id="change_admin_id",
        on_success=SwitchTo(Const(""), state=Wizard.update_admin, id="upd_adm"),
    ),
    SwitchTo(Const("Назад"), id="back_admin", state=Wizard.home_page),
    getter=get_admins,
    state=Wizard.admins,
)

add_admin = Window(
    Const("Отправьте id пользователя"),
    TextInput(id="admin_add_info", on_success=add_admin),
    SwitchTo(Const("Назад"), id="back_admin", state=Wizard.admins),
    state=Wizard.add_admin,
    parse_mode="html",
)

del_admin = Window(
    Const("List_admins for del:\n"),
    List(
        Format("{item[0]} - {item[1]}"),
        items="items",
    ),
    TextInput(id="admin_del_id", on_success=del_admin),
    SwitchTo(Const("Назад"), id="back_admin", state=Wizard.admins),
    getter=get_admins,
    state=Wizard.del_admin,
    parse_mode="html",
)

change_admin = Window(
    Format("Update admin: {items.user_id}"),
    Format(
        "Del_mess: {items.delete_message}\nChange_token: {items.change_token}\nChange_channel: {items.change_channel}"
    ),
    Button(Const("Del_mess"), id="Del_mess", on_click=change_admin),
    Button(Const("Change_token"), id="Change_token", on_click=change_admin),
    Button(Const("Change_channel"), id="Change_channel", on_click=change_admin),
    SwitchTo(Const("Назад"), id="back_admin", state=Wizard.admins),
    getter=get_admins_update,
    state=Wizard.update_admin,
    parse_mode="html",
)

"""НАСТРОЙКИ ПЕРЕВОДЧИКА"""

translator_settings = Window(
    Format("Сейчас используется: {current_translator}"),
    Button(Const("Изменить"), id="change_translator", on_click=change_translator),
    SwitchTo(Const("Назад"), id="back_translator", state=Wizard.home_page),
    getter=get_current_translator,
    state=Wizard.translator_settings,
)

"""НАСТРОЙКИ MISTRAL"""

mistral_settings = Window(
    Const("Настройки Mistral"),
    SwitchTo(Const("Добавить API key"), id="add_mistral_api", state=Wizard.mistral_add_api_key),
    SwitchTo(Const("Посмотреть API key"), id="view_mistral_tokens", state=Wizard.mistral_view_tokens),
    SwitchTo(Const("🌍 Языки"), id="mistral_languages", state=Wizard.mistral_languages),
    SwitchTo(Const("Назад"), id="back_mistral", state=Wizard.home_page),
    state=Wizard.mistral_settings,
)

mistral_add_api_key = Window(
    Const("Добавьте ключ"),
    TextInput(id="mistral_api_key_input", on_success=add_mistral_api_key),
    SwitchTo(Const("Назад"), id="back_mistral_settings", state=Wizard.mistral_settings),
    state=Wizard.mistral_add_api_key,
)

mistral_add_agent_id = Window(
    Const("Добавьте id агента"),
    TextInput(id="mistral_agent_id_input", on_success=add_mistral_agent_id),
    SwitchTo(Const("Назад"), id="back_mistral_settings", state=Wizard.mistral_settings),
    state=Wizard.mistral_add_agent_id,
)

mistral_view_tokens = Window(
    Const("Список API ключей Mistral:\n"),
    List(
        Format("{item[0]} - {item[1]} | {item[2]} | {item[3]}"),
        items="items",
    ),
    SwitchTo(Const("Удалить токен"), id="del_mistral_token", state=Wizard.mistral_delete_token),
    SwitchTo(Const("Назад"), id="back_mistral_settings", state=Wizard.mistral_settings),
    getter=get_mistral_tokens,
    state=Wizard.mistral_view_tokens,
)

mistral_delete_token = Window(
    Const("Отправьте ID токена для удаления"),
    TextInput(id="mistral_token_del_id", on_success=del_mistral_token),
    SwitchTo(Const("Назад"), id="back_mistral_view", state=Wizard.mistral_view_tokens),
    state=Wizard.mistral_delete_token,
)

mistral_edit_token = Window(
    Const("Отправьте ID токена для изменения агента, затем новый ID агента"),
    TextInput(id="mistral_agent_id_edit", on_success=edit_mistral_agent_id),
    SwitchTo(Const("Назад"), id="back_mistral_view", state=Wizard.mistral_view_tokens),
    state=Wizard.mistral_edit_token,
)

# ========== НОВЫЕ ОКНА ДЛЯ ЯЗЫКОВ ==========

"""ЯЗЫКИ MISTRAL"""

mistral_languages = Window(
    Const("🌍 Языки Mistral\n"),
    List(
        Format("{item[1]} {item[2]}"),
        items="items",
    ),
    ScrollingGroup(
        Select(
            Format("{item[1]}"),
            items="items",
            item_id_getter=operator.itemgetter(0),
            id="language_select",
            on_click=view_language,
        ),
        width=2,
        height=6,
        id="languages_scroll",
    ),
    Row(
        SwitchTo(Const("➕ Добавить язык"), id="add_language", state=Wizard.mistral_add_language_name),
        SwitchTo(Const("❌ Удалить язык"), id="delete_language", state=Wizard.mistral_delete_language),
    ),
    SwitchTo(Const("🔙 Назад"), id="back_mistral_languages", state=Wizard.mistral_settings),
    getter=get_mistral_languages,
    state=Wizard.mistral_languages,
)

mistral_language_view = Window(
    Format("🇺🇳 {language.name}\n"),
    Format("📋 Список каналов:"),
    List(
        Format("• {item[1]} (@{item[2]})"),
        items="channels",
        when="channels",
    ),
    Const("📋 Каналов не привязано", when=lambda data, widget, manager: not data.get("channels")),
    Format("\n🔑 API Key: {api_key_short}"),
    Format("🤖 Agent ID: {agent_id_short}\n"),
    Row(
        SwitchTo(Const("➕ Добавить канал"), id="add_channel_lang", state=Wizard.mistral_add_channel_to_lang),
        SwitchTo(Const("❌ Удалить канал"), id="remove_channel_lang", state=Wizard.mistral_remove_channel_from_lang),
    ),
    Row(
        SwitchTo(Const("🔑 Изменить API key"), id="edit_api_key", state=Wizard.mistral_edit_api_key),
        SwitchTo(Const("🤖 Изменить Agent ID"), id="edit_agent_id", state=Wizard.mistral_edit_agent_id),
    ),
    SwitchTo(Const("🔙 Назад"), id="back_language_view", state=Wizard.mistral_languages),
    getter=get_mistral_language_view,
    state=Wizard.mistral_language_view,
)

mistral_add_language_name = Window(
    Const("📝 Введите название языка:"),
    Const("Например: Французский, Немецкий, Итальянский"),
    TextInput(id="language_name_input", on_success=add_language_name),
    SwitchTo(Const("🔙 Назад"), id="back_add_language", state=Wizard.mistral_languages),
    state=Wizard.mistral_add_language_name,
)

mistral_add_language_key = Window(
    Const("🔑 Введите API key:"),
    TextInput(id="language_key_input", on_success=add_language_key),
    SwitchTo(Const("🔙 Назад"), id="back_add_language_key", state=Wizard.mistral_add_language_name),
    state=Wizard.mistral_add_language_key,
)

mistral_add_language_agent = Window(
    Const("🤖 Введите Agent ID:"),
    Const("Например: ag:9885ec37:20250717:cheshskii:a70b740a"),
    TextInput(id="language_agent_input", on_success=add_language_agent),
    SwitchTo(Const("🔙 Назад"), id="back_add_language_agent", state=Wizard.mistral_add_language_key),
    state=Wizard.mistral_add_language_agent,
)

mistral_add_language_channel = Window(
    Const("📺 Выберите канал для языка:"),
    List(
        Format("• {item[1]}"),
        items="items",
        when="items",
    ),
    Const("❌ Нет доступных каналов", when=lambda data, widget, manager: not data.get("items")),
    ScrollingGroup(
        Select(
            Format("{item[1]}"),
            items="items",
            item_id_getter=operator.itemgetter(0),
            id="channel_select",
            on_click=add_language_complete,
        ),
        width=1,
        height=5,
        id="channels_scroll",
        when="items",
    ),
    SwitchTo(Const("🔙 Назад"), id="back_add_language_channel", state=Wizard.mistral_add_language_agent),
    getter=get_unassigned_channels,
    state=Wizard.mistral_add_language_channel,
)

mistral_edit_api_key = Window(
    Format("🔑 Текущий API key: {api_key_short}"),
    Const("Введите новый API key:"),
    TextInput(id="language_api_key_edit", on_success=edit_language_api_key),
    SwitchTo(Const("🔙 Назад"), id="back_edit_api_key", state=Wizard.mistral_language_view),
    getter=get_mistral_language_view,
    state=Wizard.mistral_edit_api_key,
)

mistral_edit_agent_id = Window(
    Format("🤖 Текущий Agent ID: {agent_id_short}"),
    Const("Введите новый Agent ID:"),
    TextInput(id="language_agent_id_edit", on_success=edit_language_agent_id),
    SwitchTo(Const("🔙 Назад"), id="back_edit_agent_id", state=Wizard.mistral_language_view),
    getter=get_mistral_language_view,
    state=Wizard.mistral_edit_agent_id,
)

mistral_add_channel_to_lang = Window(
    Const("➕ Добавить канал к языку"),
    Const("Выберите канал:"),
    List(
        Format("• {item[1]}"),
        items="items",
        when="items",
    ),
    Const("❌ Нет доступных каналов", when=lambda data, widget, manager: not data.get("items")),
    ScrollingGroup(
        Select(
            Format("{item[1]}"),
            items="items",
            item_id_getter=operator.itemgetter(0),
            id="add_channel_select",
            on_click=add_channel_to_language,
        ),
        width=1,
        height=5,
        id="add_channels_scroll",
        when="items",
    ),
    SwitchTo(Const("🔙 Назад"), id="back_add_channel_to_lang", state=Wizard.mistral_language_view),
    getter=get_unassigned_channels,
    state=Wizard.mistral_add_channel_to_lang,
)

mistral_remove_channel_from_lang = Window(
    Const("❌ Удалить канал из языка"),
    Const("Выберите канал для удаления:"),
    List(
        Format("• {item[1]}"),
        items="items",
        when="items",
    ),
    Const("❌ Нет привязанных каналов", when=lambda data, widget, manager: not data.get("items")),
    ScrollingGroup(
        Select(
            Format("{item[1]}"),
            items="items",
            item_id_getter=operator.itemgetter(0),
            id="remove_channel_select",
            on_click=remove_channel_from_language,
        ),
        width=1,
        height=5,
        id="remove_channels_scroll",
        when="items",
    ),
    SwitchTo(Const("🔙 Назад"), id="back_remove_channel_from_lang", state=Wizard.mistral_language_view),
    getter=get_language_channels_for_removal,
    state=Wizard.mistral_remove_channel_from_lang,
)

mistral_delete_language = Window(
    Const("❌ Удаление языка"),
    Const("⚠️ ВНИМАНИЕ: Это действие нельзя отменить!"),
    Const("Выберите язык для удаления:"),
    List(
        Format("• {item[1]}"),
        items="items",
        when="items",
    ),
    ScrollingGroup(
        Select(
            Format("🗑️ {item[1]}"),
            items="items",
            item_id_getter=operator.itemgetter(0),
            id="delete_language_select",
            on_click=delete_language,
        ),
        width=1,
        height=5,
        id="delete_languages_scroll",
        when="items",
    ),
    SwitchTo(Const("🔙 Назад"), id="back_delete_language", state=Wizard.mistral_languages),
    getter=get_all_languages_for_deletion,
    state=Wizard.mistral_delete_language,
)