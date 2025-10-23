import json
import requests
import os
from typing import Dict, Any
from obsidian_ai_automator.processing.transcription.base_transcriber import BaseTranscriber
from obsidian_ai_automator.core.error_handler import TranscriptionError


class DeepgramTranscriber(BaseTranscriber):
    """
    Реализация транскрибера с использованием Deepgram API
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key  # Оставляем None, если не передан
        # Не загружаем ключ автоматически, только при необходимости
    
    def _load_api_key(self) -> str:
        """Загружает API-ключ Deepgram из файла"""
        api_key_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".deepgram_api_key")
        if os.path.exists(api_key_file):
            with open(api_key_file, 'r') as f:
                return f.read().strip()
        else:
            raise TranscriptionError(f"Файл с API-ключом Deepgram не найден: {api_key_file}")
    
    def _validate_api_key(self):
        """Проверяет валидность API-ключа"""
        # Проверяем только при необходимости, не в конструкторе
        pass
    
    def _ensure_api_key(self):
        """Проверяет, что API-ключ установлен, и если нет - пытается загрузить"""
        if not self.api_key:
            self.api_key = self._load_api_key()
            if not self.api_key:
                raise TranscriptionError("API-ключ Deepgram не установлен")
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Проверяет конфигурацию транскрибера"""
        required_keys = ['api_key', 'model', 'language']
        return all(key in config for key in required_keys)
    
    def process(self, input_data: str, config: Dict[str, Any]) -> str:
        """Обрабатывает файл и возвращает транскрипцию"""
        if not self.validate_config(config):
            raise ValueError("Некорректная конфигурация транскрибера")
        
        return self.transcribe(input_data)
    
    def transcribe(self, file_path: str) -> str:
        """
        Транскрибирует аудио/видео файл
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Текст транскрипции
        """
        # Проверяем API-ключ перед выполнением запроса
        self._ensure_api_key()
        
        # URL для Deepgram API
        model = "nova-2"  # по умолчанию
        language = "ru"   # по умолчанию
        
        DEEPGRAM_URL = f"https://api.deepgram.com/v1/listen?punctuate=true&diarize=true&language={language}&model={model}"

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "video/mp4"  # или другой соответствующий MIME-тип видео
        }

        try:
            with open(file_path, 'rb') as audio_file:
                response = requests.post(DEEPGRAM_URL, headers=headers, data=audio_file)
                response.raise_for_status()

            data = response.json()
            
            # Извлечение текста транскрипции
            if 'results' in data and 'channels' in data['results'] and data['results']['channels']:
                transcript = ""
                for channel in data['results']['channels']:
                    for alternative in channel['alternatives']:
                        transcript += alternative['transcript'] + " "
                return transcript.strip()
            else:
                raise TranscriptionError("Транскрипция не найдена в ответе Deepgram")
                
        except requests.exceptions.RequestException as e:
            raise TranscriptionError(f"Ошибка при обращении к Deepgram API: {e}")
        except Exception as e:
            raise TranscriptionError(f"Неизвестная ошибка при транскрипции с Deepgram: {e}")

    def get_transcription_with_timecodes(self, file_path: str) -> str:
        """
        Транскрибирует файл с тайм-кодами
        
        Args:
            file_path: Путь к файлу для транскрибации
            
        Returns:
            Транскрипция с тайм-кодами
        """
        # Проверяем API-ключ перед выполнением запроса
        self._ensure_api_key()
        
        # URL для Deepgram API
        model = "nova-2"  # по умолчанию
        language = "ru"   # по умолчанию
        
        DEEPGRAM_URL = f"https://api.deepgram.com/v1/listen?punctuate=true&diarize=true&language={language}&model={model}&paragraphs=true"

        headers = {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "video/mp4"  # или другой соответствующий MIME-тип видео
        }

        try:
            with open(file_path, 'rb') as audio_file:
                response = requests.post(DEEPGRAM_URL, headers=headers, data=audio_file)
                response.raise_for_status()

            data = response.json()
            
            # Извлечение транскрипта с тайм-кодами
            full_text_with_timecodes = []
            if 'results' in data and 'channels' in data['results'] and data['results']['channels']:
                for channel in data['results']['channels']:
                    for alternative in channel['alternatives']:
                        for word_info in alternative['words']:
                            start_time = str(int(word_info['start'] // 3600)).zfill(2) + ':' + \
                                         str(int((word_info['start'] % 3600) // 60)).zfill(2) + ':' + \
                                         str(int(word_info['start'] % 60)).zfill(2)
                            full_text_with_timecodes.append(f"[{start_time}] {word_info['word'].strip()}")
            
            return " ".join(full_text_with_timecodes)
                
        except requests.exceptions.RequestException as e:
            raise TranscriptionError(f"Ошибка при обращении к Deepgram API: {e}")
        except Exception as e:
            raise TranscriptionError(f"Неизвестная ошибка при транскрипции с Deepgram: {e}")