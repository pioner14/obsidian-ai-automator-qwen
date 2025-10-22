import sys
import json
import requests
import os
import re
import time
import logging
import configparser
import hashlib

def send_notification(message, level="ERROR"):
    """Отправляет уведомления через различные каналы (email, Telegram)."""
    # Сначала логируем сообщение
    if level == "ERROR":
        logging.error(f"УВЕДОМЛЕНИЕ: {message}")
    else:
        logging.info(f"УВЕДОМЛЕНИЕ: {message}")
    
    # Загружаем настройки уведомлений из config.ini
    try:
        notification_type = config.get('Notifications', 'type', fallback='none')
        
        if notification_type == 'email':
            send_email_notification(message, level)
        elif notification_type == 'telegram':
            send_telegram_notification(message, level)
        elif notification_type != 'none':
            logging.warning(f"Неизвестный тип уведомлений: {notification_type}. Поддерживаемые типы: email, telegram, none")
    except configparser.NoSectionError:
        logging.info("Секция [Notifications] отсутствует в config.ini. Уведомления отключены.")
    except Exception as e:
        logging.error(f"Ошибка при отправке уведомления: {e}")


def send_email_notification(message, level):
    """Отправляет уведомление по электронной почте."""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    try:
        smtp_server = config.get('Notifications', 'smtp_server')
        smtp_port = config.getint('Notifications', 'smtp_port', fallback=587)
        email_addr = config.get('Notifications', 'email_address')
        email_password = config.get('Notifications', 'email_password')
        recipient_email = config.get('Notifications', 'recipient_email')
        
        msg = MIMEMultipart()
        msg['From'] = email_addr
        msg['To'] = recipient_email
        msg['Subject'] = f"Obsidian AI Automator - Уведомление ({level})"
        
        body = f"Сообщение: {message}\nУровень: {level}\nВремя: {str(time.strftime('%Y-%m-%d %H:%M:%S'))}"
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_addr, email_password)
        text = msg.as_string()
        server.sendmail(email_addr, recipient_email, text)
        server.quit()
        
        logging.info("Уведомление отправлено по email")
    except Exception as e:
        logging.error(f"Ошибка при отправке email уведомления: {e}")


def send_telegram_notification(message, level):
    """Отправляет уведомление через Telegram."""
    import requests
    
    try:
        bot_token = config.get('Notifications', 'telegram_bot_token')
        chat_id = config.get('Notifications', 'telegram_chat_id')
        
        telegram_message = f"Obsidian AI Automator - Уведомление ({level})\n\n{message}"
        telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': telegram_message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(telegram_url, data=payload)
        response.raise_for_status()
        
        logging.info("Уведомление отправлено через Telegram")
    except Exception as e:
        logging.error(f"Ошибка при отправке Telegram уведомления: {e}")

# --- КОНФИГУРАЦИЯ ---
CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.ini")
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

DEEPGRAM_API_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".deepgram_api_key")
NVIDIA_API_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".nvidia_api_key")

DEEPGRAM_API_KEY = None
if os.path.exists(DEEPGRAM_API_KEY_FILE):
    with open(DEEPGRAM_API_KEY_FILE, 'r') as f:
        DEEPGRAM_API_KEY = f.read().strip()
else:
    logging.warning(f"Файл {DEEPGRAM_API_KEY_FILE} не найден. Пожалуйста, создайте его и поместите ваш Deepgram API ключ.")

NVIDIA_API_KEY = None
if os.path.exists(NVIDIA_API_KEY_FILE):
    with open(NVIDIA_API_KEY_FILE, 'r') as f:
        NVIDIA_API_KEY = f.read().strip()
else:
    logging.warning(f"Файл {NVIDIA_API_KEY_FILE} не найден. Пожалуйста, создайте его и поместите ваш NVIDIA API ключ.")

NVIDIA_API_URL = config.get('NVIDIA_API', 'api_url')
NVIDIA_MODEL = config.get('NVIDIA_API', 'model')
OBSIDIAN_VAULT_PATH = os.path.expanduser(config.get('Paths', 'obsidian_vault_path'))
TRANSCRIPT_CACHE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", config.get('Paths', 'transcript_cache_directory'))

# Настройки для LLM
try:
    CUSTOM_PROMPT_FILE = config.get('LLM', 'custom_prompt_file', fallback='custom_prompt.txt')
    FORBIDDEN_TAGS = [tag.strip() for tag in config.get('LLM', 'forbidden_tags', fallback='').split(',') if tag.strip()]
