# -- 3.0.0 - Final version with strict error handling
import asyncio
import datetime
import logging

from deepl.exceptions import QuotaExceededException, AuthorizationException

import deepl

from core.repositories.token import token_repo
from core.repositories.mistral_token import mistral_token_repo
from core.repositories.translator_settings import translator_settings_repo
from core.repositories.mistral_language import mistral_language_repo
from core.repositories.language_channel import language_channel_repo
from utils.mistral_client import (
    MistralClient, 
    MistralRateLimitError, 
    MistralAuthError, 
    MistralAPIError,
    MistralTimeoutError,
    MistralConnectionError
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

proxy = {
    "http": "168.80.203.233:8000:HA8kr7:LaeEas",
    "http": "168.81.64.241:8000:GvjxK5:roPDLH",
    "http": "168.81.67.86:8000:GvjxK5:roPDLH",
    "http": "168.81.65.83:8000:GvjxK5:roPDLH",
    "http": "168.81.65.230:8000:GvjxK5:roPDLH",
    "http": "168.80.201.196:8000:GvjxK5:roPDLH",
}

# Маппинг языков для DeepL
DEEPL_LANGUAGE_MAP = {
    "Болгарский": "BG",
    "Чешский": "CS", 
    "Немецкий": "DE",
    "Греческий": "EL",
    "Английский": "EN-US",
    "Испанский": "ES",
    "Финский": "FI",
    "Французский": "FR",
    "Венгерский": "HU",
    "Итальянский": "IT",
    "Голландский": "NL",
    "Польский": "PL",
    "Румынский": "RO",
    "Словацкий": "SK",
    "Турецкий": "TR",
    "Русский": "RU"
}


class TranslationError(Exception):
    """Исключение для ошибок перевода"""
    pass


async def translate_with_deepl(text: str, language_name: str) -> str:
    """
    Переводит текст через DeepL API
    Raises TranslationError если перевод невозможен
    """
    tokens = await token_repo.get_all()
    
    # Получаем код языка для DeepL
    deepl_lang_code = DEEPL_LANGUAGE_MAP.get(language_name)
    if not deepl_lang_code:
        raise TranslationError(f"Language {language_name} not supported by DeepL")
    
    if not tokens:
        raise TranslationError("No DeepL tokens available")
    
    for token in tokens:
        if not token.status:
            continue
            
        try:
            result = (
                deepl.Translator(token.token, proxy=proxy)
                .translate_text(text, target_lang=deepl_lang_code)
                .text
            )
            logger.info(f"✅ DeepL translation successful ({language_name}): {token.token[:8]}...")
            return result
        except QuotaExceededException:
            unblock_time = datetime.datetime.now() + datetime.timedelta(days=10)
            await token_repo.update_time(token.token, unblock_time)
            await token_repo.update_status(token.token, False)
            logger.warning(f"🚫 DeepL quota exceeded: {token.token[:8]}... Blocked until {unblock_time}")
            continue
        except AuthorizationException:
            await token_repo.del_token(token.token)
            logger.warning(f"❌ DeepL token deleted (invalid): {token.token[:8]}...")
            continue
        except Exception as e:
            logger.error(f"❌ DeepL error for token {token.token[:8]}...: {str(e)}")
            continue
    
    raise TranslationError("All DeepL tokens exhausted or failed")


async def translate_with_mistral(text: str, language_name: str) -> str:
    """
    Переводит текст через Mistral API с языково-специфичным агентом
    Raises TranslationError если перевод невозможен
    """
    # Получаем язык из базы данных
    language = await mistral_language_repo.get_by_name(language_name)
    
    if not language:
        raise TranslationError(f"Language {language_name} not found in Mistral languages")
    
    if not language.status:
        raise TranslationError(f"Language {language_name} is disabled")
    
    try:
        client = MistralClient(language.api_key, language.agent_id)
        result = await client.translate(text, language_name)
        if result:
            logger.info(f"✅ Mistral translation successful ({language_name}): {language.api_key[:8]}...")
            return result
        else:
            raise TranslationError(f"Empty response from Mistral for {language_name}")
            
    except MistralRateLimitError:
        unblock_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        await mistral_language_repo.update_status(language.id, False)
        logger.warning(f"🚫 Mistral rate limit ({language_name}): {language.api_key[:8]}... Blocked until {unblock_time}")
        raise TranslationError(f"Mistral rate limit for {language_name}")
        
    except MistralAuthError:
        await mistral_language_repo.update_status(language.id, False)
        logger.warning(f"❌ Mistral auth error ({language_name}): {language.api_key[:8]}...")
        raise TranslationError(f"Mistral authentication failed for {language_name}")
        
    except (MistralAPIError, MistralTimeoutError, MistralConnectionError) as e:
        logger.error(f"❌ Mistral error ({language_name}) for {language.api_key[:8]}...: {str(e)}")
        raise TranslationError(f"Mistral API error for {language_name}: {str(e)}")


async def get_language_by_channel_id(channel_id: str) -> str:
    """
    Получает название языка по ID канала
    """
    # Ищем в новой системе языков
    language_channel = await language_channel_repo.get_language_by_channel(channel_id)
    if language_channel:
        language = await mistral_language_repo.get_by_id(language_channel.language_id)
        if language:
            logger.info(f"🎯 Found language {language.name} for channel {channel_id}")
            return language.name
    
    # Если не найдено, возвращаем русский (для каналов без перевода)
    logger.warning(f"⚠️ No language found for channel {channel_id}, using Russian")
    return "Русский"


async def translate(text: str, channel_id: str = None, language_name: str = None) -> str:
    """
    Основная функция перевода с СТРОГОЙ обработкой ошибок
    Raises TranslationError если перевод невозможен для критических каналов
    """
    # Определяем язык перевода
    if language_name:
        target_language = language_name
    elif channel_id:
        target_language = await get_language_by_channel_id(channel_id)
    else:
        target_language = "Русский"  # По умолчанию
    
    # Если язык русский - не переводим
    if target_language == "Русский":
        logger.info("🇷🇺 Russian language detected, skipping translation")
        return text
    
    # Получаем текущий выбранный переводчик
    current_translator = await translator_settings_repo.get_current_translator()
    
    logger.info(f"🌍 Translating to {target_language} using {current_translator}")
    
    # Сначала пробуем выбранный переводчик
    if current_translator == "deepl":
        try:
            return await translate_with_deepl(text, target_language)
        except TranslationError as e:
            logger.warning(f"DeepL failed for {target_language}: {str(e)}, trying Mistral...")
            try:
                return await translate_with_mistral(text, target_language)
            except TranslationError as e2:
                logger.error(f"Both translators failed for {target_language}. DeepL: {str(e)}, Mistral: {str(e2)}")
                # СТРОГАЯ ОБРАБОТКА: выбрасываем исключение вместо возврата оригинала
                raise TranslationError(f"Translation failed for {target_language}: DeepL - {str(e)}, Mistral - {str(e2)}")
    else:  # mistral
        try:
            return await translate_with_mistral(text, target_language)
        except TranslationError as e:
            logger.warning(f"Mistral failed for {target_language}: {str(e)}, trying DeepL...")
            try:
                return await translate_with_deepl(text, target_language)
            except TranslationError as e2:
                logger.error(f"Both translators failed for {target_language}. Mistral: {str(e)}, DeepL: {str(e2)}")
                raise TranslationError(f"Translation failed for {target_language}: Mistral - {str(e)}, DeepL - {str(e2)}")


async def safe_translate(text: str, channel_id: str = None, language_name: str = None) -> tuple[str, bool]:
    """
    Безопасная функция перевода, которая возвращает (текст, успешность)
    Используется в основном коде для обработки ошибок без прерывания публикации
    """
    try:
        translated_text = await translate(text, channel_id, language_name)
        return translated_text, True
    except TranslationError as e:
        logger.error(f"💥 Translation failed: {str(e)}")
        return text, False  # Возвращаем оригинал + флаг ошибки
    except Exception as e:
        logger.error(f"💥 Unexpected translation error: {str(e)}")
        return text, False


async def check_deepl():
    """
    Проверяет и обновляет статус DeepL токенов
    """
    while True:
        logger.info("🔍 Starting DeepL token check")
        tokens = await token_repo.get_all()

        for token in tokens:
            try:
                deepl.Translator(token.token).get_usage()
                await token_repo.update_time(token.token, None)
                await token_repo.update_status(token.token, True)
                logger.info(f"✅ DeepL token valid: {token.token[:8]}...")
            except deepl.QuotaExceededException:
                token_time = await token_repo.get_time_by_token(token.token)

                if token_time is not None:
                    logger.info(f"⏳ DeepL token already blocked: {token.token[:8]}...")
                    continue

                unblock_time = datetime.datetime.now() + datetime.timedelta(days=10)
                await token_repo.update_time(token.token, unblock_time)
                await token_repo.update_status(token.token, False)
                logger.warning(f"🚫 DeepL quota exceeded: {token.token[:8]}... Blocked until {unblock_time}")
            except Exception as e:
                logger.error(f"[DEEPL CHECK ERROR] {e}")

        current_time = datetime.datetime.now()

        for token in tokens:
            token_record = await token_repo.get_time_by_token(token.token)

            if token_record.time is not None and current_time > token_record.time:
                try:
                    deepl.Translator(token.token).get_usage()
                    await token_repo.update_status(token.token, True)
                    await token_repo.update_time(token.token, None)
                    logger.info(f"🔓 DeepL token reactivated: {token.token[:8]}...")
                except deepl.AuthorizationException:
                    await token_repo.del_token(token.token)
                    logger.warning(f"❌ DeepL token deleted (invalid): {token.token[:8]}...")
                except Exception as e:
                    logger.error(f"[DEEPL REACTIVATION ERROR] {e}")

        logger.info("🕒 DeepL check sleeping for 24 hours...")
        await asyncio.sleep(86400)


async def check_mistral():
    """
    Проверяет и обновляет статус всех Mistral языков
    """
    while True:
        logger.info("🔍 Starting Mistral languages check")
        languages = await mistral_language_repo.get_all()

        for language in languages:
            try:
                client = MistralClient(language.api_key, language.agent_id)
                is_healthy = await client.check_health()
                
                if is_healthy:
                    await mistral_language_repo.update_status(language.id, True)
                    logger.info(f"✅ Mistral language valid ({language.name}): {language.api_key[:8]}...")
                else:
                    logger.warning(f"⚠️ Mistral language unhealthy ({language.name}): {language.api_key[:8]}...")
                    
            except Exception as e:
                logger.error(f"[MISTRAL CHECK ERROR] for {language.name}: {e}")

        logger.info("🕒 Mistral languages check sleeping for 1 hour...")
        await asyncio.sleep(3600)  # Проверяем каждый час


if __name__ == "__main__":
    # Пример использования
    asyncio.run(translate("Привет мир", language_name="Чешский"))