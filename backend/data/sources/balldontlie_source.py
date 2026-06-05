"""
BALLDONTLIE FIFA World Cup API 数据源
文档：https://fifa.balldontlie.io
"""
import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from .base import (
    BaseDataSource, TeamData, MatchData,
    DataSourceError, RateLimitError, DataNotFoundError
)
import os


class BALLDONTLIEDataSource(BaseDataSource):
    """BALLDONTLIE FIFA World Cup API 数据源"""
    
    BASE_URL = "https://api.balldontlie.io/fifa/worldcup/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("BALLDONTLIE_API_KEY")
        self._teams_cache: Dict[str, TeamData] = {}
        self._matches_cache: Dict[str, MatchData] = {}
        self._cache_time: Dict[str, datetime] = {}
        self._cache_ttl = timedelta(minutes=5)  # 5分钟缓存
        self._rate_limit_remaining = 100
        self._rate_limit_reset = None
    
    @property
    def name(self) -> str:
        return "balldontlie"
    
    @property
    def is_realtime(self) -> bool:
        return True
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = self.api_key
        return headers
    
    async def _request(self, endpoint: str, params: Dict = None) -> Dict:
        """发送请求"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url, 
                    headers=self._get_headers(),
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    # 检查速率限制
                    if response.status == 429:
                        retry_after = int(response.headers.get("Retry-After", 60))
                        raise RateLimitError(retry_after)
                    
                    # 更新速率限制信息
                    self._rate_limit_remaining = int(
                        response.headers.get("X-RateLimit-Remaining", 100)
                    )
                    
                    if response.status == 404:
                        raise DataNotFoundError(f"Endpoint {endpoint} not found")
                    
                    if response.status != 200:
                        raise DataSourceError(f"API error: {response.status}")
                    
                    return await response.json()
                    
            except aiohttp.ClientError as e:
                raise DataSourceError(f"Request failed: {e}")
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self._cache_time:
            return False
        return datetime.now() - self._cache_time[key] < self._cache_ttl
    
    async def get_teams(self) -> List[TeamData]:
        """获取所有球队"""
        cache_key = "all_teams"
        
        if self._is_cache_valid(cache_key):
            return list(self._teams_cache.values())
        
        try:
            data = await self._request("teams")
            
            for team_data in data.get("data", []):
                team = TeamData(
                    code=team_data.get("abbreviation", team_data.get("id", "")),
                    name=team_data.get("name", ""),
                    name_cn=team_data.get("name", ""),  # BALLDONTLIE 暂无中文名
                    rank=team_data.get("fifa_ranking", 99),
                    elo=1500,  # BALLDONTLIE 暂无 Elo 数据
                    continent=team_data.get("continent", ""),
                    group=team_data.get("group", "")
                )
                self._teams_cache[team.code] = team
            
            self._cache_time[cache_key] = datetime.now()
            return list(self._teams_cache.values())
            
        except DataSourceError:
            # API 失败时返回缓存数据
            if self._teams_cache:
                return list(self._teams_cache.values())
            raise
    
    async def get_team(self, code: str) -> Optional[TeamData]:
        """获取单个球队"""
        code = code.upper()
        
        if code in self._teams_cache and self._is_cache_valid(f"team_{code}"):
            return self._teams_cache[code]
        
        # 先确保加载了所有球队
        await self.get_teams()
        return self._teams_cache.get(code)
    
    async def get_groups(self) -> Dict[str, List[str]]:
        """获取分组信息"""
        teams = await self.get_teams()
        
        groups: Dict[str, List[str]] = {}
        for team in teams:
            if team.group:
                if team.group not in groups:
                    groups[team.group] = []
                groups[team.group].append(team.code)
        
        return groups
    
    async def get_matches(
        self, 
        group: Optional[str] = None,
        stage: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[MatchData]:
        """获取比赛列表"""
        cache_key = f"matches_{group}_{stage}_{status}"
        
        if self._is_cache_valid(cache_key):
            matches = list(self._matches_cache.values())
        else:
            params = {}
            if group:
                params["group"] = group
            if stage:
                params["stage"] = stage
            
            try:
                data = await self._request("matches", params)
                
                for match_data in data.get("data", []):
                    match = MatchData(
                        match_id=str(match_data.get("id", "")),
                        home_code=match_data.get("home_team", {}).get("abbreviation", ""),
                        away_code=match_data.get("away_team", {}).get("abbreviation", ""),
                        home_name=match_data.get("home_team", {}).get("name", ""),
                        away_name=match_data.get("away_team", {}).get("name", ""),
                        group=match_data.get("group"),
                        stage=match_data.get("stage", "GROUP"),
                        scheduled_time=match_data.get("date"),
                        home_score=match_data.get("home_score"),
                        away_score=match_data.get("away_score"),
                        status=match_data.get("status", "scheduled")
                    )
                    self._matches_cache[match.match_id] = match
                
                self._cache_time[cache_key] = datetime.now()
                matches = list(self._matches_cache.values())
                
            except DataSourceError:
                if self._matches_cache:
                    matches = list(self._matches_cache.values())
                else:
                    raise
        
        # 过滤
        if group:
            matches = [m for m in matches if m.group == group.upper()]
        if stage:
            matches = [m for m in matches if m.stage == stage]
        if status:
            matches = [m for m in matches if m.status == status]
        
        return matches
    
    async def get_match(self, match_id: str) -> Optional[MatchData]:
        """获取单场比赛"""
        cache_key = f"match_{match_id}"
        
        if match_id in self._matches_cache and self._is_cache_valid(cache_key):
            return self._matches_cache[match_id]
        
        try:
            data = await self._request(f"matches/{match_id}")
            
            match_data = data.get("data", data)
            match = MatchData(
                match_id=str(match_data.get("id", match_id)),
                home_code=match_data.get("home_team", {}).get("abbreviation", ""),
                away_code=match_data.get("away_team", {}).get("abbreviation", ""),
                home_name=match_data.get("home_team", {}).get("name", ""),
                away_name=match_data.get("away_team", {}).get("name", ""),
                group=match_data.get("group"),
                stage=match_data.get("stage", "GROUP"),
                scheduled_time=match_data.get("date"),
                home_score=match_data.get("home_score"),
                away_score=match_data.get("away_score"),
                status=match_data.get("status", "scheduled"),
                events=match_data.get("events", [])
            )
            
            self._matches_cache[match_id] = match
            self._cache_time[cache_key] = datetime.now()
            return match
            
        except DataNotFoundError:
            return None
    
    async def get_standings(self, group: str) -> List[Dict]:
        """获取小组积分榜"""
        cache_key = f"standings_{group}"
        
        if self._is_cache_valid(cache_key):
            # 从缓存获取
            pass
        
        try:
            data = await self._request("standings", {"group": group})
            
            standings = []
            for i, team_data in enumerate(data.get("data", [])):
                standings.append({
                    "position": i + 1,
                    "code": team_data.get("team", {}).get("abbreviation", ""),
                    "name": team_data.get("team", {}).get("name", ""),
                    "name_cn": team_data.get("team", {}).get("name", ""),
                    "points": team_data.get("points", 0),
                    "w": team_data.get("wins", 0),
                    "d": team_data.get("draws", 0),
                    "l": team_data.get("losses", 0),
                    "gf": team_data.get("goals_for", 0),
                    "ga": team_data.get("goals_against", 0),
                    "gd": team_data.get("goal_difference", 0)
                })
            
            self._cache_time[cache_key] = datetime.now()
            return standings
            
        except DataSourceError:
            raise
    
    async def get_fifa_rankings(self) -> Dict[str, int]:
        """获取FIFA排名"""
        teams = await self.get_teams()
        return {t.code: t.rank for t in teams}
    
    async def refresh(self) -> bool:
        """刷新数据"""
        try:
            self._cache_time.clear()
            await self.get_teams()
            await self.get_matches()
            return True
        except DataSourceError:
            return False
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            await self._request("teams", {"per_page": 1})
            return True
        except Exception:
            return False
    
    @property
    def rate_limit_remaining(self) -> int:
        """剩余请求次数"""
        return self._rate_limit_remaining
