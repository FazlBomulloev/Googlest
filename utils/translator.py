# -- 1.0.0
import asyncio
import datetime
import logging

from deepl.exceptions import QuotaExceededException, AuthorizationException

import deepl

from core.repositories.token import token_repo

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


async def translate(text: str, lang: str = "EN-US"):
    mess = ""
    tokens = await token_repo.get_all()
    result = None
    deepl_langs = [
        "BG",
        "CS",
        "DA",
        "DE",
        "EL",
        "EN",
        "EN-GB",
        "EN-US",
        "ES",
        "ET",
        "FI",
        "FR",
        "HU",
        "ID",
        "IT",
        "JA",
        "KO",
        "LT",
        "LV",
        "NB",
        "NL",
        "PL",
        "PT",
        "PT-BR",
        "PT-PT",
        "RO",
        "SK",
        "SL",
        "SV",
        "TR",
        "UK",
        "ZH",
        "RU",
    ]
    if lang in deepl_langs:
        if tokens == []:
            raise Exception("There are no deepl tokens")
        for token in tokens:
            try:
                result = (
                    deepl.Translator(token.token, proxy=proxy)
                    .translate_text(text, target_lang=lang)
                    .text
                )
                break
            except QuotaExceededException as e:
                unblock_time = datetime.datetime.now() + datetime.timedelta(days=10)
                await token_repo.update_time(token.token, unblock_time)
                await token_repo.update_status(token.token, False)
                logger.warning(
                    f"🚫 Token quota exceeded: {token.token[:8]}... Blocked until {unblock_time}"
                )
                print("Deepl tokens are rate limit\n", e)
                continue
            except AuthorizationException as e:
                await token_repo.del_token(token.token)
                print(f"Deepl tokens are invalid: {token.token}]\n", e)
                continue
            except Exception as e:
                print(f"Eror in: main.translate\n", e)
                continue
        else:
            print("Deepl tokens are invalid 1")
    else:
        print("Deepl tokens are invalid 2")
    return result


async def check_deepl():
    while True:
        logger.info("🔍 Starting token check")
        tokens = await token_repo.get_all()

        for token in tokens:
            try:
                deepl.Translator(token.token).get_usage()
                await token_repo.update_time(token.token, None)
                await token_repo.update_status(token.token, True)
                logger.info(f"✅ Token valid: {token.token[:8]}...")
            except deepl.QuotaExceededException:
                token_time = await token_repo.get_time_by_token(token.token)

                if token_time is not None:
                    logger.info(f"⏳ Token already blocked: {token.token[:8]}...")
                    continue

                unblock_time = datetime.datetime.now() + datetime.timedelta(days=10)
                await token_repo.update_time(token.token, unblock_time)
                await token_repo.update_status(token.token, False)
                logger.warning(
                    f"🚫 Token quota exceeded: {token.token[:8]}... Blocked until {unblock_time}"
                )
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
                    logger.info(f"🔓 Token reactivated: {token.token[:8]}...")
                except deepl.AuthorizationException:
                    await token_repo.del_token(token.token)
                    logger.warning(f"❌ Token deleted (invalid): {token.token[:8]}...")
                except Exception as e:
                    logger.error(f"[SECOND PASS ERROR] {e}")

        logger.info("🕒 Sleeping for 24 hours...")
        await asyncio.sleep(86400)


if __name__ == "__main__":
    print(
        translate(
            """В американских тюрьмах остаются десятки россиян, дипломаты приложат максимум усилий для их освобождения, заявило посольство РФ в США."""
        )
    )
