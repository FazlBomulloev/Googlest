import asyncio
import os
from concurrent.futures import ProcessPoolExecutor
from typing import List

from aiogram import Router, Bot, F
from aiogram.exceptions import TelegramNetworkError, TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import (
    Message,
    FSInputFile,
    InputMediaVideo,
    InputMediaPhoto,
    MessageEntity,
)
from aiogram_dialog.api.protocols import MessageNotModified
from aiogram_media_group import media_group_handler
from aiogram_dialog import DialogManager, StartMode
from core.config import settings
from core.repositories.admin import admin_repo
from core.repositories.channel import channel_repo
from core.repositories.message import message_repo
from dialogs.states import Wizard

from utils.editor import create_watermarked_video, create_watermarked_photo
from utils.translator import translate

menu_router = Router()
font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
bot = Bot(token=settings.ADMIN_BOT)


async def process_media_group(message: Message, media_type: str, file_id: str):
    # Скачивание медиафайла
    if message.text is not None:
        text = message.text
    elif message.caption is not None:
        text = message.caption
    else:
        text = None
    if text is not None and len(text) > 750:
        await message.reply(
            f"Количество символов больше 750({len(text)}). Пост не будет отправлен"
        )
        return
    try:
        media_file = await bot.get_file(file_id)
    except TelegramBadRequest as e:
        await message.reply(f"Вес файла слишком большой:\n{e}")
        return
    except Exception as e:
        await message.reply(
            f"Ошибка получения файла сообщения {message.message_id}\nОшибка: {e}"
        )
        return
    # Получение списка каналов из базы данных
    channels = await channel_repo.get_all()
    ext = "mp4" if media_type == "video" else "jpg"

    media_path = f"input_{media_type}_{message.message_id}_{file_id}.{ext}"

    try:
        await bot.download_file(media_file.file_path, media_path)
    except Exception as e:
        await message.reply(
            f"Ошибка загрузки сообщения {message.message_id} попробуйте ещё раз\nОшибка: {e}"
        )
    # Список водяных знаков и путей для сохранения медиафайлов
    watermarks = [f"{i.channel_name}" for i in channels]
    output_paths = {
        i.channel_id: f"output_{media_type}_watermark_{message.message_id}_{i.channel_id}.{ext}"
        for i in channels
    }

    # Использование ProcessPoolExecutor для параллельной обработки
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=15) as executor:
        futures = [
            loop.run_in_executor(
                executor,
                (
                    create_watermarked_video
                    if media_type == "video"
                    else create_watermarked_photo
                ),
                media_path,
                watermark,
                output_path,
                (
                    await channel_repo.get_by_channel_id(
                        next(
                            (k for k, v in output_paths.items() if v == output_path),
                            None,
                        )
                    )
                ).watermark,
            )
            for watermark, output_path in zip(watermarks, output_paths.values())
        ]
        for future in asyncio.as_completed(futures):
            try:
                result = await future
                if result is None:
                    raise Exception("Одна или несколько задач завершились с ошибкой.")
            except Exception as e:
                print(f"Ошибка при обработке медиафайла: {e}")

    return output_paths, channels, media_path


