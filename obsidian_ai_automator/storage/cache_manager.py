import os
import json
import hashlib
from typing import Any, Optional
from datetime import datetime, timedelta
from obsidian_ai_automator.core.logger import Logger


class CacheManager:
    """
    Система управления кэшем
    """
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        self.logger = Logger()
        os.makedirs(cache_dir, exist_ok=True)
    
    def _get_cache_key(self, key: str) -> str:
        """Генерирует имя файла кэша на основе ключа"""
        # Используем хэш для создания безопасного имени файла
        hashed_key = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hashed_key}.json")
    
    def get(self, key: str) -> Optional[Any]:
        """Получает значение из кэша по ключу"""
        cache_file = self._get_cache_key(key)
        
        if not os.path.exists(cache_file):
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Проверяем, не истек ли срок хранения
            ttl = cached_data.get('ttl', None)
            if ttl:
                cached_time = datetime.fromisoformat(cached_data['cached_at'])
                ttl_duration = timedelta(seconds=ttl)
                if datetime.now() - cached_time > ttl_duration:
                    # Удаляем истекший кэш
                    os.remove(cache_file)
                    self.logger.info(f"Удален устаревший кэш для ключа: {key}")
                    return None
            
            self.logger.info(f"Кэш найден для ключа: {key}")
            return cached_data['data']
        except Exception as e:
            self.logger.error(f"Ошибка при чтении кэша для ключа {key}: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Сохраняет значение в кэш с опциональным временем жизни (в секундах)"""
        cache_file = self._get_cache_key(key)
        
        try:
            cached_data = {
                'data': value,
                'cached_at': datetime.now().isoformat(),
                'ttl': ttl
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cached_data, f, ensure_ascii=False, indent=2)
            
            self.logger.info(f"Кэш сохранен для ключа: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при сохранении кэша для ключа {key}: {e}")
            return False
    
    def invalidate(self, key: str) -> bool:
        """Удаляет значение из кэша по ключу"""
        cache_file = self._get_cache_key(key)
        
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                self.logger.info(f"Кэш удален для ключа: {key}")
                return True
            except Exception as e:
                self.logger.error(f"Ошибка при удалении кэша для ключа {key}: {e}")
                return False
        
        return False
    
    def clear_expired(self) -> int:
        """Удаляет все просроченные кэши и возвращает количество удаленных записей"""
        if not os.path.exists(self.cache_dir):
            return 0
        
        deleted_count = 0
        for filename in os.listdir(self.cache_dir):
            if filename.endswith('.json'):
                cache_file = os.path.join(self.cache_dir, filename)
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    
                    ttl = cached_data.get('ttl', None)
                    if ttl:
                        cached_time = datetime.fromisoformat(cached_data['cached_at'])
                        ttl_duration = timedelta(seconds=ttl)
                        if datetime.now() - cached_time > ttl_duration:
                            os.remove(cache_file)
                            deleted_count += 1
                            self.logger.info(f"Удален устаревший кэш файл: {filename}")
                except Exception as e:
                    self.logger.error(f"Ошибка при проверке кэша {cache_file}: {e}")
        
        return deleted_count
    
    def clear_all(self) -> bool:
        """Очищает весь кэш"""
        if not os.path.exists(self.cache_dir):
            return True
        
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    cache_file = os.path.join(self.cache_dir, filename)
                    os.remove(cache_file)
            
            self.logger.info("Весь кэш очищен")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка при очистке кэша: {e}")
            return False