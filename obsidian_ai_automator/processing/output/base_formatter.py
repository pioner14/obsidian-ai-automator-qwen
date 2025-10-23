from abc import ABC, abstractmethod
from typing import Dict, Any
from obsidian_ai_automator.processing.base_processor import BaseProcessor


class BaseFormatter(BaseProcessor):
    """
    Абстрактный базовый класс для форматтеров
    """
    
    @abstractmethod
    def format(self, content: Dict[str, Any]) -> str:
        """
        Форматирует контент в соответствии с требованиями
        
        Args:
            content: Словарь с контентом для форматирования
            
        Returns:
            Отформатированный контент в виде строки
        """
        pass
    
    @abstractmethod
    def save_to_file(self, content: str, file_path: str) -> bool:
        """
        Сохраняет контент в файл
        
        Args:
            content: Контент для сохранения
            file_path: Путь к файлу для сохранения
            
        Returns:
            True если сохранение прошло успешно, иначе False
        """
        pass