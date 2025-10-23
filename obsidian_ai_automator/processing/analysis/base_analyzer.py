from abc import ABC, abstractmethod
from typing import Dict, Any
from obsidian_ai_automator.processing.base_processor import BaseProcessor


class BaseAnalyzer(BaseProcessor):
    """
    Абстрактный базовый класс для анализаторов
    """
    
    @abstractmethod
    def analyze(self, transcript: str) -> str:
        """
        Анализирует транскрипт и возвращает результат
        
        Args:
            transcript: Текст транскрипции для анализа
            
        Returns:
            Результат анализа
        """
        pass
    
    @abstractmethod
    def get_analysis_with_tags(self, transcript: str) -> Dict[str, Any]:
        """
        Анализирует транскрипт и возвращает результат с тегами
        
        Args:
            transcript: Текст транскрипции для анализа
            
        Returns:
            Словарь с результатом анализа и тегами
        """
        pass