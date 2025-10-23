#!/usr/bin/env python3
"""
Основной точка входа в приложение Obsidian AI Automator
"""
import sys
import os
from obsidian_ai_automator.core.orchestrator import ProcessingOrchestrator


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <path_to_video_or_transcript_file>")
        sys.exit(1)
    
    input_path = sys.argv[1]
    
    # Проверяем, является ли input_path директорией
    if os.path.isdir(input_path):
        # Если это директория, обрабатываем все файлы в ней
        file_paths = []
        for root, dirs, files in os.walk(input_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
        
        orchestrator = ProcessingOrchestrator()
        results = orchestrator.process_multiple_files(file_paths)
        
        print(f"Обработано файлов: {len(results)}")
        for result in results:
            print(f"Создан файл: {result}")
    else:
        # Если это отдельный файл, обрабатываем его
        orchestrator = ProcessingOrchestrator()
        result = orchestrator.process_file(input_path)
        
        if result:
            print(f"Файл успешно создан: {result}")
            sys.exit(0)
        else:
            print("Ошибка при обработке файла")
            sys.exit(1)


if __name__ == "__main__":
    main()