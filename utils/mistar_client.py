import aiohttp
import asyncio
import json
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MistralClient:
    def __init__(self, api_key: str, agent_id: str):
        self.api_key = api_key
        self.agent_id = agent_id
        self.base_url = "https://api.mistral.ai/v1/agents/completions"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

    async def translate(self, text: str, target_language: str) -> Optional[str]:
        """
        Переводит текст на указанный язык через Mistral API
        """
        prompt = f"переведи текст на {target_language} без объяснения"
        
        # ❌ УБИРАЕМ temperature при работе с агентами!
        payload = {
            "agent_id": self.agent_id,
            "messages": [
                {
                    "role": "user",
                    "content": f"{prompt}\n\n{text}"
                }
            ],
            # "temperature": 0.1,  # ❌ Эту строку удаляем!
            "max_tokens": 2000
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        translated_text = data.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
                        logger.info(f"✅ Mistral translation successful: {self.api_key[:8]}...")
                        return translated_text
                    elif response.status == 429:
                        logger.warning(f"🚫 Mistral rate limit exceeded: {self.api_key[:8]}...")
                        raise MistralRateLimitError("Rate limit exceeded")
                    elif response.status == 401:
                        logger.error(f"❌ Mistral authentication failed: {self.api_key[:8]}...")
                        raise MistralAuthError("Authentication failed")
                    else:
                        error_text = await response.text()
                        logger.error(f"❌ Mistral API error {response.status}: {error_text}")
                        raise MistralAPIError(f"API error {response.status}: {error_text}")
                        
        except asyncio.TimeoutError:
            logger.error(f"⏱️ Mistral API timeout: {self.api_key[:8]}...")
            raise MistralTimeoutError("API request timeout")
        except aiohttp.ClientError as e:
            logger.error(f"🔌 Mistral connection error: {str(e)}")
            raise MistralConnectionError(f"Connection error: {str(e)}")
        except Exception as e:
            logger.error(f"❌ Unexpected Mistral error: {str(e)}")
            raise MistralAPIError(f"Unexpected error: {str(e)}")

    async def check_health(self) -> bool:
        """
        Проверяет работоспособность API ключа
        """
        try:
            result = await self.translate("Hello", "ru")
            return result is not None
        except Exception:
            return False


class MistralRateLimitError(Exception):
    pass


class MistralAuthError(Exception):
    pass


class MistralAPIError(Exception):
    pass


class MistralTimeoutError(Exception):
    pass


class MistralConnectionError(Exception):
    pass