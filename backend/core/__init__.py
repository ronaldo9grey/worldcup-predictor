"""核心基础设施模块"""
from .database import Database, get_database
from .cache import Cache, get_cache

__all__ = ["Database", "get_database", "Cache", "get_cache"]
