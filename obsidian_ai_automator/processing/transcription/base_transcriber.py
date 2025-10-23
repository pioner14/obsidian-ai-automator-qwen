from abc import ABC, abstractmethod
from typing import Dict, Any
from obsidian_ai_automator.processing.base_processor import BaseProcessor


class BaseTranscriber(BaseProcessor):
    """
    Абстрактный базовый класс для транскриберов
    """
    
    @abstractmethod
    def transcribe(self, file_path: str) -> str:
        """
        Транскрибирует аудио/видео файл
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Текст транскрипции
        """
        pass
    
    @abstractmethod
    def get_transcription_with_timecodes(self, file_path: str) -> str:
        """
        Транскрибирует файл с тайм-кодами
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Транскрипция с тайм-кодами
        """
        pass