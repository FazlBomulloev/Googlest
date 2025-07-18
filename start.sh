#!/bin/bash



# Применяем миграции
#poetry run alembic revision --autogenerate -m "Final Tables"
#poetry run alembic upgrade head

# Запускаем сервер
poetry run python3 main.py