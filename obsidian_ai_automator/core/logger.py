import logging
from typing import Optional


class Logger:
    """
    Унифицированная система логирования
    """
    
    _instance: Optional['Logger'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'Logger':
        if cls._instance is None:
            cls._instance = super(Logger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.logger = logging.getLogger('obsidian_ai_automator')
            self._initialized = True
    
    def setup_logger(self, level: str = 'INFO', log_file: str = 'obsidian_ai_automator.log'):
        """Настраивает логгер"""
        # Преобразуем строковый уровень логирования в соответствующий уровень
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f'Invalid log level: {level}')
        
        self.logger.setLevel(numeric_level)
        
        # Создаем форматер
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Обработчик для файла
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        
        # Обработчик для консоли
        console_handler = logging.StreamHandler()
        console_handler.setLevel(numeric_level)
        console_handler.setFormatter(formatter)
        
        # Добавляем обработчики к логгеру
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str):
        """Логирует сообщение уровня DEBUG"""
        self.logger.debug(message)
    
    def info(self, message: str):
        """Логирует сообщение уровня INFO"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Логирует сообщение уровня WARNING"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Логирует сообщение уровня ERROR"""
        self.logger.error(message)
    
    def critical(self, message: str):
        """Логирует сообщение уровня CRITICAL"""
        self.logger.critical(message)