async def process_media_single(message: Message, is_video: bool):
    if message.caption is not None and len(message.caption) > 750:
        await message.reply(
            f"Количество символов больше 750({len(message.caption)}). Пост не будет отправлен"
        )
        return
    # Скачивание медиафайла
    media_type = "video" if is_video else "photo"
    try:
        if media_type == "video":
            media_file = await bot.get_file(message.video.file_id)
        else:
            media_file = await bot.get_file(message.photo[-1].file_id)
    except TelegramBadRequest as e:
        await message.reply(f"Вес файла слишком большой:\n{e}")
        return
    except Exception as e:
        await message.reply(f"{e}")
        return
    # Получение списка каналов из базы данных
    channels = await channel_repo.get_all()
    ext = "mp4" if media_type == "video" else "jpg"
    if media_type == "video":
        media_path = (
            f"input_{media_type}_{message.message_id}_{message.video.file_id}.{ext}"
        )
    else:
        media_path = (
            f"input_{media_type}_{message.message_id}_{message.photo[-1].file_id}.{ext}"
        )
    try:
        await bot.download_file(media_file.file_path, media_path)
    except Exception as e:
        await message.reply(
            f"Ошибка загрузки сообщения {message.message_id} попробуйте ещё раз\nОшибка: {e}"
        )
    # Список водяных знаков и путей для сохранения медиафайлов только для каналов с watermark
    watermarks = [f"{i.channel_name}" for i in channels]
    output_paths = {
        i.channel_id: f"output_{media_type}_watermark_{message.message_id}_{i.channel_id}.{ext}"
        for i in channels
    }

    # Использование ProcessPoolExecutor для параллельной обработки
    loop = asyncio.get_event_loop()
    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [
            loop.run_in_executor(
                executor,
                (create_watermarked_video if is_video else create_watermarked_photo),
                media_path,
                watermark,
                output_path,
                (
                    await channel_repo.get_by_channel_id(
                        next(
                            (k for k, v in output_paths.items() if v == output_path),
                            None,
                        )
                    )
                ).watermark,
            )
            for watermark, output_path in zip(watermarks, output_paths.values())
        ]
        for future in asyncio.as_completed(futures):
            result = await future
            if result is None:
                raise Exception("Одна или несколько задач завершились с ошибкой.")

    # Отправка обработанных медиафайлов во все каналы
    for channel in channels:
        # Выбираем путь для отправки: с водяным знаком или без
        output_path = next(
            (p for p in output_paths.values() if f"_{channel.channel_id}." in p),
            media_path,
        )

        if message.caption is None:
            caption = f'\n\n<a href="{channel.link_discussion}">{channel.text_discussion}</a>\n\n<a href="{channel.link_invitation}">{channel.text_invitation}</a>'
        else:
            caption = (
                await translate(message.caption, channel.language)
                + f'\n\n<a href="{channel.link_discussion}">{channel.text_discussion}</a>\n\n<a href="{channel.link_invitation}">{channel.text_invitation}</a>'
            )

        if caption is not None and len(caption) >= 1000:
            await message.reply(
                f"Ошибка отправки в канал {channel.channel_name} количество символов ({len(caption)})"
            )
            continue

        if is_video:
            mess = await bot.send_media_group(
                chat_id=channel.channel_id,
                media=[
                    InputMediaVideo(
                        media=FSInputFile(output_path),
                        caption=caption,
                        parse_mode="HTML",
                    )
                ],
                request_timeout=120,
            )
            await message_repo.create(
                main_message_id=str(message.message_id),
                channel_id=channel.channel_id,
                message_id=str(mess[0].message_id),
            )
        else:
            mess = await bot.send_media_group(
                chat_id=channel.channel_id,
                media=[
                    InputMediaPhoto(
                        media=FSInputFile(output_path),
                        caption=caption,
                        parse_mode="HTML",
                    )
                ],
                request_timeout=120,
            )
            await message_repo.create(
                main_message_id=str(message.message_id),
                channel_id=channel.channel_id,
                message_id=str(mess[0].message_id),
            )

    # Удаление временных файлов
    for output_path in output_paths.values():
        os.remove(output_path)


async def process_text(message: Message):
    if len(message.text) > 3500:
        await message.reply(
            f"Количество символов больше 3500({len(message.text)}). Пост не будет отправлен"
        )
        return
    # Получение списка каналов из базы данных
    channels = await channel_repo.get_all()

    # Отправка текстового сообщения в каналы
    for channel in channels:
        text = (
            await translate(message.text, channel.language)
            + f'\n\n<a href="{channel.link_discussion}">{channel.text_discussion}</a>\n\n<a href="{channel.link_invitation}">{channel.text_invitation}</a>'
        )

        if len(text) >= 4000:
            await message.reply(
                f"Ошибка отправки в канал {channel.channel_name} количество символов ({len(text)})"
            )
            continue

        mess = await bot.send_message(
            chat_id=channel.channel_id,
            text=text,
            parse_mode="HTML",
        )

        await message_repo.create(
            main_message_id=str(message.message_id),
            channel_id=channel.channel_id,
            message_id=str(mess.message_id),
        )


