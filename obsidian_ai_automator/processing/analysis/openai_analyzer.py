"""
Модуль для анализа с использованием OpenAI API
"""
import openai
import os
from typing import Dict, Any
from obsidian_ai_automator.processing.analysis.base_analyzer import BaseAnalyzer
from obsidian_ai_automator.processing.analysis.prompt_manager import PromptManager
from obsidian_ai_automator.core.error_handler import AnalysisError


class OpenAIAnalyzer(BaseAnalyzer):
    """
    Реализация анализатора с использованием OpenAI API
    """
    
    def __init__(self, api_key: str = None, model: str = "gpt-3.5-turbo"):
        self.api_key = api_key
        self.model = model
        # Не загружаем параметры автоматически, только при необходимости
        self.client = None
        self.prompt_manager = PromptManager()
    
    def _load_api_key(self) -> str:
        """Загружает API-ключ OpenAI из файла"""
        api_key_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".openai_api_key")
        if os.path.exists(api_key_file):
            with open(api_key_file, 'r') as f:
                return f.read().strip()
        else:
            raise AnalysisError(f"Файл с API-ключом OpenAI не найден: {api_key_file}")
    
    def _ensure_client(self):
        """Проверяет, что клиент OpenAI инициализирован"""
        if not self.client:
            if not self.api_key:
                self.api_key = self._load_api_key()
            
            if not self.api_key:
                raise AnalysisError("API-ключ OpenAI не установлен")
            
            # Инициализируем клиент OpenAI
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Проверяет конфигурацию анализатора"""
        return True  # Для OpenAI конфигурация минимальна
    
    def process(self, input_data: str, config: Dict[str, Any]) -> str:
        """Обрабатывает транскрипт и возвращает анализ"""
        return self.analyze(input_data)
    
    def analyze(self, transcript: str) -> str:
        """
        Анализирует транскрипт и возвращает результат
        Args:
            transcript: Текст транскрипции для анализа
        Returns:
            Результат анализа
        """
        self._ensure_client()
        
        prompt = self.prompt_manager.get_analysis_prompt(transcript, self.model)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048
            )
            
            result = response.choices[0].message.content
            return result
        except Exception as e:
            raise AnalysisError(f"Ошибка при обращении к OpenAI API: {e}")
    
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
            "tags": ["openai", "analysis", self.model.replace("-", "_")]
        }