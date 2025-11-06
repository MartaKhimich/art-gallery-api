import functools
import logging
from typing import Any, Callable

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"app.{name}")

def log_execution(logger_name: str = None):
    def decorator(func: Callable) -> Callable:
        logger = get_logger(logger_name or func.__module__)
        
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger.info(f"🚀 Начало выполнения {func.__name__}")
            
            try:
                result = await func(*args, **kwargs)
                logger.info(f"✅ Успешное завершение {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"❌ Ошибка в {func.__name__}: {str(e)}", exc_info=True)
                raise
        
        @functools.wraps(func)  
        def sync_wrapper(*args, **kwargs):
            logger.info(f"🚀 Начало выполнения {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                logger.info(f"✅ Успешное завершение {func.__name__}")
                return result
            except Exception as e:
                logger.error(f"❌ Ошибка в {func.__name__}: {str(e)}", exc_info=True)
                raise
        
        if func.__code__.co_flags & 0x80: 
            return async_wrapper
        else:
            return sync_wrapper
            
    return decorator