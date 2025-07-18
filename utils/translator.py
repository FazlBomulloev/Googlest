# -- 1.0.0
import asyncio
import datetime
import logging

from deepl.exceptions import QuotaExceededException, AuthorizationException

import deepl

from core.repositories.token import token_repo
from core.repositories.mistral_token import mistral_token_repo
from core.repositories.translator_settings import translator_settings_repo
from utils.mistral_client import (
    MistralClient, 
    MistralRateLimitError, 
    MistralAuthError, 
    MistralAPIError,
    MistralTimeoutError,
    MistralConnectionError
)

logging.basicConfig(
    level=logging.INFO,  # Показывать INFO, WARNING, ERROR и т.д.
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


async def translate_with_deepl(text: str, lang: str) -> str:
    """
    Переводит текст через DeepL API
    """
    tokens = await token_repo.get_all()
    deepl_langs = [
        "BG", "CS", "DA", "DE", "EL", "EN", "EN-GB", "EN-US", "ES", "ET", "FI", "FR", 
        "HU", "ID", "IT", "JA", "KO", "LT", "LV", "NB", "NL", "PL", "PT", "PT-BR", 
        "PT-PT", "RO", "SK", "SL", "SV", "TR", "UK", "ZH", "RU"
    ]
    
    if lang not in deepl_langs:
        raise Exception(f"Language {lang} not supported by DeepL")
    
    if not tokens:
        raise Exception("No DeepL tokens available")
    
    for token in tokens:
        if not token.status:
            continue
            
        try:
            result = (
                deepl.Translator(token.token, proxy=proxy)
                .translate_text(text, target_lang=lang)
                .text
            )
            logger.info(f"✅ DeepL translation successful: {token.token[:8]}...")
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
    
    raise Exception("All DeepL tokens exhausted or failed")


async def translate_with_mistral(text: str, lang: str) -> str:
    """
    Переводит текст через Mistral API
    """
    tokens = await mistral_token_repo.get_all()
    
    if not tokens:
        raise Exception("No Mistral tokens available")
    
    for token in tokens:
        if not token.status:
            continue
            
        try:
            client = MistralClient(token.api_key, token.agent_id)
            result = await client.translate(text, lang)
            if result:
                logger.info(f"✅ Mistral translation successful: {token.api_key[:8]}...")
                return result
        except MistralRateLimitError:
            unblock_time = datetime.datetime.now() + datetime.timedelta(hours=1)
            await mistral_token_repo.update_time(token.api_key, unblock_time)
            await mistral_token_repo.update_status(token.api_key, False)
            logger.warning(f"🚫 Mistral rate limit: {token.api_key[:8]}... Blocked until {unblock_time}")
            continue
        except MistralAuthError:
            await mistral_token_repo.del_token(token.api_key)
            logger.warning(f"❌ Mistral token deleted (invalid): {token.api_key[:8]}...")
            continue
        except (MistralAPIError, MistralTimeoutError, MistralConnectionError) as e:
            logger.error(f"❌ Mistral error for token {token.api_key[:8]}...: {str(e)}")
            continue
    
    raise Exception("All Mistral tokens exhausted or failed")


async def translate(text: str, lang: str = "EN-US") -> str:
    """
    Основная функция перевода с ротацией между переводчиками
    """
    # Получаем текущий выбранный переводчик
    current_translator = await translator_settings_repo.get_current_translator()
    
    # Сначала пробуем выбранный переводчик
    if current_translator == "deepl":
        try:
            return await translate_with_deepl(text, lang)
        except Exception as e:
            logger.warning(f"DeepL failed: {str(e)}, trying Mistral...")
            try:
                return await translate_with_mistral(text, lang)
            except Exception as e2:
                logger.error(f"Both translators failed. DeepL: {str(e)}, Mistral: {str(e2)}")
                return text  # Возвращаем оригинальный текст
    else:  # mistral
        try:
            return await translate_with_mistral(text, lang)
        except Exception as e:
            logger.warning(f"Mistral failed: {str(e)}, trying DeepL...")
            try:
                return await translate_with_deepl(text, lang)
            except Exception as e2:
                logger.error(f"Both translators failed. Mistral: {str(e)}, DeepL: {str(e2)}")
                return text  # Возвращаем оригинальный текст


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
    Проверяет и обновляет статус Mistral токенов
    """
    while True:
        logger.info("🔍 Starting Mistral token check")
        tokens = await mistral_token_repo.get_all()

        for token in tokens:
            try:
                client = MistralClient(token.api_key, token.agent_id)
                is_healthy = await client.check_health()
                
                if is_healthy:
                    await mistral_token_repo.update_time(token.api_key, None)
                    await mistral_token_repo.update_status(token.api_key, True)
                    logger.info(f"✅ Mistral token valid: {token.api_key[:8]}...")
                else:
                    logger.warning(f"⚠️ Mistral token unhealthy: {token.api_key[:8]}...")
                    
            except Exception as e:
                logger.error(f"[MISTRAL CHECK ERROR] {e}")

        # Проверяем заблокированные токены
        current_time = datetime.datetime.now()
        for token in tokens:
            if token.time is not None and current_time > datetime.datetime.fromisoformat(token.time):
                try:
                    client = MistralClient(token.api_key, token.agent_id)
                    is_healthy = await client.check_health()
                    
                    if is_healthy:
                        await mistral_token_repo.update_status(token.api_key, True)
                        await mistral_token_repo.update_time(token.api_key, None)
                        logger.info(f"🔓 Mistral token reactivated: {token.api_key[:8]}...")
                        
                except Exception as e:
                    logger.error(f"[MISTRAL REACTIVATION ERROR] {e}")

        logger.info("🕒 Mistral check sleeping for 1 hour...")
        await asyncio.sleep(3600)  # Проверяем каждый час


if __name__ == "__main__":
    print(
        translate(
            """В американских тюрьмах остаются десятки россиян, дипломаты приложат максимум усилий для их освобождения, заявило посольство РФ в США."""
        )
    )