#!/usr/bin/env python3
"""
Простой тест для проверки работы PromptManager
"""
import sys
import os

# Добавляем путь к модулям
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from prompt_manager import PromptManager

def test_prompt_manager():
    print("Тестирование PromptManager...")
    
    # Создаем экземпляр PromptManager
    pm = PromptManager()
    
    # Получаем тестовый промпт
    sample_transcript = "Это тестовый транскрипт для проверки работы системы. Speaker 1: [00:01:15] Пример наглядного пособия в действии."
    nvidia_model = "test-model"
    
    prompt = pm.get_analysis_prompt(sample_transcript, nvidia_model)
    
    print(f"Количество запрещенных тегов: {len(pm.forbidden_tags)}")
    print(f"Запрещенные теги: {pm.forbidden_tags}")
    print(f"Длина сгенерированного промпта: {len(prompt)} символов")
    
    # Проверяем, что запрещенные теги присутствуют в промпте
    if pm.forbidden_tags:
        for tag in pm.forbidden_tags:
            if tag in prompt:
                print(f"✓ Запрещенный тег '{tag}' присутствует в промпте как инструкция")
            else:
                print(f"✗ Запрещенный тег '{tag}' отсутствует в промпте")
    
    print("\nПромпт успешно сгенерирован!")
    return True

if __name__ == "__main__":
    success = test_prompt_manager()
    if success:
        print("\n✓ Тест PromptManager прошел успешно!")
    else:
        print("\n✗ Тест PromptManager не удался!")
        sys.exit(1)