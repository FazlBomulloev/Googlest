#!/bin/bash

# Применяем миграции
poetry run alembic upgrade head

# Инициализируем систему языков Mistral (проверка данных)
poetry run python3 init_mistral_languages.py

# Запускаем сервер
poetry run python3 main.py