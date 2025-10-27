"""
Модуль для транскрибации с использованием локальной модели Whisper
"""
import os
from typing import Dict, Any
from obsidian_ai_automator.processing.transcription.base_transcriber import BaseTranscriber
from obsidian_ai_automator.core.error_handler import TranscriptionError


class LocalWhisperTranscriber(BaseTranscriber):
    """
    Реализация транскрибера с использованием локальной модели Whisper
    """
    
    def __init__(self, model_size: str = "base"):
        # Инициализируем модель при первом использовании, чтобы избежать долгой инициализации при импорте
        self._model = None
        self.model_size = model_size
    
    def _load_model(self):
        """Загружает модель whisper при необходимости"""
        try:
            import whisper
            if self._model is None:
                self._model = whisper.load_model(self.model_size)
        except ImportError:
            raise TranscriptionError("Библиотека 'whisper' не установлена. Установите её с помощью 'pip install openai-whisper'")
        except Exception as e:
            raise TranscriptionError(f"Ошибка при загрузке модели Whisper: {e}")
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Проверяет конфигурацию транскрибера"""
        return True  # Для локального Whisper конфигурация минимальна
    
    def process(self, input_data: str, config: Dict[str, Any]) -> str:
        """Обрабатывает файл и возвращает транскрипцию"""
        return self.transcribe(input_data)
    
    def transcribe(self, file_path: str) -> str:
        """
        Транскрибирует аудио/видео файл с помощью локальной модели Whisper
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Текст транскрипции
        """
        try:
            self._load_model()
            
            # Транскрибируем аудио
            result = self._model.transcribe(file_path)
            return result["text"]
        
        except Exception as e:
            raise TranscriptionError(f"Ошибка при транскрибации с локальной моделью Whisper: {e}")
    
    def get_transcription_with_timecodes(self, file_path: str) -> str:
        """
        Транскрибирует файл с тайм-кодами
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Транскрипция с тайм-кодами
        """
        try:
            self._load_model()
            
            # Транскрибируем аудио с тайм-кодами
            result = self._model.transcribe(file_path, word_timestamps=True)
            
            transcription_with_timecodes = []
            for segment in result["segments"]:
                start_time = self._format_time(segment["start"])
                text = segment["text"].strip()
                transcription_with_timecodes.append(f"[{start_time}] {text}")
            
            return " ".join(transcription_with_timecodes)
        
        except Exception as e:
            raise TranscriptionError(f"Ошибка при транскрибации с локальной моделью Whisper: {e}")
    
    def _format_time(self, seconds: float) -> str:
        """
        Преобразует время в секундах в формат HH:MM:SS
        
        Args:
            seconds: Время в секундах
            
        Returns:
            Время в формате HH:MM:SS
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"