import requests
import os
from typing import Dict, Any
from obsidian_ai_automator.processing.analysis.base_analyzer import BaseAnalyzer
from obsidian_ai_automator.processing.analysis.prompt_manager import PromptManager
from obsidian_ai_automator.core.error_handler import AnalysisError


class NvidiaAnalyzer(BaseAnalyzer):
    """
    Реализация анализатора с использованием NVIDIA API
    """
    
    def __init__(self, api_key: str = None, api_url: str = None, model: str = None):
        self.api_key = api_key  # Оставляем None, если не передан
        self.api_url = api_url
        self.model = model
        # Не загружаем параметры автоматически, только при необходимости
        self.prompt_manager = PromptManager()
    
    def _load_api_key(self) -> str:
        """Загружает API-ключ NVIDIA из файла"""
        api_key_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".nvidia_api_key")
        if os.path.exists(api_key_file):
            with open(api_key_file, 'r') as f:
                return f.read().strip()
        else:
            raise AnalysisError(f"Файл с API-ключом NVIDIA не найден: {api_key_file}")
    
    def _load_api_url(self) -> str:
        """Загружает URL API из конфигурации"""
        # Здесь будет загрузка из централизованной конфигурации
        # Для временной реализации возвращаем стандартный URL
        return "https://integrate.api.nvidia.com/v1/chat/completions"
    
    def _load_model(self) -> str:
        """Загружает модель из конфигурации"""
        # Здесь будет загрузка из централизованной конфигурации
        # Для временной реализации возвращаем стандартную модель
        return "deepseek-ai/deepseek-v3.1-terminus"
    
    def _validate_credentials(self):
        """Проверяет валидность учетных данных"""
        # Проверяем только при необходимости, не в конструкторе
        pass
    
    def _ensure_credentials(self):
        """Проверяет, что все учетные данные установлены"""
        if not self.api_key:
            self.api_key = self._load_api_key()
            if not self.api_key:
                raise AnalysisError("API-ключ NVIDIA не установлен")
        if not self.api_url:
            self.api_url = self._load_api_url()
            if not self.api_url:
                raise AnalysisError("URL API NVIDIA не установлен")
        if not self.model:
            self.model = self._load_model()
            if not self.model:
                raise AnalysisError("Модель NVIDIA не установлена")
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Проверяет конфигурацию анализатора"""
        required_keys = ['api_key', 'api_url', 'model']
        return all(key in config for key in required_keys)
    
    def process(self, input_data: str, config: Dict[str, Any]) -> str:
        """Обрабатывает транскрипт и возвращает анализ"""
        if not self.validate_config(config):
            raise ValueError("Некорректная конфигурация анализатора")
        
        return self.analyze(input_data)
    
    def analyze(self, transcript: str) -> str:
        """
        Анализирует транскрипт и возвращает результат
        
        Args:
            transcript: Текст транскрипции для анализа
            
        Returns:
            Результат анализа
        """
        # Проверяем учетные данные перед выполнением запроса
        self._ensure_credentials()
        
        prompt = self.prompt_manager.get_analysis_prompt(transcript, self.model)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.3,
            "top_p": 0.7,
            "max_tokens": 8192,
            "stream": False
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json().get("choices")[0].get("message").get("content", "")
            return result
        except Exception as e:
            raise AnalysisError(f"Ошибка при обращении к NVIDIA API: {e}")

    def get_analysis_with_tags(self, transcript: str) -> Dict[str, Any]:
        """
        Анализирует транскрипт и возвращает результат с тегами
        
        Args:
            transcript: Текст транскрипции для анализа
            
        Returns:
            Словарь с результатом анализа и тегами
        """
        analysis_result = self.analyze(transcript)
        
        # Временная реализация - в будущем можно улучшить извлечение тегов
        return {
            "analysis": analysis_result,
            "tags": ["nvidia", "analysis", self.model.replace("/", "_")]
        }