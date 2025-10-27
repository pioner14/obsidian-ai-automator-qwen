"""
Модуль для транскрибации с использованием Ollama API (OpenAI-совместимое)
"""
import openai
import os
from typing import Dict, Any
from obsidian_ai_automator.processing.transcription.base_transcriber import BaseTranscriber
from obsidian_ai_automator.core.error_handler import TranscriptionError


class OllamaTranscriber(BaseTranscriber):
    """
    Реализация транскрибера с использованием Ollama API через OpenAI-совместимый интерфейс
    """
    
    def __init__(self, api_url: str = "http://localhost:11434"):
        self.api_url = api_url.rstrip('/')
        # Для Ollama не нужен API-ключ, но мы устанавливаем фиктивный, т.к. openai требует его
        self.client = openai.OpenAI(
            base_url=f"{self.api_url}/v1",
            api_key="ollama"  # Произвольный ключ для OpenAI клиента, т.к. Ollama не требует ключ
        )
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Проверяет конфигурацию транскрибера"""
        return True  # Для Ollama конфигурация минимальна
    
    def process(self, input_data: str, config: Dict[str, Any]) -> str:
        """Обрабатывает файл и возвращает транскрипцию"""
        return self.transcribe(input_data)
    
    def transcribe(self, file_path: str) -> str:
        """
        Транскрибирует аудио/видео файл с помощью Ollama API
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Текст транскрипции
        """
        try:
            with open(file_path, "rb") as audio_file:
                response = self.client.audio.transcriptions.create(
                    model="whisper:latest",  # или другая подходящая модель
                    file=audio_file,
                    response_format="text"
                )
            
            return response
        
        except Exception as e:
            raise TranscriptionError(f"Ошибка при транскрибации с Ollama API: {e}")
    
    def get_transcription_with_timecodes(self, file_path: str) -> str:
        """
        Транскрибирует файл с тайм-кодами (реализация зависит от API)
        Для Ollama тайм-коды не поддерживаются напрямую
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Транскрипция с тайм-кодами (временная реализация без тайм-кодов)
        """
        # Ollama API с whisper не предоставляет тайм-коды, возвращаем обычную транскрипцию
        return self.transcribe(file_path)