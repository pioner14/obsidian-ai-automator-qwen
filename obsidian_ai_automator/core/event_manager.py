from typing import Callable, Dict, List, Any
from obsidian_ai_automator.core.logger import Logger
from obsidian_ai_automator.core.notification import NotificationManager
from obsidian_ai_automator.core.config import ConfigManager


class EventManager:
    """
    Система управления событиями и уведомлениями
    """
    
    def __init__(self, config: ConfigManager = None):
        self._subscribers: Dict[str, List[Callable]] = {}
        self.logger = Logger()
        self.config = config
        self.notification_manager = NotificationManager(self.config) if config else None
    
    def subscribe(self, event_type: str, callback: Callable):
        """Подписывает функцию на определенное событие"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []
        self._subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Отписывает функцию от определенного события"""
        if event_type in self._subscribers:
            try:
                self._subscribers[event_type].remove(callback)
            except ValueError:
                pass  # Функция не была подписана
    
    def emit(self, event_type: str, data: Any = None):
        """Вызывает все функции, подписанные на событие"""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    self.logger.error(f"Ошибка при обработке события {event_type}: {e}")
    
    def add_notification_handler(self):
        """Добавляет обработчик уведомлений на основе конфигурации"""
        def notification_handler(data: Any):
            if self.notification_manager:
                # Проверяем, является ли data словарем с сообщением и уровнем
                if isinstance(data, dict) and 'message' in data and 'level' in data:
                    self.notification_manager.send_notification(data['message'], data['level'])
                elif isinstance(data, str):
                    self.notification_manager.send_notification(data, "INFO")
                else:
                    self.notification_manager.send_notification(str(data), "INFO")
            else:
                # Если notification_manager не определен, выводим в лог
                print(f"Уведомление: {data}")
        
        self.subscribe("notification", notification_handler)
    
    def emit_notification(self, message: str, level: str = "INFO"):
        """Отправляет уведомление через систему событий"""
        self.emit("notification", {"message": message, "level": level})