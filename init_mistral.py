#!/usr/bin/env python3
"""
Скрипт для инициализации Mistral токенов
Запускается один раз для добавления начальных данных
"""

import asyncio
from core.repositories.mistral_token import mistral_token_repo
from core.repositories.translator_settings import translator_settings_repo


async def init_mistral_tokens():
    """Инициализация Mistral токенов"""
    
    # Ваши данные для Mistral
    api_key = "FVved5ohmgoHYYFh7uK2laq5rQNAzgZ5"
    agent_id = "ag:9885ec37:20250717:cheshskii:a70b740a"
    
    # Проверяем, есть ли уже такой токен
    existing_token = await mistral_token_repo.get_by_api_key(api_key)
    
    if not existing_token:
        # Создаем новый токен
        await mistral_token_repo.create(
            api_key=api_key,
            agent_id=agent_id,
            status=True
        )
        print(f"✅ Mistral токен добавлен: {api_key[:8]}...")
    else:
        print(f"ℹ️ Mistral токен уже существует: {api_key[:8]}...")
    
    # Устанавливаем переводчик по умолчанию (deepl)
    current_translator = await translator_settings_repo.get_current_translator()
    print(f"ℹ️ Текущий переводчик: {current_translator}")
    
    print("✅ Инициализация завершена")


if __name__ == "__main__":
    asyncio.run(init_mistral_tokens())