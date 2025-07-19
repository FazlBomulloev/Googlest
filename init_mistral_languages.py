import asyncio
from core.repositories.mistral_language import mistral_language_repo
from core.repositories.translator_settings import translator_settings_repo


async def init_mistral_languages_system():
    """Инициализация системы языков Mistral"""
    
    print("🚀 Инициализация системы языков Mistral...")
    
    # Проверяем, что языки были созданы миграцией
    languages = await mistral_language_repo.get_all()
    print(f"📊 Найдено языков в базе: {len(languages)}")
    
    for language in languages:
        print(f"✅ {language.name}: {language.agent_id[:30]}...")
    
    # Устанавливаем переводчик по умолчанию (если не установлен)
    current_translator = await translator_settings_repo.get_current_translator()
    print(f"🔧 Текущий переводчик: {current_translator}")
    
    print("✅ Система языков Mistral готова к работе!")
    print("📝 Теперь вы можете:")
    print("   • Привязывать каналы к языкам через UI")
    print("   • Добавлять новые языки и агенты")
    print("   • Редактировать API ключи и Agent ID")


if __name__ == "__main__":
    asyncio.run(init_mistral_languages_system())