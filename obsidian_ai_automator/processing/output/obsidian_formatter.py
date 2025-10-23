import os
import re
from typing import Dict, Any
from obsidian_ai_automator.processing.output.base_formatter import BaseFormatter
from obsidian_ai_automator.core.error_handler import OutputError


class ObsidianFormatter(BaseFormatter):
    """
    Реализация форматтера для вывода в формате Obsidian
    """
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Проверяет конфигурацию форматтера"""
        required_keys = ['obsidian_vault_path']
        return all(key in config for key in required_keys)
    
    def process(self, input_data: Dict[str, Any], config: Dict[str, Any]) -> str:
        """Обрабатывает данные и возвращает форматированный контент"""
        if not self.validate_config(config):
            raise ValueError("Некорректная конфигурация форматтера")
        
        return self.format(input_data)
    
    def format(self, content: Dict[str, Any]) -> str:
        """
        Форматирует контент в соответствии с требованиями Obsidian
        
        Args:
            content: Словарь с контентом для форматирования
            
        Returns:
            Отформатированный контент в виде строки
        """
        # Извлекаем данные из контента
        title = content.get('title', 'Без названия')
        tags = content.get('tags', [])
        analysis = content.get('analysis', '')
        transcript = content.get('transcript', '')
        
        # Формируем YAML frontmatter
        yaml_frontmatter = f"""---
title: {title}
tags: [{', '.join(tags)}]
---"""
        
        # Формируем тело заметки
        note_body = f"""
## Анализ

{analysis}

## Полный Транскрипт

{transcript}
"""
        
        # Комбинируем всё вместе
        formatted_content = f"{yaml_frontmatter}{note_body}"
        return formatted_content
    
    def save_to_file(self, content: str, file_path: str) -> bool:
        """
        Сохраняет контент в файл
        
        Args:
            content: Контент для сохранения
            file_path: Путь к файлу для сохранения
            
        Returns:
            True если сохранение прошло успешно, иначе False
        """
        try:
            # Создаем директорию, если она не существует
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # Определяем безопасное имя файла
            safe_filename = re.sub(r'[^\w\s-]', '', os.path.basename(file_path))
            safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
            final_file_path = os.path.join(directory, safe_filename)
            
            with open(final_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return True
        except Exception as e:
            raise OutputError(f"Ошибка при сохранении файла {file_path}: {e}")