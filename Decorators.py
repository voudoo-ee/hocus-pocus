import functools
import logging
import time
from typing import Callable, Any


# Decorator to calculate time taken by a function
def timer(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        logger = logging.getLogger("timer")
        start = time.time()
        func(*args, **kwargs)
        end = time.time()
        t = round(end - start)
        logger.info(f'{func.__name__} ran for {parse_time(t)}.')

    return wrapper


def parse_time(t: int) -> str:
    if t < 60:
        return f'{t}s'
    elif t < 3600:
        return f'{t // 60}m {t % 60}s'
    else:
        return f'{t // 3600}h {(t % 3600) // 60}m {(t % 3600) % 60}s'
