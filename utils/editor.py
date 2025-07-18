from PIL import Image
from mako.testing.helpers import result_lines
from moviepy import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    ImageClip,
)
import time
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor

from core.repositories.channel import channel_repo

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def create_watermarked_video(video_path, watermark_text, output_path, wm):
    video = VideoFileClip(video_path)
    video = video.resized(0.85)
    try:
        # Создание текстового водяного знака
        font_size = int(video.size[0] * 0.03)
        watermark = TextClip(
            text=watermark_text,
            font_size=font_size,
            color="red",
            font=font_path,
            stroke_color="white",  # Цвет обводки
            stroke_width=1,  # Ширина обводки
            method="caption",  # Метод для автоматического переноса текста
            size=video.size,  # Размер фото
            horizontal_align="left",  # Выравнивание текста по правому краю
            vertical_align="center",  # Выравнивание текста по нижнему краю
            duration=video.duration,
        ).rotated(30)
        # Наложение водяного знака на видео и сохранение результата
        if wm:
            result = CompositeVideoClip([video, watermark])
        else:
            result = CompositeVideoClip([video])
        result.write_videofile(output_path, preset="ultrafast", fps=video.fps / 2)
        print(f"Видео с водяным знаком '{watermark_text}' сохранено в {output_path}")
        return output_path
    except Exception as e:
        print(f"Ошибка при создании видео с водяным знаком '{watermark_text}': {e}")
        return None


def create_watermarked_photo(photo_path, watermark_text, output_path, wm):
    photo = ImageClip(photo_path)
    try:
        # Создание текстового водяного знака
        font_size = int(photo.size[0] * 0.03)
        watermark = TextClip(
            text=watermark_text,
            font_size=font_size,
            color="red",
            font=font_path,
            stroke_color="white",  # Цвет обводки
            stroke_width=1,  # Ширина обводки
            method="caption",  # Метод для автоматического переноса текста
            size=photo.size,  # Размер фото
            horizontal_align="left",  # Выравнивание текста по правому краю
            vertical_align="center",  # Выравнивание текста по нижнему краю
            duration=photo.duration,
        ).rotated(30)
        # Наложение водяного знака на фото и сохранение результата
        result = CompositeVideoClip([photo, watermark])
        frame = result.get_frame(0)  # Получение первого кадра
        img = Image.fromarray(frame)
        img = img.convert("RGB")  # Удаление альфа-канала
        img.save(output_path, "JPEG")
        print(f"Фото с водяным знаком '{watermark_text}' сохранено в {output_path}")
        return output_path
    except Exception as e:
        print(f"Ошибка при создании фото с водяным знаком '{watermark_text}': {e}")
        return None
