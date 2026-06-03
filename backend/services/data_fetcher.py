"""数据获取服务"""
import httpx
import asyncio
from typing import Optional, List, Dict
from datetime import datetime
import json


class DataFetcher:
    """数据获取器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.headers = {"X-Auth-Token": api_key} if api_key else {}
        self.base_url = "https://api.football-data.org/v4"
    
    async def fetch_competition_matches(self, competition_code: str = "WC") -> List[dict]:
        """获取世界杯比赛数据"""
        # 2026世界杯的competition code可能是 WC 或其他
        url = f"{self.base_url}/competitions/{competition_code}/matches"
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, headers=self.headers, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("matches", [])
                else:
                    print(f"API Error: {resp.status_code} - {resp.text}")
                    return []
            except Exception as e:
                print(f"Fetch error: {e}")
                return []
    
    async def fetch_teams(self, competition_code: str = "WC") -> List[dict]:
        """获取参赛球队"""
        url = f"{self.base_url}/competitions/{competition_code}/teams"
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, headers=self.headers, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("teams", [])
                return []
            except Exception as e:
                print(f"Fetch teams error: {e}")
                return []
    
    async def fetch_standings(self, competition_code: str = "WC") -> List[dict]:
        """获取积分榜"""
        url = f"{self.base_url}/competitions/{competition_code}/standings"
        
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(url, headers=self.headers, timeout=30)
                if resp.status_code == 200:
                    data = resp.json()
                    return data.get("standings", [])
                return []
            except Exception as e:
                print(f"Fetch standings error: {e}")
                return []


class MockDataGenerator:
    """模拟数据生成器（开发测试用）"""
    
    # 2026世界杯32强预测（实际参赛队需要确认）
    TEAMS_2026 = {
        # 东道主
        "USA": {"name": "United States", "name_cn": "美国", "rank": 13, "elo": 1745, "continent": "NA"},
        "MEX": {"name": "Mexico", "name_cn": "墨西哥", "rank": 15, "elo": 1720, "continent": "NA"},
        "CAN": {"name": "Canada", "name_cn": "加拿大", "rank": 47, "elo": 1610, "continent": "NA"},
        
        # 南美
        "ARG": {"name": "Argentina", "name_cn": "阿根廷", "rank": 1, "elo": 1885, "continent": "SA"},
        "BRA": {"name": "Brazil", "name_cn": "巴西", "rank": 5, "elo": 1830, "continent": "SA"},
        "URU": {"name": "Uruguay", "name_cn": "乌拉圭", "rank": 11, "elo": 1765, "continent": "SA"},
        "COL": {"name": "Colombia", "name_cn": "哥伦比亚", "rank": 12, "elo": 1755, "continent": "SA"},
        
        # 欧洲
        "FRA": {"name": "France", "name_cn": "法国", "rank": 2, "elo": 1870, "continent": "EU"},
        "ENG": {"name": "England", "name_cn": "英格兰", "rank": 4, "elo": 1835, "continent": "EU"},
        "BEL": {"name": "Belgium", "name_cn": "比利时", "rank": 3, "elo": 1850, "continent": "EU"},
        "NED": {"name": "Netherlands", "name_cn": "荷兰", "rank": 7, "elo": 1800, "continent": "EU"},
        "POR": {"name": "Portugal", "name_cn": "葡萄牙", "rank": 6, "elo": 1815, "continent": "EU"},
        "GER": {"name": "Germany", "name_cn": "德国", "rank": 16, "elo": 1715, "continent": "EU"},
        "ESP": {"name": "Spain", "name_cn": "西班牙", "rank": 8, "elo": 1790, "continent": "EU"},
        "ITA": {"name": "Italy", "name_cn": "意大利", "rank": 9, "elo": 1780, "continent": "EU"},
        "CRO": {"name": "Croatia", "name_cn": "克罗地亚", "rank": 10, "elo": 1770, "continent": "EU"},
        "SUI": {"name": "Switzerland", "name_cn": "瑞士", "rank": 14, "elo": 1730, "continent": "EU"},
        "DEN": {"name": "Denmark", "name_cn": "丹麦", "rank": 21, "elo": 1680, "continent": "EU"},
        
        # 亚洲
        "JPN": {"name": "Japan", "name_cn": "日本", "rank": 18, "elo": 1695, "continent": "AS"},
        "KOR": {"name": "South Korea", "name_cn": "韩国", "rank": 23, "elo": 1660, "continent": "AS"},
        "AUS": {"name": "Australia", "name_cn": "澳大利亚", "rank": 25, "elo": 1650, "continent": "AS"},
        "IRN": {"name": "Iran", "name_cn": "伊朗", "rank": 20, "elo": 1690, "continent": "AS"},
        "SAU": {"name": "Saudi Arabia", "name_cn": "沙特", "rank": 53, "elo": 1580, "continent": "AS"},
        "QAT": {"name": "Qatar", "name_cn": "卡塔尔", "rank": 37, "elo": 1620, "continent": "AS"},
        
        # 非洲
        "SEN": {"name": "Senegal", "name_cn": "塞内加尔", "rank": 17, "elo": 1700, "continent": "AF"},
        "MAR": {"name": "Morocco", "name_cn": "摩洛哥", "rank": 13, "elo": 1745, "continent": "AF"},
        "NGA": {"name": "Nigeria", "name_cn": "尼日利亚", "rank": 36, "elo": 1625, "continent": "AF"},
        "GHA": {"name": "Ghana", "name_cn": "加纳", "rank": 61, "elo": 1550, "continent": "AF"},
        "CMR": {"name": "Cameroon", "name_cn": "喀麦隆", "rank": 46, "elo": 1615, "continent": "AF"},
        
        # 其他
        "ECU": {"name": "Ecuador", "name_cn": "厄瓜多尔", "rank": 32, "elo": 1640, "continent": "SA"},
        "PER": {"name": "Peru", "name_cn": "秘鲁", "rank": 35, "elo": 1630, "continent": "SA"},
    }
    
    # 模拟近期状态
    TEAM_FORMS = {
        "ARG": "WDWWL",
        "FRA": "WWWDW",
        "BRA": "WDWDL",
        "ENG": "WWWWD",
        "BEL": "WDWWL",
        "POR": "WWWDW",
        "NED": "DWWWD",
        "ESP": "WWDWD",
        "GER": "LDWWW",
        "ITA": "WDWDL",
        "CRO": "WWDWD",
        "URU": "WWWWL",
        "USA": "WDLWW",
        "MEX": "DWDWW",
        "JPN": "WWDWL",
        "KOR": "WWDLW",
        "MAR": "WDWWWW",
        "SEN": "WWWDW",
        "CAN": "DWLWD",
        # 默认其他为中等状态
    }
    
    @classmethod
    def generate_sample_matches(cls, num_matches: int = 16) -> List[dict]:
        """生成模拟比赛数据"""
        from datetime import timedelta
        import random
        
        teams = list(cls.TEAMS_2026.keys())
        matches = []
        base_time = datetime(2026, 6, 12, 18, 0)  # 2026世界杯预计时间
        
        stages = ["GROUP", "GROUP", "GROUP", "ROUND_OF_16"]
        
        for i in range(num_matches):
            home = random.choice(teams)
            away = random.choice([t for t in teams if t != home])
            home_data = cls.TEAMS_2026[home]
            away_data = cls.TEAMS_2026[away]
            
            match = {
                "match_id": f"WC2026_{i+1:03d}",
                "home_team": home,
                "home_team_name": home_data["name"],
                "home_team_name_cn": home_data["name_cn"],
                "home_team_rank": home_data["rank"],
                "home_elo": home_data["elo"],
                "home_recent_form": cls.TEAM_FORMS.get(home, "WDWDW"),
                "away_team": away,
                "away_team_name": away_data["name"],
                "away_team_name_cn": away_data["name_cn"],
                "away_team_rank": away_data["rank"],
                "away_elo": away_data["elo"],
                "away_recent_form": cls.TEAM_FORMS.get(away, "WDWDW"),
                "match_time": (base_time + timedelta(days=i//4, hours=i%4*3)).isoformat(),
                "venue": f"Stadium {i+1}",
                "stage": stages[min(i//4, 3)],
                "status": "SCHEDULED",
                "is_neutral": True,
                "host_country": "USA",
            }
            matches.append(match)
        
        return matches
    
    @classmethod
    def get_team_list(cls) -> List[dict]:
        """获取球队列表"""
        teams = []
        for code, data in cls.TEAMS_2026.items():
            teams.append({
                "fifa_code": code,
                "name": data["name"],
                "name_cn": data["name_cn"],
                "fifa_rank": data["rank"],
                "elo_rating": data["elo"],
                "continent": data["continent"],
                "recent_form": cls.TEAM_FORMS.get(code, "WDWDW"),
            })
        return sorted(teams, key=lambda x: x["fifa_rank"])


class OddsFetcher:
    """赔率数据获取器"""
    
    def __init__(self):
        # 可以接入赔率API
        pass
    
    async def fetch_match_odds(self, match_id: str) -> Optional[dict]:
        """获取比赛赔率"""
        # 模拟赔率数据
        # 实际应接入赔率API
        return {
            "home_odds": None,
            "draw_odds": None,
            "away_odds": None,
            "source": "mock",
            "updated_at": datetime.now().isoformat()
        }