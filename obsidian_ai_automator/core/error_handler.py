"""
Модуль для централизованной обработки исключений
"""
from typing import Type, Callable, Any
import functools
import logging
from obsidian_ai_automator.core.logger import Logger
from obsidian_ai_automator.core.event_manager import EventManager
from obsidian_ai_automator.core.config import ConfigManager


class ProcessingError(Exception):
    """Базовое исключение для ошибок обработки"""
    pass


class TranscriptionError(ProcessingError):
    """Исключение для ошибок транскрибации"""
    pass


class AnalysisError(ProcessingError):
    """Исключение для ошибок анализа"""
    pass


class OutputError(ProcessingError):
    """Исключение для ошибок форматирования вывода"""
    pass


class ConfigError(ProcessingError):
    """Исключение для ошибок конфигурации"""
    pass


def handle_exceptions(exception_mapping: dict = None):
    """
    Декоратор для централизованной обработки исключений
    
    Args:
        exception_mapping: Словарь сопоставления исключений к обработчикам
    """
    if exception_mapping is None:
        exception_mapping = {}
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger = Logger()
                
                # Определяем тип исключения и применяем соответствующий обработчик
                exc_type = type(e)
                if exc_type in exception_mapping:
                    handler = exception_mapping[exc_type]
                    return handler(e)
                else:
                    # Логируем необработанное исключение
                    logger.error(f"Необработанное исключение в {func.__name__}: {e}")
                    raise e
        return wrapper
    return decorator


def retry_on_failure(max_attempts: int = 3, delay: float = 1.0):
    """
    Декоратор для повторных попыток выполнения функции при ошибке
    
    Args:
        max_attempts: Максимальное количество попыток
        delay: Задержка между попытками в секундах
    """
    import time
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_attempts - 1:  # Не ждем после последней попытки
                        Logger().warning(f"Ошибка в {func.__name__}, попытка {attempt + 1}/{max_attempts}: {e}")
                        time.sleep(delay)
                    else:
                        Logger().error(f"Все попытки исчерпаны для {func.__name__}: {e}")
            
            # Если все попытки не удались, поднимаем последнее исключение
            raise last_exception
        return wrapper
    return decorator


class ErrorHandler:
    """
    Класс для централизованной обработки ошибок
    """
    
    def __init__(self, config: ConfigManager = None):
        self.logger = Logger()
        self.config = config
        self.event_manager = EventManager(config) if config else None
        if self.event_manager:
            self.event_manager.add_notification_handler()
    
    def handle_transcription_error(self, error: Exception, file_path: str = None) -> None:
        """Обработка ошибки транскрибации"""
        error_msg = f"Ошибка транскрибации"
        if file_path:
            error_msg += f" файла {file_path}"
        error_msg += f": {error}"
        
        self.logger.error(error_msg)
        
        # Отправляем уведомление об ошибке
        if self.event_manager:
            self.event_manager.emit_notification(error_msg, "ERROR")
    
    def handle_analysis_error(self, error: Exception, transcript: str = None) -> None:
        """Обработка ошибки анализа"""
        error_msg = f"Ошибка анализа"
        if transcript:
            error_msg += f" транскрипции длиной {len(transcript)} символов"
        error_msg += f": {error}"
        
        self.logger.error(error_msg)
        
        # Отправляем уведомление об ошибке
        if self.event_manager:
            self.event_manager.emit_notification(error_msg, "ERROR")
    
    def handle_output_error(self, error: Exception, content: str = None) -> None:
        """Обработка ошибки форматирования вывода"""
        error_msg = f"Ошибка форматирования вывода"
        if content:
            error_msg += f" контента длиной {len(content)} символов"
        error_msg += f": {error}"
        
        self.logger.error(error_msg)
        
        # Отправляем уведомление об ошибке
        if self.event_manager:
            self.event_manager.emit_notification(error_msg, "ERROR")
    
    def handle_config_error(self, error: Exception, config_key: str = None) -> None:
        """Обработка ошибки конфигурации"""
        error_msg = f"Ошибка конфигурации"
        if config_key:
            error_msg += f" для ключа {config_key}"
        error_msg += f": {error}"
        
        self.logger.error(error_msg)
        
        # Отправляем уведомление об ошибке
        if self.event_manager:
            self.event_manager.emit_notification(error_msg, "ERROR")