except configparser.NoSectionError:
    CUSTOM_PROMPT_FILE = 'custom_prompt.txt'
    FORBIDDEN_TAGS = []
# ---------------------

def calculate_file_hash(file_path):
    """Вычисляет SHA-256 хеш файла для проверки дубликатов."""
    hash_sha256 = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            # Читаем файл по частям для экономии памяти
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    except Exception as e:
        logging.error(f"Ошибка при вычислении хеша файла {file_path}: {e}")
        send_notification(f"Ошибка при вычислении хеша файла {file_path}: {e}")
        return None


def check_duplicate_file(file_path):
    """Проверяет, обрабатывался ли файл ранее, используя его хеш."""
    # Получаем директорию для хранения хешей
    hash_cache_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".hash_cache")
    os.makedirs(hash_cache_dir, exist_ok=True)
    
    file_hash = calculate_file_hash(file_path)
    if not file_hash:
        return False  # Не удалось вычислить хеш, продолжаем обработку
    
    hash_file_path = os.path.join(hash_cache_dir, file_hash)
    
    if os.path.exists(hash_file_path):
        # Файл с таким хешем уже обрабатывался
        logging.info(f"Файл {file_path} уже обрабатывался ранее (найден хеш: {file_hash})")
        return True
    else:
        # Отмечаем, что файл с таким хешем теперь обрабатывается
        with open(hash_file_path, 'w') as f:
            f.write(f"Processed: {file_path} at {str(os.path.getmtime(file_path))}")
        logging.info(f"Файл {file_path} отмечен как обработанный (хеш: {file_hash})")
        return False


