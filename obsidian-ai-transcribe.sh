#!/bin/bash
# Скрипт-обертка для автоматизации:

INPUT_VIDEO=$1

if [ -z "$INPUT_VIDEO" ]; then
    echo "Usage: $0 /path/to/video.mp4"
    exit 1
fi

# Проверяем существование входного файла
if [ ! -f "$INPUT_VIDEO" ]; then
    echo "Ошибка: Входной файл не найден: $INPUT_VIDEO"
    exit 1
fi

# Получаем имя файла без пути для логирования
INPUT_FILENAME=$(basename "$INPUT_VIDEO")
echo "Начинаем обработку файла: $INPUT_FILENAME"

# 1. Транскрипция с Deepgram API и анализ LLM (NVIDIA API) и запись в Obsidian
echo "-> 1/2: Транскрипция (Deepgram API) и анализ LLM (NVIDIA API) и запись в Obsidian..."
PYTHON_SCRIPT_PATH="$(pwd)/scripts/ai_analyzer.py" 

# Запускаем Python скрипт и сохраняем результат и код возврата
OUTPUT=$(source venv/bin/activate && python "$PYTHON_SCRIPT_PATH" "$INPUT_VIDEO" 2>&1)
EXIT_CODE=$?

# Проверяем успешность выполнения и наличие пути к созданному файлу
if [ $EXIT_CODE -eq 0 ]; then
    # Извлекаем путь к созданному файлу из вывода (предполагаем, что он в последней строке или содержит путь)
    CREATED_MARKDOWN_PATH=$(echo "$OUTPUT" | tail -n 1)
    
    # Проверяем, что путь к файлу выглядит правильно (содержит .md и путь к Obsidian)
    if [[ "$CREATED_MARKDOWN_PATH" == *".md"* && -f "$CREATED_MARKDOWN_PATH" ]]; then
        echo "Markdown файл успешно создан: $CREATED_MARKDOWN_PATH"
        echo "-> 2/2: Удаление исходного файла: $INPUT_VIDEO"
        
        # Удаляем исходный файл
        if rm "$INPUT_VIDEO"; then
            echo "Исходный файл успешно удален: $INPUT_VIDEO"
        else
            echo "Ошибка: Не удалось удалить исходный файл: $INPUT_VIDEO"
            exit 1
        fi
    else
        echo "Ошибка: Созданный Markdown файл не найден или путь некорректен: $CREATED_MARKDOWN_PATH"
        echo "Вывод Python скрипта: $OUTPUT"
        exit 1
    fi
else
    echo "Ошибка при выполнении Python скрипта. Код возврата: $EXIT_CODE"
    echo "Вывод Python скрипта: $OUTPUT"
    exit $EXIT_CODE
fi

echo "Готово. Заметка синхронизирована через Syncthing."