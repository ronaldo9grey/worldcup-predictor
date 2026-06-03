"""缓存层 - 支持 Redis（生产）和内存缓存（开发）"""
import json
import time
from typing import Optional, Dict, Any, Callable
from functools import wraps


class Cache:
    """
    缓存抽象层，支持多种后端
    - 生产环境：Redis
    - 开发环境：内存缓存
    """
    
    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self._redis = None
        self._memory_cache: Dict[str, Dict[str, Any]] = {}
        
        if redis_url:
            try:
                import redis
                self._redis = redis.from_url(redis_url)
                self._redis.ping()
            except Exception:
                # Redis 不可用时降级到内存缓存
                self._redis = None
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """获取缓存值"""
        if self._redis:
            try:
                value = self._redis.get(key)
                return json.loads(value) if value else None
            except Exception:
                pass
        
        # 内存缓存
        entry = self._memory_cache.get(key)
        if entry and entry["expires_at"] > time.time():
            return entry["value"]
        elif entry:
            del self._memory_cache[key]
        return None
    
    def set(self, key: str, value: Dict[str, Any], ttl_seconds: int = 3600) -> None:
        """设置缓存值"""
        if self._redis:
            try:
                self._redis.setex(key, ttl_seconds, json.dumps(value))
                return
            except Exception:
                pass
        
        # 内存缓存
        self._memory_cache[key] = {
            "value": value,
            "expires_at": time.time() + ttl_seconds
        }
    
    def delete(self, key: str) -> None:
        """删除缓存"""
        if self._redis:
            try:
                self._redis.delete(key)
            except Exception:
                pass
        
        self._memory_cache.pop(key, None)
    
    def clear(self) -> None:
        """清空所有缓存"""
        if self._redis:
            try:
                self._redis.flushdb()
            except Exception:
                pass
        
        self._memory_cache.clear()


def cached(key_pattern: str, ttl_seconds: int = 3600):
    """
    方法级缓存装饰器
    
    用法：
        @cached("team:{code}", ttl_seconds=7200)
        def get_team_data(self, code: str):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 构建 key
            cache_key = key_pattern.format(*args, **kwargs)
            
            # 尝试从缓存获取
            cache = get_cache()
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # 执行方法
            result = func(self, *args, **kwargs)
            
            # 缓存结果
            if result is not None:
                cache.set(cache_key, result, ttl_seconds)
            
            return result
        return wrapper
    return decorator


# 单例模式
_cache_instance: Optional[Cache] = None


def get_cache(redis_url: Optional[str] = None) -> Cache:
    """获取缓存实例"""
    global _cache_instance
    if _cache_instance is None:
        _cache_instance = Cache(redis_url)
    return _cache_instance


def reset_cache(redis_url: Optional[str] = None) -> Cache:
    """重置缓存实例（用于测试）"""
    global _cache_instance
    _cache_instance = Cache(redis_url)
    return _cache_instance
