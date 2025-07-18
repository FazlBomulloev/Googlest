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
    
    try:
        # Создание текстового водяного знака только если нужен
        if wm:
            # Определяем размер шрифта относительно размера видео
            font_size = max(20, int(min(video.size) * 0.04))  # Минимум 20px
            
            watermark = TextClip(
                text=watermark_text,
                font_size=font_size,
                color="red",
                font=font_path,
                stroke_color="white",
                stroke_width=2,
                duration=video.duration,
            ).with_position(('center', 'center')).with_opacity(0.7).rotated(30)
            
            # Наложение водяного знака на видео
            result = CompositeVideoClip([video, watermark])
        else:
            result = video
        
        # Настройки для совместимости с Telegram
        result.write_videofile(
            output_path,
            codec='libx264',           # H.264 кодек - совместим с Telegram
            audio_codec='aac',         # AAC аудио кодек
            temp_audiofile='temp-audio.m4a',
            remove_temp=True,
            preset='medium',           # Баланс качества и скорости
            ffmpeg_params=[
                '-crf', '23',          # Качество видео (18-28 оптимально)
                '-pix_fmt', 'yuv420p', # Формат пикселей для совместимости
                '-movflags', '+faststart',  # Для быстрой загрузки
                '-max_muxing_queue_size', '1024',  # Буфер для стабильности
                '-avoid_negative_ts', 'make_zero'   # Фиксация временных меток
            ],
            fps=min(video.fps, 30),    # Ограничиваем до 30 FPS максимум
            verbose=False,
            logger=None
        )
        
        print(f"Видео с водяным знаком '{watermark_text}' сохранено в {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Ошибка при создании видео с водяным знаком '{watermark_text}': {e}")
        return None
    finally:
        # Освобождаем ресурсы
        video.close()
        if 'result' in locals():
            result.close()


def create_watermarked_photo(photo_path, watermark_text, output_path, wm):
    photo = ImageClip(photo_path)
    
    try:
        if wm:
            # Создание текстового водяного знака
            font_size = max(24, int(min(photo.size) * 0.04))  # Минимум 24px для фото
            
            watermark = TextClip(
                text=watermark_text,
                font_size=font_size,
                color="red",
                font=font_path,
                stroke_color="white",
                stroke_width=2,
                duration=1,  # Для фото достаточно 1 секунды
            ).with_position(('center', 'center')).with_opacity(0.7).rotated(30)
            
            # Наложение водяного знака на фото
            result = CompositeVideoClip([photo, watermark])
        else:
            result = CompositeVideoClip([photo])
        
        # Получение первого кадра и сохранение как изображение
        frame = result.get_frame(0)
        img = Image.fromarray(frame)
        
        # Конвертация в RGB и сохранение
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Сохранение с оптимальными настройками для Telegram
        img.save(output_path, 'JPEG', quality=85, optimize=True)
        
        print(f"Фото с водяным знаком '{watermark_text}' сохранено в {output_path}")
        return output_path
        
    except Exception as e:
        print(f"Ошибка при создании фото с водяным знаком '{watermark_text}': {e}")
        return None
    finally:
        # Освобождаем ресурсы
        photo.close()
        if 'result' in locals():
            result.close()