"""
WorldCup26.ir 数据源
免费、无需 API Key、支持实时比分
API 地址: https://worldcup26.ir
"""
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime
from .base import (
    BaseDataSource, TeamData, MatchData,
    DataSourceError, RateLimitError, DataNotFoundError
)
import logging

logger = logging.getLogger(__name__)


class WorldCup26Source(BaseDataSource):
    """WorldCup26.ir 数据源"""
    
    BASE_URL = "https://worldcup26.ir/get"
    
    def __init__(self):
        self._teams_cache: Dict[str, TeamData] = {}
        self._matches_cache: Dict[str, MatchData] = {}
        self._groups_cache: Dict[str, List[str]] = {}
        self._standings_cache: Dict[str, List[Dict]] = {}
        self._cache_time: Dict[str, datetime] = {}
        self._cache_ttl = 60  # 1分钟缓存（实时数据需要频繁更新）
        
        # 本地补充数据（FIFA排名、Elo、中文名称）
        self._supplement_data = self._load_supplement_data()
    
    @property
    def name(self) -> str:
        return "worldcup26"
    
    @property
    def is_realtime(self) -> bool:
        return True
    
    def _load_supplement_data(self) -> Dict:
        """加载本地补充数据（FIFA排名、Elo、中文名称）"""
        try:
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            from data.world_cup_2026 import ALL_TEAMS
            
            supplement = {}
            for team in ALL_TEAMS:
                code = team["code"]
                supplement[code] = {
                    "rank": team.get("rank", 99),
                    "elo": team.get("elo", 1500),
                    "name_cn": team.get("name_cn", team["name"]),
                    "form": team.get("form", ""),
                    "wc_titles": team.get("wc_titles", 0),
                    "continent": team.get("continent", "")
                }
            
            # 添加代码映射（WorldCup26.ir 代码 → 本地代码）
            code_mappings = {
                "RSA": "ZAF",  # South Africa
                "KSA": "SAU",  # Saudi Arabia
            }
            
            for wc_code, local_code in code_mappings.items():
                if local_code in supplement:
                    supplement[wc_code] = supplement[local_code].copy()
            
            return supplement
        except Exception as e:
            logger.warning(f"加载补充数据失败: {e}")
            return {}
    
    async def _request(self, endpoint: str) -> Dict:
        """发送请求"""
        url = f"{self.BASE_URL}/{endpoint}"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    url,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 429:
                        raise RateLimitError(60)
                    
                    if response.status == 404:
                        raise DataNotFoundError(f"Endpoint {endpoint} not found")
                    
                    if response.status != 200:
                        raise DataSourceError(f"API error: {response.status}")
                    
                    return await response.json()
                    
            except aiohttp.ClientError as e:
                logger.error(f"Request failed: {e}")
                raise DataSourceError(f"Request failed: {e}")
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self._cache_time:
            return False
        elapsed = (datetime.now() - self._cache_time[key]).total_seconds()
        return elapsed < self._cache_ttl
    
    async def get_teams(self) -> List[TeamData]:
        """获取所有球队"""
        cache_key = "all_teams"
        
        if self._is_cache_valid(cache_key):
            return list(self._teams_cache.values())
        
        try:
            data = await self._request("teams")
            
            for team_data in data.get("teams", []):
                # 获取补充数据
                code = team_data.get("fifa_code", team_data.get("iso2", ""))
                supplement = self._supplement_data.get(code, {})
                
                team = TeamData(
                    code=code,
                    name=team_data.get("name_en", team_data.get("name", "")),
                    name_cn=supplement.get("name_cn", team_data.get("name_en", "")),
                    rank=supplement.get("rank", 99),
                    elo=supplement.get("elo", 1500),
                    continent=supplement.get("continent", team_data.get("groups", "")),
                    form=supplement.get("form", ""),
                    wc_titles=supplement.get("wc_titles", 0),
                    group=team_data.get("groups", "")
                )
                self._teams_cache[code] = team
            
            self._cache_time[cache_key] = datetime.now()
            return list(self._teams_cache.values())
            
        except DataSourceError:
            if self._teams_cache:
                return list(self._teams_cache.values())
            raise
    
    async def get_team(self, code: str) -> Optional[TeamData]:
        """获取单个球队"""
        code = code.upper()
        
        if code in self._teams_cache and self._is_cache_valid(f"team_{code}"):
            return self._teams_cache[code]
        
        # 先确保加载所有球队
        await self.get_teams()
        return self._teams_cache.get(code)
    
    async def get_groups(self) -> Dict[str, List[str]]:
        """获取分组信息"""
        cache_key = "groups"
        
        if self._is_cache_valid(cache_key):
            return self._groups_cache.copy()
        
        # 直接从 teams 缓存构建分组信息（更可靠）
        teams = await self.get_teams()
        groups: Dict[str, List[str]] = {}
        for team in teams:
            if team.group:
                if team.group not in groups:
                    groups[team.group] = []
                groups[team.group].append(team.code)
        
        self._groups_cache = groups
        self._cache_time[cache_key] = datetime.now()
        return self._groups_cache.copy()
    
    async def get_matches(
        self, 
        group: Optional[str] = None,
        stage: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[MatchData]:
        """获取比赛列表"""
        cache_key = f"matches_{group}_{stage}_{status}"
        
        if not self._is_cache_valid("all_matches"):
            try:
                data = await self._request("games")
                
                # 先获取球队列表，建立 name -> code 映射
                teams = await self.get_teams()
                name_to_code = {t.name: t.code for t in teams}
                
                for match_data in data.get("games", []):
                    match_id = match_data.get("id", "")
                    
                    # 解析比分状态
                    finished = match_data.get("finished", "FALSE") == "TRUE"
                    time_elapsed = match_data.get("time_elapsed", "notstarted")
                    
                    if finished:
                        match_status = "finished"
                    elif time_elapsed == "notstarted":
                        match_status = "scheduled"
                    else:
                        match_status = "live"
                    
                    # 将 team_id 转换为 code
                    home_name = match_data.get("home_team_name_en", "")
                    away_name = match_data.get("away_team_name_en", "")
                    home_code = name_to_code.get(home_name, match_data.get("home_team_id", ""))
                    away_code = name_to_code.get(away_name, match_data.get("away_team_id", ""))
                    
                    match = MatchData(
                        match_id=match_id,
                        home_code=home_code,
                        away_code=away_code,
                        home_name=match_data.get("home_team_name_en", ""),
                        away_name=match_data.get("away_team_name_en", ""),
                        group=match_data.get("group"),
                        stage="GROUP" if match_data.get("type") == "group" else "KNOCKOUT",
                        match_index=int(match_data.get("id", "0")),
                        round_num=int(match_data.get("matchday", "1")),
                        scheduled_time=match_data.get("local_date"),
                        home_score=int(match_data.get("home_score", 0)) if match_data.get("home_score") else None,
                        away_score=int(match_data.get("away_score", 0)) if match_data.get("away_score") else None,
                        status=match_status
                    )
                    self._matches_cache[match_id] = match
                
                self._cache_time["all_matches"] = datetime.now()
                
            except DataSourceError:
                if not self._matches_cache:
                    raise
        
        matches = list(self._matches_cache.values())
        
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
        # 确保缓存已加载
        if not self._matches_cache:
            await self.get_matches()
        
        return self._matches_cache.get(match_id)
    
    async def get_standings(self, group: str) -> List[Dict]:
        """获取小组积分榜 - 基于比赛结果本地计算（避免 /get/groups 端点的bug）"""
        cache_key = f"standings_{group}"
        
        if self._is_cache_valid(cache_key):
            return self._standings_cache.get(group, [])
        
        try:
            # 获取该小组的所有比赛（从 /get/games 获取，数据正确）
            matches = await self.get_matches(group=group)
            
            # 获取小组球队列表
            groups_data = await self.get_groups()
            group_teams = groups_data.get(group.upper(), [])
            
            # 初始化积分榜
            standings_dict = {}
            for team_code in group_teams:
                team_info = self._teams_cache.get(team_code)
                standings_dict[team_code] = {
                    "code": team_code,
                    "name": team_info.name if team_info else team_code,
                    "name_cn": team_info.name_cn if team_info else team_code,
                    "rank": team_info.rank if team_info else 99,
                    "points": 0,
                    "w": 0,
                    "d": 0,
                    "l": 0,
                    "gf": 0,
                    "ga": 0,
                    "gd": 0
                }
            
            # 基于比赛结果计算积分榜
            for match in matches:
                if match.status != "finished":
                    continue
                
                home_code = match.home_code
                away_code = match.away_code
                home_score = match.home_score or 0
                away_score = match.away_score or 0
                
                # 更新进球失球
                if home_code in standings_dict:
                    standings_dict[home_code]["gf"] += home_score
                    standings_dict[home_code]["ga"] += away_score
                
                if away_code in standings_dict:
                    standings_dict[away_code]["gf"] += away_score
                    standings_dict[away_code]["ga"] += home_score
                
                # 更新积分和胜负
                if home_score > away_score:
                    # 主胜
                    if home_code in standings_dict:
                        standings_dict[home_code]["points"] += 3
                        standings_dict[home_code]["w"] += 1
                    if away_code in standings_dict:
                        standings_dict[away_code]["l"] += 1
                elif home_score < away_score:
                    # 客胜
                    if away_code in standings_dict:
                        standings_dict[away_code]["points"] += 3
                        standings_dict[away_code]["w"] += 1
                    if home_code in standings_dict:
                        standings_dict[home_code]["l"] += 1
                else:
                    # 平局
                    if home_code in standings_dict:
                        standings_dict[home_code]["points"] += 1
                        standings_dict[home_code]["d"] += 1
                    if away_code in standings_dict:
                        standings_dict[away_code]["points"] += 1
                        standings_dict[away_code]["d"] += 1
            
            # 计算净胜球并排序
            for team_data in standings_dict.values():
                team_data["gd"] = team_data["gf"] - team_data["ga"]
            
            # 转为列表并排序（积分 > 净胜球 > 进球数）
            standings = list(standings_dict.values())
            standings.sort(key=lambda x: (-x["points"], -x["gd"], -x["gf"]))
            
            # 添加排名
            for i, team in enumerate(standings, 1):
                team["position"] = i
            
            self._standings_cache[group.upper()] = standings
            self._cache_time[cache_key] = datetime.now()
            
            return standings
            
        except DataSourceError:
            return self._standings_cache.get(group.upper(), [])
    
    async def get_fifa_rankings(self) -> Dict[str, int]:
        """获取FIFA排名（使用本地补充数据）"""
        teams = await self.get_teams()
        return {t.code: t.rank for t in teams}
    
    async def refresh(self) -> bool:
        """刷新数据"""
        try:
            self._cache_time.clear()
            await self.get_teams()
            await self.get_matches()
            return True
        except DataSourceError as e:
            logger.error(f"Refresh failed: {e}")
            return False
    
    async def health_check(self) -> bool:
        """健康检查"""
        try:
            data = await self._request("teams")
            return "teams" in data
        except Exception:
            return False
    
    async def get_live_matches(self) -> List[MatchData]:
        """获取正在进行的比赛"""
        return await self.get_matches(status="live")
    
    async def get_finished_matches(self) -> List[MatchData]:
        """获取已结束的比赛"""
        return await self.get_matches(status="finished")
    
    async def get_upcoming_matches(self, limit: int = 10) -> List[MatchData]:
        """获取即将开始的比赛"""
        matches = await self.get_matches(status="scheduled")
        return matches[:limit]
