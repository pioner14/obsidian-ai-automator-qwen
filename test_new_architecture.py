#!/usr/bin/env python3
"""
Тестирование новой модульной архитектуры Obsidian AI Automator
"""
import os
import tempfile
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from obsidian_ai_automator.core.orchestrator import ProcessingOrchestrator
from obsidian_ai_automator.processing.transcription.deepgram_transcriber import DeepgramTranscriber
from obsidian_ai_automator.processing.analysis.nvidia_analyzer import NvidiaAnalyzer
from obsidian_ai_automator.processing.output.obsidian_formatter import ObsidianFormatter


def test_transcriber_creation():
    """Тестируем создание транскрибера"""
    try:
        # Создаем транскрибер без API-ключа - должно пройти успешно
        # API-ключ будет запрошен только при вызове методов
        transcriber = DeepgramTranscriber(api_key=None)
        print("✓ Транскрибер успешно создан без API-ключа")
        return True
    except Exception as e:
        print(f"✗ Ошибка при создании транскрибера: {e}")
        return False


def test_analyzer_creation():
    """Тестируем создание анализатора"""
    try:
        # Создаем анализатор без API-ключа - должно пройти успешно
        # API-ключ будет запрошен только при вызове методов
        analyzer = NvidiaAnalyzer(api_key=None)
        print("✓ Анализатор успешно создан без API-ключа")
        return True
    except Exception as e:
        print(f"✗ Ошибка при создании анализатора: {e}")
        return False


def test_formatter_creation():
    """Тестируем создание форматтера"""
    try:
        formatter = ObsidianFormatter()
        print("✓ Форматтер успешно создан")
        return True
    except Exception as e:
        print(f"✗ Ошибка при создании форматтера: {e}")
        return False


def test_config_loading():
    """Тестируем загрузку конфигурации"""
    try:
        orchestrator = ProcessingOrchestrator()
        print("✓ Оркестратор успешно создан с конфигурацией")
        return True
    except Exception as e:
        print(f"✗ Ошибка при создании оркестратора: {e}")
        return False


def run_all_tests():
    """Запускаем все тесты"""
    print("=== Тестирование новой архитектуры Obsidian AI Automator ===\n")
    
    tests = [
        ("Создание транскрибера", test_transcriber_creation),
        ("Создание анализатора", test_analyzer_creation),
        ("Создание форматтера", test_formatter_creation),
        ("Загрузка конфигурации", test_config_loading)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Тест: {test_name}")
        result = test_func()
        results.append((test_name, result))
        print()
    
    print("=== Результаты тестирования ===")
    passed = 0
    for test_name, result in results:
        status = "✓ ПРОЙДЕН" if result else "✗ НЕ ПРОЙДЕН"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nПройдено: {passed}/{len(results)} тестов")
    
    if passed == len(results):
        print("🎉 Все тесты пройдены успешно!")
        return True
    else:
        print("⚠️  Некоторые тесты не пройдены")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)