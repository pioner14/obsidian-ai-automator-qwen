"""
Модуль для транскрибации с использованием OpenAI API
"""
import openai
import os
from typing import Dict, Any
from obsidian_ai_automator.processing.transcription.base_transcriber import BaseTranscriber
from obsidian_ai_automator.core.error_handler import TranscriptionError


class OpenAITranscriber(BaseTranscriber):
    """
    Реализация транскрибера с использованием OpenAI API
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        # Не загружаем ключ автоматически, только при необходимости
        self.client = None
    
    def _load_api_key(self) -> str:
        """Загружает API-ключ OpenAI из файла"""
        api_key_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".openai_api_key")
        if os.path.exists(api_key_file):
            with open(api_key_file, 'r') as f:
                return f.read().strip()
        else:
            raise TranscriptionError(f"Файл с API-ключом OpenAI не найден: {api_key_file}")
    
    def _ensure_client(self):
        """Проверяет, что клиент OpenAI инициализирован"""
        if not self.client:
            if not self.api_key:
                self.api_key = self._load_api_key()
            
            if not self.api_key:
                raise TranscriptionError("API-ключ OpenAI не установлен")
            
            # Инициализируем клиент OpenAI
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Проверяет конфигурацию транскрибера"""
        return True  # Для OpenAI конфигурация минимальна
    
    def process(self, input_data: str, config: Dict[str, Any]) -> str:
        """Обрабатывает файл и возвращает транскрипцию"""
        return self.transcribe(input_data)
    
    def transcribe(self, file_path: str) -> str:
        """
        Транскрибирует аудио/видео файл с помощью OpenAI Whisper API
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Текст транскрипции
        """
        self._ensure_client()
        
        try:
            with open(file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            return response
        
        except Exception as e:
            raise TranscriptionError(f"Ошибка при транскрибации с OpenAI API: {e}")
    
    def get_transcription_with_timecodes(self, file_path: str) -> str:
        """
        Транскрибирует файл с тайм-кодами (OpenAI Whisper не предоставляет тайм-коды в текстовом формате)
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Транскрипция с тайм-кодами (временная реализация без тайм-кодов)
        """
        self._ensure_client()
        
        try:
            with open(file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            return response  # Возвращаем просто текст, так как тайм-коды не поддерживаются
        
        except Exception as e:
            raise TranscriptionError(f"Ошибка при транскрибации с OpenAI API: {e}")