"""
Модуль для сбора и хранения аналитических метрик
"""
import json
import os
import time
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from obsidian_ai_automator.core.config import ConfigManager
from obsidian_ai_automator.core.logger import Logger


class MetricsCollector:
    """
    Класс для сбора и хранения аналитических метрик
    """
    
    def __init__(self, config: ConfigManager = None):
        self.config = config
        self.logger = Logger()
        self.metrics_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "metrics.json")
        self.metrics = self._load_metrics()
        
        # Инициализируем основные метрики
        self._init_default_metrics()
    
    def _init_default_metrics(self):
        """Инициализирует значения по умолчанию для метрик"""
        default_metrics = {
            "total_processed_files": 0,
            "total_processing_errors": 0,
            "total_api_calls": 0,
            "total_transcription_time": 0,
            "total_analysis_time": 0,
            "files": [],
            "api_usage": {
                "deepgram": {
                    "total_calls": 0,
                    "total_duration": 0,
                    "total_cost": 0
                },
                "nvidia": {
                    "total_calls": 0,
                    "total_tokens": 0,
                    "total_cost": 0
                }
            },
            "processing_stats": {
                "average_processing_time": 0,
                "longest_processing_time": 0,
                "shortest_processing_time": float('inf')
            }
        }
        
        for key, value in default_metrics.items():
            if key not in self.metrics:
                self.metrics[key] = value
    
    def _load_metrics(self) -> Dict[str, Any]:
        """Загружает метрики из файла"""
        try:
            if os.path.exists(self.metrics_file):
                with open(self.metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Ошибка при загрузке метрик: {e}")
        
        return {}
    
    def save_metrics(self):
        """Сохраняет метрики в файл"""
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.metrics, f, ensure_ascii=False, indent=2, default=str)
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении метрик: {e}")
    
    def record_file_processed(self, file_path: str, processing_time: float):
        """Фиксирует информацию о обработанном файле"""
        self.metrics["total_processed_files"] += 1
        
        # Обновляем статистику обработки
        if processing_time > self.metrics["processing_stats"]["longest_processing_time"]:
            self.metrics["processing_stats"]["longest_processing_time"] = processing_time
        
        if processing_time < self.metrics["processing_stats"]["shortest_processing_time"]:
            self.metrics["processing_stats"]["shortest_processing_time"] = processing_time
        
        # Обновляем среднее время обработки (с использованием скользящего среднего)
        total_files = self.metrics["total_processed_files"]
        current_avg = self.metrics["processing_stats"]["average_processing_time"]
        new_avg = ((current_avg * (total_files - 1)) + processing_time) / total_files
        self.metrics["processing_stats"]["average_processing_time"] = new_avg
        
        # Добавляем информацию о файле
        file_record = {
            "file_path": file_path,
            "processing_time": processing_time,
            "processed_at": datetime.now().isoformat()
        }
        self.metrics["files"].append(file_record)
        
        # Ограничиваем размер истории файлов
        max_history = 1000  # Максимальное количество записей в истории
        if len(self.metrics["files"]) > max_history:
            self.metrics["files"] = self.metrics["files"][-max_history:]
    
    def record_error(self, error_type: str, error_message: str):
        """Фиксирует информацию об ошибке"""
        self.metrics["total_processing_errors"] += 1
        
        error_record = {
            "error_type": error_type,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        if "errors" not in self.metrics:
            self.metrics["errors"] = []
        
        self.metrics["errors"].append(error_record)
        
        # Ограничиваем размер истории ошибок
        max_history = 1000
        if len(self.metrics["errors"]) > max_history:
            self.metrics["errors"] = self.metrics["errors"][-max_history:]
    
    def record_api_call(self, provider: str, duration: float = 0, additional_data: Dict[str, Any] = None):
        """Фиксирует информацию о вызове API"""
        self.metrics["total_api_calls"] += 1
        
        if provider in self.metrics["api_usage"]:
            self.metrics["api_usage"][provider]["total_calls"] += 1
            
            if duration > 0:
                self.metrics["api_usage"][provider]["total_duration"] += duration
                
            if additional_data:
                # Обновляем дополнительные метрики в зависимости от провайдера
                if provider == "deepgram" and "duration" in additional_data:
                    self.metrics["api_usage"][provider]["total_duration"] += additional_data["duration"]
                elif provider == "nvidia" and "tokens" in additional_data:
                    self.metrics["api_usage"][provider]["total_tokens"] += additional_data["tokens"]
    
    def get_summary(self) -> Dict[str, Any]:
        """Возвращает сводку по метрикам"""
        return {
            "total_processed_files": self.metrics.get("total_processed_files", 0),
            "total_processing_errors": self.metrics.get("total_processing_errors", 0),
            "total_api_calls": self.metrics.get("total_api_calls", 0),
            "processing_stats": self.metrics.get("processing_stats", {}),
            "api_usage": self.metrics.get("api_usage", {})
        }
    
    def get_detailed_report(self) -> str:
        """Генерирует детальный отчет по метрикам"""
        summary = self.get_summary()
        
        report = f"""
=== Отчет по аналитике Obsidian AI Automator ===
Дата отчета: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Общая статистика:
- Всего обработано файлов: {summary['total_processed_files']}
- Всего ошибок обработки: {summary['total_processing_errors']}
- Всего вызовов API: {summary['total_api_calls']}

Статистика обработки:
- Среднее время обработки: {summary['processing_stats'].get('average_processing_time', 0):.2f} сек
- Самое долгое время обработки: {summary['processing_stats'].get('longest_processing_time', 0):.2f} сек
- Самое короткое время обработки: {summary['processing_stats'].get('shortest_processing_time', 0):.2f} сек

Использование API:
- Deepgram:
  - Всего вызовов: {summary['api_usage']['deepgram']['total_calls']}
  - Общая длительность: {summary['api_usage']['deepgram']['total_duration']:.2f} сек
- NVIDIA:
  - Всего вызовов: {summary['api_usage']['nvidia']['total_calls']}
  - Всего токенов: {summary['api_usage']['nvidia']['total_tokens']}
"""
        return report