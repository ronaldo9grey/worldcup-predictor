"""
统一数据服务
提供统一的数据访问接口，隐藏底层数据源实现细节
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import os
import asyncio
import logging

from data.sources import (
    BaseDataSource, TeamData, MatchData,
    create_data_source, DataSourceError, RateLimitError
)

logger = logging.getLogger(__name__)


class DataService:
    """统一数据服务"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # 从环境变量读取数据源类型
        source_type = os.getenv("DATA_SOURCE", "mock")
        
        # 构建配置
        config = {
            "api_key": os.getenv("BALLDONTLIE_API_KEY"),
        }
        
        # 创建数据源
        self._source = create_data_source(source_type, config)
        self._source_type = source_type
        self._last_refresh: Optional[datetime] = None
        self._refresh_interval = int(os.getenv("DATA_REFRESH_INTERVAL", "300"))  # 5分钟
        self._refresh_task = None
        
        self._initialized = True
        
        logger.info(f"DataService initialized with source: {source_type}")
    
    @property
    def source_name(self) -> str:
        """当前数据源名称"""
        return self._source.name
    
    @property
    def is_realtime(self) -> bool:
        """是否支持实时数据"""
        return self._source.is_realtime
    
    # ========== 球队相关 ==========
    
    async def get_all_teams(self) -> List[Dict]:
        """获取所有球队（返回字典格式，兼容现有API）"""
        teams = await self._source.get_teams()
        return [self._team_to_dict(t) for t in teams]
    
    async def get_team(self, code: str) -> Optional[Dict]:
        """获取单个球队"""
        team = await self._source.get_team(code)
        return self._team_to_dict(team) if team else None
    
    async def get_team_lookup(self) -> Dict[str, Dict]:
        """获取球队查询字典"""
        teams = await self._source.get_teams()
        return {t.code: self._team_to_dict(t) for t in teams}
    
    # ========== 分组相关 ==========
    
    async def get_groups(self) -> Dict[str, List[str]]:
        """获取分组信息"""
        return await self._source.get_groups()
    
    async def get_group_teams(self, group: str) -> List[Dict]:
        """获取小组球队列表"""
        groups = await self._source.get_groups()
        codes = groups.get(group.upper(), [])
        
        teams = []
        for code in codes:
            team = await self.get_team(code)
            if team:
                teams.append(team)
        
        return teams
    
    async def get_all_groups(self) -> Dict[str, List[Dict]]:
        """获取所有小组球队"""
        groups = await self._source.get_groups()
        result = {}
        
        for group, codes in groups.items():
            result[group] = []
            for code in codes:
                team = await self.get_team(code)
                if team:
                    result[group].append(team)
        
        return result
    
    # ========== 比赛相关 ==========
    
    async def get_matches(
        self,
        group: Optional[str] = None,
        stage: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """获取比赛列表"""
        matches = await self._source.get_matches(group, stage, status)
        return [self._match_to_dict(m) for m in matches]
    
    async def get_match(self, match_id: str) -> Optional[Dict]:
        """获取单场比赛"""
        match = await self._source.get_match(match_id)
        return self._match_to_dict(match) if match else None
    
    async def get_group_matches(self, group: str) -> List[Dict]:
        """获取小组比赛"""
        return await self.get_matches(group=group)
    
    async def get_live_matches(self) -> List[Dict]:
        """获取正在进行的比赛"""
        return await self.get_matches(status="live")
    
    async def get_finished_matches(self) -> List[Dict]:
        """获取已结束的比赛"""
        return await self.get_matches(status="finished")
    
    # ========== 积分榜相关 ==========
    
    async def get_standings(self, group: str) -> List[Dict]:
        """获取小组积分榜"""
        return await self._source.get_standings(group)
    
    async def get_all_standings(self) -> Dict[str, List[Dict]]:
        """获取所有小组积分榜"""
        groups = await self._source.get_groups()
        result = {}
        
        for group in groups:
            result[group] = await self.get_standings(group)
        
        return result
    
    # ========== FIFA 排名 ==========
    
    async def get_fifa_rankings(self) -> Dict[str, int]:
        """获取FIFA排名"""
        return await self._source.get_fifa_rankings()
    
    # ========== 数据刷新 ==========
    
    async def refresh(self) -> bool:
        """手动刷新数据"""
        try:
            success = await self._source.refresh()
            if success:
                self._last_refresh = datetime.now()
                logger.info("Data refreshed successfully")
            return success
        except DataSourceError as e:
            logger.error(f"Data refresh failed: {e}")
            return False
    
    async def start_auto_refresh(self):
        """启动自动刷新（世界杯期间使用）"""
        if self._refresh_task is not None:
            logger.warning("Auto refresh already running")
            return
        
        async def refresh_loop():
            while True:
                try:
                    await self.refresh()
                except Exception as e:
                    logger.error(f"Auto refresh error: {e}")
                
                await asyncio.sleep(self._refresh_interval)
        
        self._refresh_task = asyncio.create_task(refresh_loop())
        logger.info(f"Auto refresh started (interval: {self._refresh_interval}s)")
    
    def stop_auto_refresh(self):
        """停止自动刷新"""
        if self._refresh_task is not None:
            self._refresh_task.cancel()
            self._refresh_task = None
            logger.info("Auto refresh stopped")
    
    # ========== 数据源切换 ==========
    
    async def switch_source(self, source_type: str, **kwargs) -> bool:
        """
        切换数据源
        
        Args:
            source_type: 新的数据源类型
            **kwargs: 数据源配置参数
        
        Returns:
            是否切换成功
        """
        try:
            new_source = create_data_source(source_type, kwargs)
            
            # 健康检查
            if not await new_source.health_check():
                logger.error(f"New source {source_type} health check failed")
                return False
            
            # 切换成功
            old_type = self._source_type
            self._source = new_source
            self._source_type = source_type
            
            logger.info(f"Data source switched: {old_type} -> {source_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to switch source: {e}")
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        source_healthy = await self._source.health_check()
        
        return {
            "source": self._source_type,
            "source_healthy": source_healthy,
            "is_realtime": self.is_realtime,
            "last_refresh": self._last_refresh.isoformat() if self._last_refresh else None,
            "auto_refresh": self._refresh_task is not None
        }
    
    # ========== 工具方法 ==========
    
    def _team_to_dict(self, team: TeamData) -> Dict:
        """TeamData 转换为字典（兼容现有API）"""
        return {
            "code": team.code,
            "name": team.name,
            "name_cn": team.name_cn,
            "rank": team.rank,
            "elo": team.elo,
            "continent": team.continent,
            "form": team.form,
            "wc_titles": team.wc_titles,
            "group": team.group
        }
    
    def _match_to_dict(self, match: MatchData) -> Dict:
        """MatchData 转换为字典（兼容现有API）"""
        return {
            "match_id": match.match_id,
            "home": match.home_code,
            "home_name": match.home_name,
            "away": match.away_code,
            "away_name": match.away_name,
            "group": match.group,
            "stage": match.stage,
            "match_index": match.match_index,
            "round": match.round_num,
            "scheduled_time": match.scheduled_time,
            "home_score": match.home_score,
            "away_score": match.away_score,
            "status": match.status,
            "events": match.events
        }


# 全局实例
_data_service: Optional[DataService] = None


def get_data_service() -> DataService:
    """获取数据服务实例"""
    global _data_service
    if _data_service is None:
        _data_service = DataService()
    return _data_service
