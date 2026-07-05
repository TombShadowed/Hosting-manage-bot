# Credit: Made by ShadowedTomb — Telegram: @ShadowedTomb

import time
import asyncio
from typing import Dict

_LAST_CALL: Dict[int, float] = {}
_LOCK = asyncio.Lock()

def rate_limit(seconds: float = 1.0):
    """Decorator to rate-limit handlers by `from_user.id`.

    Usage:
        @rate_limit(2.0)
        async def handler(...)
    """
    def decorator(func):
        async def wrapper(client, message, *args, **kwargs):
            uid = getattr(message.from_user, 'id', None)
            now = time.time()
            async with _LOCK:
                last = _LAST_CALL.get(uid, 0)
                if now - last < seconds:
                    try:
                        await message.reply_text('⏳ Please wait before using this command again.')
                    except Exception:
                        pass
                    return
                _LAST_CALL[uid] = now
            return await func(client, message, *args, **kwargs)
        return wrapper
    return decorator
