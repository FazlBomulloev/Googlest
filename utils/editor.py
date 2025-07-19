from PIL import Image
from mako.testing.helpers import result_lines
from moviepy import (
    VideoFileClip,
    TextClip,
    CompositeVideoClip,
    ImageClip,
)
import time
import os
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed, ProcessPoolExecutor

from core.repositories.channel import channel_repo

# Подавляем вывод MoviePy
os.environ["IMAGEIO_FFMPEG_EXE"] = "/usr/local/bin/ffmpeg"

font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def create_watermarked_video(video_path, watermark_text, output_path, wm):
    video = VideoFileClip(video_path)
    video = video.resized(0.85)  
    
    try:
        if wm:
            font_size = int(video.size[0] * 0.03)
            watermark = TextClip(
                text=watermark_text,
                font_size=font_size,
                color="red",
                font=font_path,
                stroke_color="white",  # Цвет обводки
                stroke_width=1,  # Ширина обводки
                method="caption",  # Метод для автоматического переноса текста
                size=video.size,  # Размер видео
                horizontal_align="left",  # Выравнивание текста по левому краю
                vertical_align="center",  # Выравнивание текста по центру
                duration=video.duration,
            ).rotated(30)
            
            # Наложение водяного знака на видео
            result = CompositeVideoClip([video, watermark])
        else:
            result = CompositeVideoClip([video])
        
        # 🔧 УНИКАЛЬНЫЙ временный аудиофайл для каждого процесса
        unique_temp_audio = f"temp-audio-{uuid.uuid4().hex[:8]}.m4a"
        
        result.write_videofile(
            output_path,
            codec='libx264',          
            audio_codec='aac',        
            temp_audiofile=unique_temp_audio, 
            remove_temp=True,
            preset='medium',          
            ffmpeg_params=[
                '-crf', '23',         
                '-pix_fmt', 'yuv420p', 
                '-movflags', '+faststart',  
                '-max_muxing_queue_size', '1024',  
                '-avoid_negative_ts', 'make_zero'   
            ],
            fps=min(video.fps, 30),   
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
            horizontal_align="left",  # Выравнивание текста по левому краю
            vertical_align="center",  # Выравнивание текста по центру
            duration=photo.duration,
        ).rotated(30)
        
        # Наложение водяного знака на фото и сохранение результата
        if wm:
            result = CompositeVideoClip([photo, watermark])
        else:
            result = CompositeVideoClip([photo])
            
        frame = result.get_frame(0)  # Получение первого кадра
        img = Image.fromarray(frame)
        img = img.convert("RGB")  # Удаление альфа-канала
        
        # Сохранение с оптимальными настройками для Telegram
        img.save(output_path, "JPEG", quality=85, optimize=True)
        
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