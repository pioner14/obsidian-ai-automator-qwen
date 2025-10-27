import asyncio
import os
import sys
import time
from typing import Dict, Any, Optional, List
from obsidian_ai_automator.core.config import ConfigManager
from obsidian_ai_automator.core.logger import Logger
from obsidian_ai_automator.core.event_manager import EventManager
from obsidian_ai_automator.storage.cache_manager import CacheManager
from obsidian_ai_automator.core.error_handler import ErrorHandler, TranscriptionError, AnalysisError, OutputError
from obsidian_ai_automator.core.analytics import MetricsCollector
from obsidian_ai_automator.processing.transcription.deepgram_transcriber import DeepgramTranscriber
from obsidian_ai_automator.processing.analysis.nvidia_analyzer import NvidiaAnalyzer
from obsidian_ai_automator.processing.output.obsidian_formatter import ObsidianFormatter


class AsyncProcessingOrchestrator:
    """
    Асинхронная версия основного класса для параллельной обработки файлов
    """
    
    def __init__(self, config_file_path: str = "config.ini"):
        self.config = ConfigManager(config_file_path)
        self.logger = Logger()
        self.event_manager = EventManager(self.config)
        self.cache_manager = CacheManager()
        self.error_handler = ErrorHandler(self.config)
        self.metrics_collector = MetricsCollector(self.config)
        
        # Инициализируем логирование
        log_level = self.config.get('Logging', 'level', fallback='INFO')
        self.logger.setup_logger(level=log_level)
        
        # Подписываемся на события уведомлений
        self.event_manager.add_notification_handler()
        
        # Инициализируем компоненты в зависимости от конфигурации
        self._initialize_components()
        
        # Получаем максимальное количество параллельных процессов из конфигурации
        self.max_parallel_processes = self.config.getint('Processing', 'max_parallel_processes', fallback=2)
    
    def _initialize_components(self):
        """
        Инициализирует компоненты на основе конфигурации
        """
        processing_config = self.config.get_processing_config()
        
        # Инициализируем транскрибер
        transcription_provider = processing_config['transcription_provider']
        if transcription_provider == 'deepgram':
            self.transcriber = DeepgramTranscriber()
        elif transcription_provider == 'openai':
            from obsidian_ai_automator.processing.transcription.openai_transcriber import OpenAITranscriber
            self.transcriber = OpenAITranscriber()
        elif transcription_provider == 'whisper':
            from obsidian_ai_automator.processing.transcription.whisper_transcriber import WhisperTranscriber
            self.transcriber = WhisperTranscriber()
        else:
            raise ValueError(f"Неподдерживаемый провайдер транскрибации: {transcription_provider}")
        
        # Инициализируем анализатор
        analysis_provider = processing_config['analysis_provider']
        if analysis_provider == 'nvidia':
            self.analyzer = NvidiaAnalyzer()
        elif analysis_provider == 'openai':
            from obsidian_ai_automator.processing.analysis.openai_analyzer import OpenAIAnalyzer
            self.analyzer = OpenAIAnalyzer()
        else:
            raise ValueError(f"Неподдерживаемый провайдер анализа: {analysis_provider}")
        
        # Инициализируем форматтер
        output_format = processing_config['output_format']
        if output_format == 'obsidian':
            self.formatter = ObsidianFormatter()
        else:
            raise ValueError(f"Неподдерживаемый формат вывода: {output_format}")
    
    async def process_file_async(self, file_path: str) -> Optional[str]:
        """
        Асинхронно обрабатывает файл, выполняя транскрибацию, анализ и форматирование
        
        Args:
            file_path: Путь к файлу для обработки
            
        Returns:
            Путь к созданному файлу или None в случае ошибки
        """
        start_time = time.time()
        self.logger.info(f"Начало асинхронной обработки файла: {file_path}")
        
        # Проверяем, существует ли файл
        if not os.path.exists(file_path):
            self.logger.error(f"Файл не найден: {file_path}")
            self.metrics_collector.record_error("FileNotFound", f"Файл не найден: {file_path}")
            return None
        
        # Генерируем ключ для кэша на основе пути к файлу и его содержимого
        cache_key = f"transcript_{file_path}_{os.path.getmtime(file_path)}"
        
        # Проверяем, есть ли транскрипция в кэше
        cached_transcript = self.cache_manager.get(cache_key)
        if cached_transcript:
            self.logger.info(f"Используем кэшированную транскрипцию для файла: {file_path}")
            transcript = cached_transcript
        else:
            # Выполняем транскрибацию
            self.logger.info("Выполняем транскрибацию файла...")
            transcription_start = time.time()
            try:
                transcript = await self._transcribe_file_async(file_path)
                transcription_time = time.time() - transcription_start
                
                # Записываем метрики транскрибации
                self.metrics_collector.record_api_call("deepgram", duration=transcription_time,
                                                      additional_data={"duration": transcription_time})
                self.metrics_collector.metrics["total_transcription_time"] += transcription_time
            except TranscriptionError as e:
                self.error_handler.handle_transcription_error(e, file_path)
                self.event_manager.emit("processing_error", str(e))
                self.metrics_collector.record_error("TranscriptionError", str(e))
                return None
            except Exception as e:
                self.logger.error(f"Неожиданная ошибка при транскрибации: {e}")
                self.event_manager.emit("processing_error", str(e))
                self.metrics_collector.record_error("TranscriptionError", str(e))
                return None
            
            if not transcript:
                self.logger.error("Транскрипция не удалась или вернула пустой результат")
                self.metrics_collector.record_error("TranscriptionError", "Транскрипция не удалась или вернула пустой результат")
                return None
            
            # Сохраняем в кэш на 24 часа
            self.cache_manager.set(cache_key, transcript, ttl=86400)
        
        # Выполняем анализ
        self.logger.info("Выполняем анализ транскрипции...")
        analysis_start = time.time()
        try:
            analysis_result = await self._analyze_transcript_async(transcript)
            analysis_time = time.time() - analysis_start
            
            # Записываем метрики анализа
            self.metrics_collector.record_api_call("nvidia", duration=analysis_time,
                                                  additional_data={"tokens": len(transcript)})
            self.metrics_collector.metrics["total_analysis_time"] += analysis_time
        except AnalysisError as e:
            self.error_handler.handle_analysis_error(e, transcript)
            self.event_manager.emit("processing_error", str(e))
            self.metrics_collector.record_error("AnalysisError", str(e))
            return None
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при анализе: {e}")
            self.event_manager.emit("processing_error", str(e))
            self.metrics_collector.record_error("AnalysisError", str(e))
            return None
        
        # Подготавливаем контент для форматирования
        content = {
            'title': f"Анализ: {os.path.basename(file_path)}",
            'tags': analysis_result['tags'],
            'analysis': analysis_result['analysis'],
            'transcript': transcript
        }
        
        # Форматируем контент
        self.logger.info("Форматируем контент для Obsidian...")
        try:
            formatted_content = await self._format_content_async(content)
        except OutputError as e:
            self.error_handler.handle_output_error(e, str(content))
            self.event_manager.emit("processing_error", str(e))
            self.metrics_collector.record_error("OutputError", str(e))
            return None
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при форматировании: {e}")
            self.event_manager.emit("processing_error", str(e))
            self.metrics_collector.record_error("OutputError", str(e))
            return None
        
        # Определяем путь для сохранения
        paths_config = self.config.get_paths_config()
        obsidian_vault_path = os.path.expanduser(paths_config['obsidian_vault_path'])
        
        # Создаем безопасное имя файла
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        safe_filename = f"{base_name}.md"
        output_file_path = os.path.join(obsidian_vault_path, safe_filename)
        
        # Сохраняем файл
        self.logger.info(f"Сохраняем файл в: {output_file_path}")
        try:
            if await self._save_file_async(formatted_content, output_file_path):
                self.logger.info(f"Файл успешно создан: {output_file_path}")
                self.event_manager.emit("file_processed", output_file_path)
                
                # Фиксируем успешную обработку файла
                processing_time = time.time() - start_time
                self.metrics_collector.record_file_processed(file_path, processing_time)
                self.metrics_collector.save_metrics()
                
                return output_file_path
            else:
                self.logger.error(f"Ошибка при сохранении файла: {output_file_path}")
                self.metrics_collector.record_error("OutputError", f"Ошибка при сохранении файла: {output_file_path}")
                return None
        except OutputError as e:
            self.error_handler.handle_output_error(e, output_file_path)
            self.event_manager.emit("processing_error", str(e))
            self.metrics_collector.record_error("OutputError", str(e))
            return None
        except Exception as e:
            self.logger.error(f"Неожиданная ошибка при сохранении файла: {e}")
            self.event_manager.emit("processing_error", str(e))
            self.metrics_collector.record_error("OutputError", str(e))
            return None
    
    async def _transcribe_file_async(self, file_path: str) -> str:
        """
        Асинхронная транскрибация файла
        """
        # Используем asyncio.to_thread для выполнения синхронной операции в отдельном потоке
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.transcriber.get_transcription_with_timecodes, file_path)
    
    async def _analyze_transcript_async(self, transcript: str) -> Dict[str, Any]:
        """
        Асинхронный анализ транскрипции
        """
        # Используем asyncio.to_thread для выполнения синхронной операции в отдельном потоке
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.analyzer.get_analysis_with_tags, transcript)
    
    async def _format_content_async(self, content: Dict[str, Any]) -> str:
        """
        Асинхронное форматирование контента
        """
        # Используем asyncio.to_thread для выполнения синхронной операции в отдельном потоке
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.formatter.format, content)
    
    async def _save_file_async(self, content: str, file_path: str) -> bool:
        """
        Асинхронное сохранение файла
        """
        # Используем asyncio.to_thread для выполнения синхронной операции в отдельном потоке
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.formatter.save_to_file, content, file_path)
    
    async def process_multiple_files_async(self, file_paths: List[str]) -> List[str]:
        """
        Асинхронно обрабатывает несколько файлов параллельно
        
        Args:
            file_paths: Список путей к файлам для обработки
            
        Returns:
            Список путей к созданным файлам
        """
        semaphore = asyncio.Semaphore(self.max_parallel_processes)
        
        async def process_with_semaphore(file_path):
            async with semaphore:
                return await self.process_file_async(file_path)
        
        tasks = [process_with_semaphore(file_path) for file_path in file_paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Фильтруем результаты, исключая None и исключения
        processed_files = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"Ошибка при обработке файла {file_paths[i]}: {result}")
            elif result:
                processed_files.append(result)
        
        return processed_files