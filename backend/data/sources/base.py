"""
数据源基类定义
所有数据源（模拟、FIFA、BALLDONTLIE等）都需实现此接口
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class TeamData(BaseModel):
    """球队数据模型"""
    code: str
    name: str
    name_cn: str
    rank: int
    elo: float
    continent: str
    form: str = ""
    wc_titles: int = 0
    group: Optional[str] = None


class MatchData(BaseModel):
    """比赛数据模型"""
    match_id: str
    home_code: str
    away_code: str
    home_name: str = ""
    away_name: str = ""
    group: Optional[str] = None
    stage: str = "GROUP"
    match_index: int = 0
    round_num: int = 1
    scheduled_time: Optional[str] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str = "scheduled"  # scheduled, live, finished
    events: List[Dict] = []


class StandingData(BaseModel):
    """积分榜数据模型"""
    group: str
    standings: List[Dict]


class BaseDataSource(ABC):
    """数据源基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """数据源名称"""
        pass
    
    @property
    @abstractmethod
    def is_realtime(self) -> bool:
        """是否支持实时数据"""
        pass
    
    @abstractmethod
    async def get_teams(self) -> List[TeamData]:
        """获取所有球队"""
        pass
    
    @abstractmethod
    async def get_team(self, code: str) -> Optional[TeamData]:
        """获取单个球队"""
        pass
    
    @abstractmethod
    async def get_groups(self) -> Dict[str, List[str]]:
        """获取分组信息 {group: [team_codes]}"""
        pass
    
    @abstractmethod
    async def get_matches(
        self, 
        group: Optional[str] = None,
        stage: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[MatchData]:
        """获取比赛列表"""
        pass
    
    @abstractmethod
    async def get_match(self, match_id: str) -> Optional[MatchData]:
        """获取单场比赛"""
        pass
    
    @abstractmethod
    async def get_standings(self, group: str) -> List[Dict]:
        """获取小组积分榜"""
        pass
    
    @abstractmethod
    async def get_fifa_rankings(self) -> Dict[str, int]:
        """获取FIFA排名 {team_code: rank}"""
        pass
    
    @abstractmethod
    async def refresh(self) -> bool:
        """刷新数据（从远程获取最新数据）"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """健康检查"""
        pass


class DataSourceError(Exception):
    """数据源错误"""
    pass


class RateLimitError(DataSourceError):
    """速率限制错误"""
    def __init__(self, retry_after: int = 60):
        self.retry_after = retry_after
        super().__init__(f"Rate limited, retry after {retry_after}s")


class DataNotFoundError(DataSourceError):
    """数据未找到错误"""
    pass
