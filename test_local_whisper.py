#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы с локальной моделью Whisper
"""
import os
import sys
from pathlib import Path

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from obsidian_ai_automator.processing.transcription.local_whisper_transcriber import LocalWhisperTranscriber


def test_local_whisper():
    """Тестируем локальный транскрибер Whisper"""
    print("Тестируем локальный транскрибер Whisper...")
    
    # Проверяем наличие файла для транскрибации
    if len(sys.argv) < 2:
        print("Usage: python test_local_whisper.py <path_to_audio_file>")
        return
    
    audio_file = sys.argv[1]
    
    if not os.path.exists(audio_file):
        print(f"Файл не найден: {audio_file}")
        return
    
    # Создаем экземпляр транскрибера
    transcriber = LocalWhisperTranscriber(model_size="base")  # Используем модель base для тестирования
    
    try:
        print(f"Начинаем транскрибацию файла: {audio_file}")
        transcription = transcriber.transcribe(audio_file)
        print("Транскрипция успешно завершена:")
        print(transcription)
        
        print("\nТеперь пробуем с тайм-кодами...")
        transcription_with_timecodes = transcriber.get_transcription_with_timecodes(audio_file)
        print("Транскрипция с тайм-кодами:")
        print(transcription_with_timecodes)
        
    except Exception as e:
        print(f"Ошибка при транскрибации: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_local_whisper()