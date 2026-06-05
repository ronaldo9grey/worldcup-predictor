"""
模拟数据源 - 使用现有静态数据
用于开发和测试，世界杯开始前使用
"""
from typing import Dict, List, Optional
from .base import (
    BaseDataSource, TeamData, MatchData, StandingData,
    DataSourceError, DataNotFoundError
)
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from data.world_cup_2026 import ALL_TEAMS, GROUPS, MATCH_SCHEDULE


class MockDataSource(BaseDataSource):
    """模拟数据源（使用现有静态数据）"""
    
    def __init__(self):
        self._teams_cache: Dict[str, TeamData] = {}
        self._matches_cache: Dict[str, MatchData] = {}
        self._initialized = False
        self._init_data()
    
    @property
    def name(self) -> str:
        return "mock"
    
    @property
    def is_realtime(self) -> bool:
        return False
    
    def _init_data(self):
        """初始化数据缓存"""
        if self._initialized:
            return
        
        # 构建球队缓存
        team_lookup = {t["code"]: t for t in ALL_TEAMS}
        
        for team in ALL_TEAMS:
            team_data = TeamData(
                code=team["code"],
                name=team["name"],
                name_cn=team["name_cn"],
                rank=team["rank"],
                elo=team["elo"],
                continent=team["continent"],
                form=team.get("form", ""),
                wc_titles=team.get("wc_titles", 0)
            )
            self._teams_cache[team["code"]] = team_data
        
        # 为每个球队添加分组信息
        for group_name, codes in GROUPS.items():
            for code in codes:
                if code in self._teams_cache:
                    self._teams_cache[code].group = group_name
        
        # 构建比赛缓存
        match_id = 0
        for group_name, matches in MATCH_SCHEDULE.items():
            for match in matches:
                match_id += 1
                match_data = MatchData(
                    match_id=match["match_id"],
                    home_code=match["home"],
                    away_code=match["away"],
                    home_name=self._teams_cache.get(match["home"], TeamData(code=match["home"], name=match["home"], name_cn=match["home"], rank=99, elo=1400, continent="")).name_cn,
                    away_name=self._teams_cache.get(match["away"], TeamData(code=match["away"], name=match["away"], name_cn=match["away"], rank=99, elo=1400, continent="")).name_cn,
                    group=group_name,
                    stage="GROUP",
                    match_index=match["match_index"],
                    round_num=match["round"]
                )
                self._matches_cache[match["match_id"]] = match_data
        
        self._initialized = True
    
    async def get_teams(self) -> List[TeamData]:
        """获取所有球队"""
        return list(self._teams_cache.values())
    
    async def get_team(self, code: str) -> Optional[TeamData]:
        """获取单个球队"""
        return self._teams_cache.get(code.upper())
    
    async def get_groups(self) -> Dict[str, List[str]]:
        """获取分组信息"""
        return GROUPS.copy()
    
    async def get_matches(
        self, 
        group: Optional[str] = None,
        stage: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[MatchData]:
        """获取比赛列表"""
        matches = list(self._matches_cache.values())
        
        if group:
            matches = [m for m in matches if m.group == group.upper()]
        
        if stage:
            matches = [m for m in matches if m.stage == stage]
        
        if status:
            matches = [m for m in matches if m.status == status]
        
        return matches
    
    async def get_match(self, match_id: str) -> Optional[MatchData]:
        """获取单场比赛"""
        return self._matches_cache.get(match_id)
    
    async def get_standings(self, group: str) -> List[Dict]:
        """获取小组积分榜（模拟数据，尚未开始比赛）"""
        group = group.upper()
        codes = GROUPS.get(group, [])
        if not codes:
            raise DataNotFoundError(f"Group {group} not found")
        
        standings = []
        for i, code in enumerate(codes):
            team = self._teams_cache.get(code)
            standings.append({
                "position": i + 1,
                "code": code,
                "name": team.name if team else code,
                "name_cn": team.name_cn if team else code,
                "rank": team.rank if team else 99,
                "points": 0,
                "w": 0,
                "d": 0,
                "l": 0,
                "gf": 0,
                "ga": 0,
                "gd": 0
            })
        
        return standings
    
    async def get_fifa_rankings(self) -> Dict[str, int]:
        """获取FIFA排名"""
        return {code: team.rank for code, team in self._teams_cache.items()}
    
    async def refresh(self) -> bool:
        """刷新数据（模拟数据不需要刷新）"""
        return True
    
    async def health_check(self) -> bool:
        """健康检查"""
        return self._initialized
    
    def set_match_result(self, match_id: str, home_score: int, away_score: int):
        """设置比赛结果（用于测试）"""
        if match_id in self._matches_cache:
            match = self._matches_cache[match_id]
            match.home_score = home_score
            match.away_score = away_score
            match.status = "finished"
    
    def get_team_form_data(self, code: str) -> Dict:
        """获取球队状态数据"""
        team = self._teams_cache.get(code)
        if not team:
            return {}
        
        form = team.form
        form_data = {
            "W": form.count("W"),
            "D": form.count("D"),
            "L": form.count("L"),
            "form": form,
            "form_points": form.count("W") * 3 + form.count("D")
        }
        
        return form_data
