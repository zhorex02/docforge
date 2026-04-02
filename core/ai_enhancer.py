"""AI text enhancement using Claude API. Only for proposals and SOWs."""

import logging
import os

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a professional business writer. Enhance the given text to be more professional, clear, and compelling. Keep the same meaning but improve the wording, structure, and tone. Output ONLY the improved text, nothing else. Do NOT add legal clauses, disclaimers, or contractual terms."""


async def enhance_text_async(text: str, context: str = "business proposal") -> str:
    """Enhance text using Claude API. Returns original text if API fails."""
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        logger.warning("No ANTHROPIC_API_KEY set, returning original text")
        return text

    try:
        import httpx
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 500,
                    "system": _SYSTEM_PROMPT,
                    "messages": [
                        {"role": "user", "content": f"Context: {context}\n\nText to improve:\n{text}"}
                    ],
                },
            )
            if response.status_code == 200:
                data = response.json()
                return data["content"][0]["text"]
            else:
                logger.warning("Claude API returned %d, using original text", response.status_code)
                return text
    except Exception as e:
        logger.warning("AI enhancement failed (%s), using original text", e)
        return text


def enhance_text(text: str, context: str = "business proposal") -> str:
    """Synchronous wrapper for enhance_text_async."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, enhance_text_async(text, context))
            return future.result(timeout=20)
    else:
        return asyncio.run(enhance_text_async(text, context))
