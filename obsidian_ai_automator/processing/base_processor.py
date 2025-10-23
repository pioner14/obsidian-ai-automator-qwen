from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseProcessor(ABC):
    """
    Абстрактный базовый класс для всех процессоров
    """
    
    @abstractmethod
    def process(self, input_data: Any, config: Dict[str, Any]) -> Any:
        """
        Обрабатывает входные данные и возвращает результат
        
        Args:
            input_data: Входные данные для обработки
            config: Конфигурация процессора
            
        Returns:
            Результат обработки
        """
        pass
    
    @abstractmethod
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """
        Проверяет корректность конфигурации
        
        Args:
            config: Конфигурация для проверки
            
        Returns:
            True если конфигурация корректна, иначе False
        """
        pass