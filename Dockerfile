# Используем базовый образ Python 3.12-slim
FROM python:3.12-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем зависимости ОС, включая wget и ffmpeg
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    build-essential \
    libssl-dev \
    libffi-dev \
    python3-dev \
    python3-pip \
    fonts-dejavu \
    && wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz \
    && tar -xJf ffmpeg-release-amd64-static.tar.xz \
    && mv ffmpeg-*/ffmpeg /usr/local/bin/ \
    && mv ffmpeg-*/ffprobe /usr/local/bin/ \
    && rm -rf ffmpeg-*/ ffmpeg-release-amd64-static.tar.xz \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN pip install poetry

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

# Копируем только необходимые файлы для установки зависимостей
COPY pyproject.toml poetry.lock* /app/

# Перегенерируем lock-файл, если pyproject.toml изменился
RUN poetry lock

# Устанавливаем зависимости без установки текущего пакета
RUN poetry install --no-root --no-interaction --no-ansi

# Копируем всё приложение и скрипт запуска
COPY . /app
COPY start.sh /app/
RUN chmod +x start.sh

# Точка входа
CMD ["/app/start.sh"]
