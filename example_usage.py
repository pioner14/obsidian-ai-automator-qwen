#!/usr/bin/env python3
"""
Пример использования новой модульной архитектуры Obsidian AI Automator
"""
import os
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from obsidian_ai_automator.core.orchestrator import ProcessingOrchestrator


def example_usage():
    """Пример использования оркестратора"""
    print("=== Пример использования новой архитектуры ===\n")
    
    try:
        # Создаем оркестратор с конфигурацией
        orchestrator = ProcessingOrchestrator()
        print("✓ Оркестратор успешно создан")
        
        # Пример обработки файла (файл не существует, но показывает структуру вызова)
        print("\nДля обработки файла используйте:")
        print("result = orchestrator.process_file('/path/to/your/video.mp4')")
        print("где '/path/to/your/video.mp4' - путь к видеофайлу для обработки")
        
        print("\nАрхитектура поддерживает:")
        print("- Модульную структуру для легкого расширения")
        print("- Обработку ошибок с типизированными исключениями")
        print("- Централизованное логирование")
        print("- Гибкую конфигурацию")
        print("- Кэширование результатов")
        
    except Exception as e:
        print(f"Ошибка в примере: {e}")
        return False
    
    print("\n✓ Пример выполнен успешно")
    return True


if __name__ == "__main__":
    success = example_usage()
    sys.exit(0 if success else 1)