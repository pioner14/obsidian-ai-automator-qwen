"""
Модуль для управления уведомлениями в Obsidian AI Automator
"""
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from obsidian_ai_automator.core.config import ConfigManager
from obsidian_ai_automator.core.logger import Logger


class BaseNotification:
    """Базовый класс для отправки уведомлений"""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = Logger()

    def send(self, message: str, level: str = "INFO") -> bool:
        """
        Отправляет уведомление
        :param message: Текст сообщения
        :param level: Уровень важности (INFO, ERROR и т.п.)
        :return: True, если уведомление отправлено успешно
        """
        raise NotImplementedError("Метод send должен быть реализован в подклассе")


class EmailNotification(BaseNotification):
    """Класс для отправки уведомлений по электронной почте"""

    def __init__(self, config: ConfigManager):
        super().__init__(config)
        self.smtp_server = self.config.get('Notifications', 'smtp_server', fallback='smtp.gmail.com')
        self.smtp_port = self.config.getint('Notifications', 'smtp_port', fallback=587)
        self.email_address = self.config.get('Notifications', 'email_address', fallback='')
        self.email_password = self.config.get('Notifications', 'email_password', fallback='')
        self.recipient_email = self.config.get('Notifications', 'recipient_email', fallback='')

    def send(self, message: str, level: str = "INFO") -> bool:
        """
        Отправляет уведомление по электронной почте
        :param message: Текст сообщения
        :param level: Уровень важности
        :return: True, если уведомление отправлено успешно
        """
        if not all([self.email_address, self.email_password, self.recipient_email]):
            self.logger.error("Недостаточно данных для отправки email уведомления")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = self.recipient_email
            msg['Subject'] = f"Obsidian AI Automator - Уведомление ({level})"

            body = f"Сообщение: {message}\nУровень: {level}\nВремя: {str(__import__('time').strftime('%Y-%m-%d %H:%M:%S'))}"
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_address, self.email_password)
            text = msg.as_string()
            server.sendmail(self.email_address, self.recipient_email, text)
            server.quit()

            self.logger.info("Уведомление отправлено по email")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при отправке email уведомления: {e}")
            return False


class TelegramNotification(BaseNotification):
    """Класс для отправки уведомлений через Telegram"""

    def __init__(self, config: ConfigManager):
        super().__init__(config)
        self.bot_token = self.config.get('Notifications', 'telegram_bot_token', fallback='')
        self.chat_id = self.config.get('Notifications', 'telegram_chat_id', fallback='')

    def send(self, message: str, level: str = "INFO") -> bool:
        """
        Отправляет уведомление через Telegram
        :param message: Текст сообщения
        :param level: Уровень важности
        :return: True, если уведомление отправлено успешно
        """
        if not all([self.bot_token, self.chat_id]):
            self.logger.error("Недостаточно данных для отправки Telegram уведомления")
            return False

        try:
            telegram_message = f"Obsidian AI Automator - Уведомление ({level})\n\n{message}"
            telegram_url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"

            payload = {
                'chat_id': self.chat_id,
                'text': telegram_message,
                'parse_mode': 'HTML'
            }

            response = requests.post(telegram_url, data=payload)
            response.raise_for_status()

            self.logger.info("Уведомление отправлено через Telegram")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при отправке Telegram уведомления: {e}")
            return False


class NotificationManager:
    """Класс для управления различными способами уведомлений"""

    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = Logger()
        self.notification_type = self.config.get('Notifications', 'type', fallback='none')

        # Инициализация способов уведомлений
        self.email_notifier = EmailNotification(self.config) if self.notification_type == 'email' else None
        self.telegram_notifier = TelegramNotification(self.config) if self.notification_type == 'telegram' else None

    def send_notification(self, message: str, level: str = "ERROR") -> bool:
        """
        Отправляет уведомление через настроенный канал
        :param message: Текст сообщения
        :param level: Уровень важности
        :return: True, если уведомление отправлено успешно
        """
        # Сначала логируем сообщение
        if level == "ERROR":
            self.logger.error(f"УВЕДОМЛЕНИЕ: {message}")
        else:
            self.logger.info(f"УВЕДОМЛЕНИЕ: {message}")

        success = True

        if self.notification_type == 'email' and self.email_notifier:
            success &= self.email_notifier.send(message, level)
        elif self.notification_type == 'telegram' and self.telegram_notifier:
            success &= self.telegram_notifier.send(message, level)
        elif self.notification_type != 'none':
            self.logger.warning(f"Неизвестный тип уведомлений: {self.notification_type}. Поддерживаемые типы: email, telegram, none")

        # Проверяем, нужно ли отправлять уведомления об успешных операциях
        if level == "INFO":
            try:
                notification_success_enabled = self.config.getboolean('Notifications', 'success_notifications', fallback=False)
                if not notification_success_enabled:
                    # Если уведомления об успехе отключены, не считаем это за ошибку
                    return True
            except Exception as e:
                self.logger.error(f"Ошибка при проверке настройки уведомлений об успехе: {e}")

        return success