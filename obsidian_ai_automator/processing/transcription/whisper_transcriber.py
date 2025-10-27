"""
Модуль для транскрибации с использованием Whisper API (локальной версии)
"""
import requests
import os
from typing import Dict, Any
from obsidian_ai_automator.processing.transcription.base_transcriber import BaseTranscriber
from obsidian_ai_automator.core.error_handler import TranscriptionError


class WhisperTranscriber(BaseTranscriber):
    """
    Реализация транскрибера с использованием локального Whisper API (через Ollama или другой сервер)
    """
    
    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        # Для работы с локальным Whisper API нам не нужен API-ключ
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Проверяет конфигурацию транскрибера"""
        return True  # Для Whisper конфигурация минимальна
    
    def process(self, input_data: str, config: Dict[str, Any]) -> str:
        """Обрабатывает файл и возвращает транскрипцию"""
        return self.transcribe(input_data)
    
    def transcribe(self, file_path: str) -> str:
        """
        Транскрибирует аудио/видео файл с помощью локального Whisper API
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Текст транскрипции
        """
        try:
            with open(file_path, "rb") as audio_file:
                files = {"file": audio_file}
                response = requests.post(f"{self.api_url}/transcriptions", files=files)
                response.raise_for_status()
                
                # Ответ в формате JSON с ключом text
                result = response.json()
                if "text" in result:
                    return result["text"]
                else:
                    raise TranscriptionError(f"Непредвиденный формат ответа от Whisper API: {result}")
        
        except Exception as e:
            raise TranscriptionError(f"Ошибка при транскрибации с Whisper API: {e}")
    
    def get_transcription_with_timecodes(self, file_path: str) -> str:
        """
        Транскрибирует файл с тайм-кодами (реализация зависит от API)
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Транскрипция с тайм-кодами
        """
        try:
            with open(file_path, "rb") as audio_file:
                # Некоторые реализации Whisper API поддерживают формат srt или vtt с тайм-кодами
                files = {"file": audio_file}
                data = {"response_format": "verbose_json"}  # Пытаемся получить подробный формат с тайм-кодами
                response = requests.post(f"{self.api_url}/transcriptions", files=files, data=data)
                response.raise_for_status()
                
                result = response.json()
                
                # Если API предоставляет сегменты с тайм-кодами, форматируем их
                if "segments" in result:
                    transcription_with_timecodes = []
                    for segment in result["segments"]:
                        start_time = self._format_time(segment["start"])
                        text = segment["text"].strip()
                        transcription_with_timecodes.append(f"[{start_time}] {text}")
                    
                    return " ".join(transcription_with_timecodes)
                else:
                    # В противном случае возвращаем обычный текст
                    if "text" in result:
                        return result["text"]
                    else:
                        raise TranscriptionError(f"Непредвиденный формат ответа от Whisper API: {result}")
        
        except Exception as e:
            raise TranscriptionError(f"Ошибка при транскрибации с Whisper API: {e}")
    
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