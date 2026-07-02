import asyncio
import functools
import time
from typing import Any, Callable, Optional, TypeVar

from loguru import logger

T = TypeVar("T")


def retry_async(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
):
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            current_delay = delay

            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__}: {e}"
                        )
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"All {max_retries} retries failed for {func.__name__}: {e}"
                        )

            raise last_exception

        return wrapper

    return decorator


def rate_limited(max_per_second: float = 5):
    min_interval = 1.0 / max_per_second

    def decorator(func: Callable) -> Callable:
        last_called = [0.0]

        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                await asyncio.sleep(min_interval - elapsed)
            result = await func(*args, **kwargs)
            last_called[0] = time.time()
            return result

        return wrapper

    return decorator


def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."
