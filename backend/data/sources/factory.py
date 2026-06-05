"""
数据源工厂
根据配置创建对应的数据源实例
"""
from typing import Optional, Dict, Any
from .base import BaseDataSource, DataSourceError
from .mock_source import MockDataSource
from .balldontlie_source import BALLDONTLIEDataSource


def create_data_source(
    source_type: str = "mock",
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> BaseDataSource:
    """
    创建数据源实例
    
    Args:
        source_type: 数据源类型 (mock, balldontlie)
        config: 配置字典
        **kwargs: 额外参数
    
    Returns:
        BaseDataSource 实例
    
    Raises:
        ValueError: 未知的数据源类型
    """
    config = config or {}
    
    if source_type == "mock":
        return MockDataSource()
    
    elif source_type == "balldontlie":
        api_key = (
            kwargs.get("api_key") or 
            config.get("api_key") or
            config.get("BALLDONTLIE_API_KEY")
        )
        return BALLDONTLIEDataSource(api_key=api_key)
    
    else:
        raise ValueError(
            f"Unknown data source type: {source_type}. "
            f"Available: mock, balldontlie"
        )


def get_available_sources() -> Dict[str, str]:
    """获取可用的数据源列表"""
    return {
        "mock": "模拟数据源（用于开发和测试）",
        "balldontlie": "BALLDONTLIE API（免费，支持实时数据）"
    }