@menu_router.message(Command("start"))
async def start_mess(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=Wizard.home_page, mode=StartMode.RESET_STACK)


@menu_router.channel_post(F.media_group_id, F.content_type.in_({"photo", "video"}))
@media_group_handler
async def handle_media_group(messages: list[Message]):
    if str(messages[0].chat.id) == str(settings.CHANNEL_ID):
        if len(messages) > 3:
            await messages[0].reply(
                f"Количество медиа больше 3({len(messages)}) пост не будет отправлен"
            )
            return
        media_files_by_channel = {}

        for message in messages:
            caption_start = message.caption or message.text
            media_type = "photo" if message.photo else "video"
            file_id = (
                message.photo[-1].file_id if message.photo else message.video.file_id
            )

            output_paths, channels, media_path = await process_media_group(
                message, media_type, file_id
            )

            for channel in channels:
                # Выбираем путь для отправки: с водяным знаком или без
                output_path = output_paths.get(channel.channel_id, media_path)

                # Добавляем подпись только к первому медиафайлу для данного канала
                if channel.channel_id not in media_files_by_channel:
                    if caption_start is None:
                        caption = (
                            f'<a href="{channel.link_discussion}">{channel.text_discussion}</a>\n\n'
                            f'<a href="{channel.link_invitation}">{channel.text_invitation}</a>'
                        )
                    else:
                        caption = await translate(caption_start, channel.language) + (
                            f'\n\n<a href="{channel.link_discussion}">{channel.text_discussion}</a>\n\n'
                            f'<a href="{channel.link_invitation}">{channel.text_invitation}</a>'
                        )
                else:
                    caption = None

                if caption is not None and len(caption) >= 1000:
                    await message.reply(
                        f"Ошибка отправки в канал {channel.channel_name} количество символов ({len(caption)})"
                    )
                    continue

                # Добавляем медиафайл в список
                media_files_by_channel.setdefault(channel.channel_id, []).append(
                    InputMediaVideo(
                        media=FSInputFile(output_path),
                        caption=caption,
                        parse_mode="HTML",
                    )
                    if media_type == "video"
                    else InputMediaPhoto(
                        media=FSInputFile(output_path),
                        caption=caption,
                        parse_mode="HTML",
                    )
                )

        # Отправка всех медиафайлов в соответствующие каналы
        for channel_id, media_files in media_files_by_channel.items():
            mess = await bot.send_media_group(
                chat_id=channel_id,
                media=media_files,
                request_timeout=120,
            )
            mess_ids = ""
            for i in mess:
                mess_ids += f"{i.message_id},"
            await message_repo.create(
                main_message_id=str(messages[0].message_id),
                channel_id=channel_id,
                message_id=mess_ids,
            )

        await messages[0].reply(f"id: {messages[0].message_id}")
        # Удаление временных файлов
        for output_paths_list in media_files_by_channel.values():
            for media_file in output_paths_list:
                try:
                    os.remove(media_file.media.path)
                except FileNotFoundError:
                    print(f"Файл {media_file.media.path} не найден для удаления.")
                except Exception as e:
                    print(f"Ошибка при удалении файла {media_file.media.path}: {e}")


@menu_router.channel_post()
async def handle_channel_video(message: Message):
    if str(message.chat.id) == str(settings.CHANNEL_ID):
        if message.video:
            await process_media_single(message, is_video=True)
            await message.reply(f"id: {message.message_id}")
        elif message.photo:
            await process_media_single(message, is_video=False)
            await message.reply(f"id: {message.message_id}")
        else:
            await process_text(message)
            await message.reply(f"id: {message.message_id}")


@menu_router.edited_channel_post()
async def handle_edit(message: Message):
    if str(message.chat.id) == str(settings.CHANNEL_ID):
        related_messages = await message_repo.get_by_id_all(message.message_id)
        for related_message in related_messages:
            channel_id = related_message.channel_id
            message_id = related_message.message_id
            # Обновление поста в канале
            await bot.delete_message(
                chat_id=channel_id,
                message_id=message_id,
            )

        await handle_channel_video(message)
