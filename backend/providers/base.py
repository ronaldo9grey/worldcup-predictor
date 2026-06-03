"""数据提供者抽象基类"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class DataProvider(ABC):
    """
    数据提供者抽象基类
    所有数据源都实现这个接口，便于扩展和测试
    """
    
    @abstractmethod
    def get_team_data(self, team_code: str) -> Optional[Dict[str, Any]]:
        """获取单支球队数据"""
        pass
    
    @abstractmethod
    def get_match_data(self, home_code: str, away_code: str) -> Optional[Dict[str, Any]]:
        """获取比赛相关数据（如历史交锋）"""
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """提供者名称"""
        pass
    
    def is_available(self) -> bool:
        """检查数据源是否可用"""
        return True
    
    def refresh(self) -> bool:
        """刷新数据（从外部源拉取）"""
        return True