def transcribe_with_deepgram(video_path):
    """Транскрибирует видеофайл с помощью Deepgram API, используя кэширование."""
    if not DEEPGRAM_API_KEY:
        error_message = f"Ошибка: DEEPGRAM_API_KEY не установлен. Пожалуйста, создайте файл {DEEPGRAM_API_KEY_FILE} и поместите в него ваш ключ."
        logging.error(error_message)
        send_notification(error_message)
        sys.exit(1)

    # Создаем директорию для кэша, если ее нет
    os.makedirs(TRANSCRIPT_CACHE_DIR, exist_ok=True)

    # Генерируем имя кэш-файла на основе имени видеофайла
    video_filename = os.path.basename(video_path)
    json_cache_filename = os.path.join(TRANSCRIPT_CACHE_DIR, f"{video_filename}.json")
    text_cache_filename = os.path.join(TRANSCRIPT_CACHE_DIR, f"{video_filename}.txt")

    # Проверяем, существует ли кэшированный текстовый транскрипт
    if os.path.exists(text_cache_filename):
        logging.info(f"Используем кэшированный текстовый транскрипт для {video_filename}")
        with open(text_cache_filename, 'r', encoding='utf-8') as f:
            return f.read()

    # Проверяем, существует ли кэшированный JSON-транскрипт
    if os.path.exists(json_cache_filename):
        logging.info(f"Используем кэшированный JSON-транскрипт для {video_filename}")
        try:
            with open(json_cache_filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Извлечение полного текста из JSON для сохранения в текстовый кэш
            full_text_from_json = []
            if 'results' in data and 'channels' in data['results'] and data['results']['channels']:
                for channel in data['results']['channels']:
                    for alternative in channel['alternatives']:
                        full_text_from_json.append(alternative['transcript'])
            plain_text_transcript = " ".join(full_text_from_json).strip()

            # Сохраняем чистый текстовый транскрипт в кэш-файл
            with open(text_cache_filename, 'w', encoding='utf-8') as f:
                f.write(plain_text_transcript)
            logging.info(f"Чистый текстовый транскрипт сохранен в кэш: {text_cache_filename}")

            # Извлечение транскрипта с тайм-кодами для возврата
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
        except Exception as e:
            logging.error(f"Ошибка при чтении кэш-файла {json_cache_filename}: {e}. Повторяем транскрипцию.")
            # Если кэш-файл поврежден, удаляем его и продолжаем без него
            os.remove(json_cache_filename)

    logging.info(f"Кэшированный транскрипт для {video_filename} не найден или поврежден. Выполняем транскрипцию с Deepgram API...")

    # URL для Deepgram API
    DEEPGRAM_URL = "https://api.deepgram.com/v1/listen?punctuate=true&diarize=true&language=ru&model=nova-2"

    headers = {
        "Authorization": f"Token {DEEPGRAM_API_KEY}",
        "Content-Type": "video/mp4" # Или другой соответствующий MIME-тип видео
    }

    try:
        with open(video_path, 'rb') as video_file:
            response = requests.post(DEEPGRAM_URL, headers=headers, data=video_file)
            response.raise_for_status() # Вызывает исключение для ошибок HTTP

        data = response.json()
        
        # Сохраняем полный ответ Deepgram в кэш-файл
        with open(json_cache_filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        logging.info(f"Полный JSON-транскрипт Deepgram сохранен в кэш: {json_cache_filename}")

        # Извлечение чистого текста транскрипции для сохранения в текстовый кэш
        plain_text_transcript = ""
        if 'results' in data and 'channels' in data['results'] and data['results']['channels']:
            for channel in data['results']['channels']:
                for alternative in channel['alternatives']:
                    plain_text_transcript += alternative['transcript'] + " "
        plain_text_transcript = plain_text_transcript.strip()

        # Сохраняем чистый текстовый транскрипт в кэш-файл
        with open(text_cache_filename, 'w', encoding='utf-8') as f:
            f.write(plain_text_transcript)
        logging.info(f"Чистый текстовый транскрипт сохранен в кэш: {text_cache_filename}")

        # Извлечение транскрипта с тайм-кодами для возврата
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
        error_message = f"Ошибка при обращении к Deepgram API: {e}"
        logging.error(error_message)
        send_notification(error_message)
        sys.exit(1)
    except Exception as e:
        error_message = f"Неизвестная ошибка при транскрипции с Deepgram: {e}"
        logging.error(error_message)
        send_notification(error_message)
        sys.exit(1)

def analyze_with_nvidia_llm(transcript):
    """Отправляет транскрипт в NVIDIA API и получает структурированный Markdown."""
    if not NVIDIA_API_KEY:
        error_message = f"Ошибка: NVIDIA_API_KEY не установлен. Пожалуйста, создайте файл {NVIDIA_API_KEY_FILE} и поместите в него ваш ключ."
        logging.error(error_message)
        send_notification(error_message)
        sys.exit(1)
    prompt = f"""Ты — ИИ-аналитик, помогающий исследователю из Общества Сторожевой Башни. 
    Твоя задача — проанализировать предоставленную стенограмму лекции на русском языке, чтобы найти ключевые "наглядные пособия" или "примеры" и объяснения библейских стихов для дальнейшего исследования.
    **Крайне важно:**
    1. Отвечай **ТОЛЬКО НА РУССКОМ ЯЗЫКЕ**.
    2. Используй только информацию из предоставленного транскрипта. Не генерируй информацию извне и не галлюцинируй.

    Выполни 3 шага:
    1. **Заголовок:** Сгенерируй краткий и точный заголовок (не более 10 слов) из транскрипта. Заголовок должен быть без квадратных скобок.
    2. **Примеры:** Выдели **3-5** наиболее ярких наглядных примеров (иллюстраций) и объяснений библейских стихов, которые использовал спикер. Укажи **тайм-код** (в формате HH:MM:SS) начала каждого примера из транскрипта.
    3. **Формат:** Отформатируй ВСЕ в формат Obsidian Markdown, используя YAML Frontmatter и Callouts. Добавь к каждому примеру **понятные теги**, которые помогут легко найти его в Obsidian (например, #БиблейскийПример, #НаглядноеПособие, #ОбъяснениеСтиха). **Не включай ничего, кроме запрошенного Markdown**.

    ---
    ### ТРЕБУЕМЫЙ ФОРМАТ OBSIDIAN ###
    ```markdown
    ---
    title: Твой сгенерированный заголовок
    tags: [jw, research, transcript, {NVIDIA_MODEL}]
    ---

    ## Анализ: Ключевые Примеры (Наглядные Пособия)

    > [!example|collapse open] [Название Примера, HH:MM:SS] #Тег1 #Тег2
    > [Твой краткий пересказ Примера, должен быть коротким]

    > [!example|collapse open] [Название Второго Примера, HH:MM:SS] #Тег3
    > [Твой краткий пересказ Второго Примера, должен быть коротким]
    
    ## Полный Транскрипт
    ```
    ---
    
    ### ТРАНСКРИПТ ДЛЯ АНАЛИЗА:
    {transcript}
    """
    
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "model": NVIDIA_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "top_p": 0.7,
        "max_tokens": 8192,
        "stream": False
    }

    try:
        response = requests.post(NVIDIA_API_URL, headers=headers, json=data)
        response.raise_for_status()
        return response.json().get('choices')[0].get('message').get('content', '')
    except Exception as e:
        error_message = f"Ошибка при обращении к NVIDIA API: {e}"
        logging.error(error_message)
        send_notification(error_message)
        return f"Error communicating with NVIDIA API: {e}"

def main():
    # Получаем уровень логирования из конфигурации
    log_level_str = config.get('Logging', 'level', fallback='INFO')
    log_level = getattr(logging, log_level_str.upper(), logging.INFO)
    
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler("ai_analyzer.log"),
                            logging.StreamHandler(sys.stderr)
                        ])
    logging.info("Запуск скрипта ai_analyzer.py")
    if len(sys.argv) < 2:
        print("Usage: python ai_analyzer.py <path_to_video_or_transcript_file>")
        sys.exit(1)

    input_path = sys.argv[1]
    
    # Проверяем, обрабатывался ли файл ранее
    if check_duplicate_file(input_path):
        logging.info(f"Файл {input_path} уже был обработан ранее. Пропускаем.")
        print(f"Файл {input_path} уже был обработан ранее. Пропускаем.")
        sys.exit(0)
    
    file_extension = os.path.splitext(input_path)[1].lower()

    allowed_video_extensions = config.get('File_Filtering', 'allowed_extensions', fallback='').split(',')
    allowed_video_extensions = [ext.strip() for ext in allowed_video_extensions if ext.strip()]
    
    is_video_file = False
    for ext in allowed_video_extensions:
        if file_extension == ext:
            is_video_file = True
            break

    transcript_with_timecodes = ""
    if is_video_file:
        logging.info(f"Начало транскрипции видео с Deepgram API: {input_path}...")
        transcript_with_timecodes = transcribe_with_deepgram(input_path)
        logging.info("Транскрипция завершена.")
    elif file_extension == '.txt':
        logging.info(f"Используем предоставленный текстовый файл как транскрипт: {input_path}...")
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                transcript_with_timecodes = f.read()
            logging.info("Транскрипт успешно прочитан из файла.")
        except Exception as e:
            error_message = f"Ошибка при чтении файла транскрипта {input_path}: {e}"
            logging.error(error_message)
            send_notification(error_message)
            sys.exit(1)
    else:
        error_message = f"Неподдерживаемый тип входного файла: {input_path}. Ожидается видеофайл или текстовый файл транскрипта."
        logging.error(error_message)
        send_notification(error_message)
        sys.exit(1)
    
    if not transcript_with_timecodes:
        error_message = "Ошибка: Транскрипция не удалась или вернула пустой результат."
        logging.error(error_message)
        send_notification(error_message)
        sys.exit(1)

    logging.info("Начало анализа LLM (NVIDIA API)...")
    markdown_output = analyze_with_nvidia_llm(transcript_with_timecodes)
    logging.info("Анализ LLM (NVIDIA API) завершен.")
    
    if markdown_output.startswith("Error"):
        error_message = f"Ошибка LLM-анализа: {markdown_output}"
        logging.error(error_message)
        send_notification(error_message)
        sys.exit(1)

    title_line = next((line for line in markdown_output.split('\n') if line.startswith('title:')), None)
    if title_line:
        file_title = title_line.split('title:')[1].strip()
        safe_filename = re.sub(r'[^\w\s-]', '', file_title).strip()
        safe_filename = re.sub(r'[-\s]+', '_', safe_filename)
        filename = f"{safe_filename}.md"
    else:
        base_name = os.path.basename(input_path)
        if is_video_file:
            filename = f"LLM_Analysis_{base_name.replace(file_extension, '.md')}"
        else: # .txt file
            filename = f"LLM_Analysis_{base_name.replace('.txt', '.md')}"

    output_path = os.path.join(OBSIDIAN_VAULT_PATH, filename)
    os.makedirs(OBSIDIAN_VAULT_PATH, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(markdown_output)

    logging.info(f"Успех. Obsidian заметка создана: {output_path}")
    print(output_path)  # Выводим путь к созданному файлу для bash-скрипта
    return output_path

if __name__ == "__main__":
    main()
