from typing import Callable, Dict, List, Any
from obsidian_ai_automator.core.logger import Logger


class EventManager:
    """
    Система управления событиями и уведомлениями
    """
    
    def __init__(self):
        self._subscribers: Dict[str, List[Callable]] = {}
        self.logger = Logger()
    
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
    
    def add_notification_handler(self, notification_type: str = "telegram"):
        """Добавляет обработчик уведомлений"""
        def notification_handler(data: Any):
            # В реальной реализации здесь будет код для отправки уведомлений
            # в зависимости от типа уведомления (email, telegram, и т.д.)
            print(f"Уведомление ({notification_type}): {data}")
        
        self.subscribe("notification", notification_handler)