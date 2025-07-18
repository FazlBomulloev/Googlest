#!/bin/bash

# Применяем миграции
poetry run alembic upgrade head

# Инициализируем Mistral токены (запускается один раз)
poetry run python3 init_mistral.py

# Запускаем сервер
poetry run python3 main.py