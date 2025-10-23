import configparser
import os
from typing import Dict, Any


class ConfigManager:
    """
    Класс для управления конфигурацией приложения
    """
    
    def __init__(self, config_file_path: str = "config.ini"):
        """
        Инициализация ConfigManager
        :param config_file_path: путь к файлу конфигурации
        """
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser()
        
        # Если конфигурационный файл существует, загружаем его
        if os.path.exists(config_file_path):
            self.config.read(config_file_path)
        else:
            # Создаем базовую конфигурацию
            self._create_default_config()
    
    def _create_default_config(self):
        """Создает базовую конфигурацию"""
        # Секция путей
        self.config['Paths'] = {
            'watch_directory': '/home/nick/Public/ai-automator/',
            'obsidian_vault_path': '/home/nick/Obsidian Vault/Auto_Notes',
            'transcript_cache_directory': '.deepgram_cache'
        }
        
        # Секция NVIDIA API
        self.config['NVIDIA_API'] = {
            'api_url': 'https://integrate.api.nvidia.com/v1/chat/completions',
            'model': 'deepseek-ai/deepseek-v3.1-terminus'
        }
        
        # Секция фильтрации файлов
        self.config['File_Filtering'] = {
            'allowed_extensions': '.mp4, .mov, .avi, .mp3, .wav'
        }
        
        # Секция уведомлений
        self.config['Notifications'] = {
            'type': 'telegram',
            'success_notifications': 'false',
            'telegram_bot_token': '8277878393:AAF49h_lExvpw40LHyVVWJAe4dsJXw0Ai-Q',
            'telegram_chat_id': '6012855770'
        }
        
        # Секция логирования
        self.config['Logging'] = {
            'level': 'INFO'
        }
        
        # Секция LLM
        self.config['LLM'] = {
            'custom_prompt_file': 'custom_prompt.txt',
            'forbidden_tags': ''
        }
        
        # Секция обработки
        self.config['Processing'] = {
            'max_parallel_processes': '2',
            'transcription_provider': 'deepgram',
            'analysis_provider': 'nvidia',
            'output_format': 'obsidian'
        }
    
    def save_config(self):
        """Сохраняет конфигурацию в файл"""
        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)
    
    def get(self, section: str, key: str, fallback: str = None) -> str:
        """Получает значение из конфигурации"""
        return self.config.get(section, key, fallback=fallback)
    
    def getint(self, section: str, key: str, fallback: int = 0) -> int:
        """Получает целочисленное значение из конфигурации"""
        return self.config.getint(section, key, fallback=fallback)
    
    def getboolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """Получает булевое значение из конфигурации"""
        return self.config.getboolean(section, key, fallback=fallback)
    
    def set(self, section: str, key: str, value: str):
        """Устанавливает значение в конфигурации"""
        if not self.config.has_section(section):
            self.config.add_section(section)
        self.config.set(section, key, value)
    
    def get_processing_config(self) -> Dict[str, Any]:
        """Получает конфигурацию для обработки"""
        return {
            'max_parallel_processes': self.getint('Processing', 'max_parallel_processes', fallback=2),
            'transcription_provider': self.get('Processing', 'transcription_provider', fallback='deepgram'),
            'analysis_provider': self.get('Processing', 'analysis_provider', fallback='nvidia'),
            'output_format': self.get('Processing', 'output_format', fallback='obsidian')
        }
    
    def get_paths_config(self) -> Dict[str, str]:
        """Получает конфигурацию путей"""
        return {
            'watch_directory': self.get('Paths', 'watch_directory'),
            'obsidian_vault_path': self.get('Paths', 'obsidian_vault_path'),
            'transcript_cache_directory': self.get('Paths', 'transcript_cache_directory')
        }
    
    def get_api_config(self) -> Dict[str, str]:
        """Получает конфигурацию API"""
        return {
            'nvidia_api_url': self.get('NVIDIA_API', 'api_url'),
            'nvidia_model': self.get('NVIDIA_API', 'model')
        }