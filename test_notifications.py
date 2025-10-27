#!/usr/bin/env python3
"""
Тестовый скрипт для проверки новой системы уведомлений
"""
import os
import sys

# Добавляем путь к модулям
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from obsidian_ai_automator.core.notification import NotificationManager
from obsidian_ai_automator.core.config import ConfigManager


def test_notifications():
    """Тестируем систему уведомлений"""
    print("Тестируем систему уведомлений...")
    
    # Создаем экземпляр конфигурации
    config = ConfigManager()
    
    # Создаем менеджер уведомлений
    notification_manager = NotificationManager(config)
    
    # Проверяем разные типы уведомлений
    test_messages = [
        ("Тестовое уведомление INFO", "INFO"),
        ("Тестовое уведомление ERROR", "ERROR"),
        ("Тестовое уведомление WARNING", "WARNING")
    ]
    
    for message, level in test_messages:
        print(f"Отправляем {level} уведомление: {message}")
        result = notification_manager.send_notification(message, level)
        print(f"Уведомление {'успешно отправлено' if result else 'не отправлено'}")
    
    print("Тестирование завершено.")


if __name__ == "__main__":
    test_notifications()