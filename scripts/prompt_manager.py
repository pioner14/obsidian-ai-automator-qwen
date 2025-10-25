"""
Модуль для управления промптами, используемыми LLM
"""
import os
import configparser
import logging


class PromptManager:
    """
    Класс для управления промптами, используемыми LLM
    """
    
    def __init__(self, config_file_path="../config.ini"):
        """
        Инициализация PromptManager
        :param config_file_path: путь к файлу конфигурации
        """
        self.config = configparser.ConfigParser()
        config_abs_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_file_path)
        self.config.read(config_abs_path)
        
        # Загружаем настройки из конфигурации
        try:
            self.custom_prompt_file = self.config.get('LLM', 'custom_prompt_file', fallback='custom_prompt.txt')
            self.forbidden_tags = [tag.strip() for tag in self.config.get('LLM', 'forbidden_tags', fallback='').split(',') if tag.strip()]
            self.default_tags = [tag.strip() for tag in self.config.get('LLM', 'default_tags', fallback='jw, research, transcript, {NVIDIA_MODEL}').split(',') if tag.strip()]
        except configparser.NoSectionError:
            self.custom_prompt_file = 'custom_prompt.txt'
            self.forbidden_tags = []
            self.default_tags = ['jw', 'research', 'transcript', '{NVIDIA_MODEL}']
    
    def get_analysis_prompt(self, transcript, nvidia_model):
        """
        Получает промпт для анализа транскрипта с помощью LLM
        :param transcript: текст транскрипта
        :param nvidia_model: название модели NVIDIA
        :return: готовый промпт для LLM
        """
        # Загружаем пользовательский промпт из файла
        prompt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", self.custom_prompt_file)
        if os.path.exists(prompt_file_path):
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
        else:
            # Используем стандартный промпт, если файл не найден
            prompt_template = """Ты — ИИ-аналитик, помогающий исследователю. 
            Твоя задача — проанализировать предоставленную стенограмму лекции на русском языке, чтобы найти ключевые "наглядные пособия" или "примеры" и объяснения библейских стихов для дальнейшего исследования.

            **Крайне важно:**
            1. Отвечай **ТОЛЬКО НА РУССКОМ ЯЗЫКЕ**.
            2. Используй только информацию из предоставленного транскрипта. Не генерируй информацию извне и не галлюцинируй.
            3. НЕ используй следующие теги: {FORBIDDEN_TAGS}
            4. Создавай понятные теги, которые помогут легко найти информацию в Obsidian, но избегай указанных выше тегов.
            5. Внимательно относись к точности тайм-кодов и описаний примеров.

            Выполни 3 шага:
            1. **Заголовок:** Сгенерируй краткий и точный заголовок (не более 10 слов) из транскрипта. Заголовок должен быть без квадратных скобок.
            2. **Примеры:** Выдели **3-5** наиболее ярких наглядных примеров (иллюстраций) и объяснений библейских стихов, которые использовал спикер. Укажи **тайм-код** (в формате HH:MM:SS) начала каждого примера из транскрипта.
            3. **Формат:** Отформатируй ВСЕ в формат Obsidian Markdown, используя YAML Frontmatter и Callouts. **Не включай ничего, кроме запрошенного Markdown**.

            ---
            ### ТРЕБУЕМЫЙ ФОРМАТ OBSIDIAN ###
            ```markdown
            ---
            title: Твой сгенерированный заголовок
            tags: [{DEFAULT_TAGS}]
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
            {transcript}"""
        
        # Подставляем переменные в шаблон промпта
        forbidden_tags_str = ", ".join(self.forbidden_tags) if self.forbidden_tags else "нет запрещенных тегов"
        # Форматируем теги для YAML frontmatter, подставляя модель NVIDIA
        formatted_tags = []
        for tag in self.default_tags:
            if tag == "{NVIDIA_MODEL}":
                formatted_tags.append(nvidia_model)
            else:
                formatted_tags.append(tag)
        tags_str = ", ".join(formatted_tags)
        
        prompt = prompt_template.format(
            FORBIDDEN_TAGS=forbidden_tags_str,
            NVIDIA_MODEL=nvidia_model,
            transcript=transcript,
            DEFAULT_TAGS=tags_str
        )
        
        return prompt
    
    def get_custom_prompt(self):
        """
        Возвращает пользовательский промпт из файла
        :return: содержимое пользовательского промпта или None, если файл не найден
        """
        prompt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", self.custom_prompt_file)
        if os.path.exists(prompt_file_path):
            with open(prompt_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            logging.warning(f"Файл пользовательского промпта {prompt_file_path} не найден")
            return None
    
    def save_custom_prompt(self, prompt_text):
        """
        Сохраняет пользовательский промпт в файл
        :param prompt_text: текст промпта для сохранения
        """
        prompt_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", self.custom_prompt_file)
        with open(prompt_file_path, 'w', encoding='utf-8') as f:
            f.write(prompt_text)
        logging.info(f"Пользовательский промпт сохранен в {prompt_file_path}")