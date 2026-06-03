"""球队身价数据提供者"""
from typing import Dict, Any, Optional
from .base import DataProvider


class TeamValueProvider(DataProvider):
    """
    球队身价数据提供者
    
    数据来源：
    1. Transfermarkt 网站爬取（需遵守robots.txt）
    2. 手动录入主要球队
    """
    
    # 2024年球队身价数据（百万欧元）
    TEAM_VALUES = {
        # 欧洲强队
        "ENG": 1520,  # 英格兰
        "FRA": 1290,  # 法国
        "POR": 1050,  # 葡萄牙
        "GER": 890,   # 德国
        "ESP": 980,   # 西班牙
        "NED": 850,   # 荷兰
        "ITA": 780,   # 意大利
        "BEL": 720,   # 比利时
        "CRO": 420,   # 克罗地亚
        
        # 南美强队
        "ARG": 820,   # 阿根廷
        "BRA": 1060,  # 巴西
        "URU": 450,   # 乌拉圭
        "COL": 280,   # 哥伦比亚
        
        # 其他
        "USA": 350,
        "MEX": 220,
        "JPN": 180,
        "KOR": 150,
        "SEN": 220,
        "MAR": 200,
        
        # 默认值（未收录球队）
        "_default": 100
    }
    
    def __init__(self, database=None):
        self.db = database
    
    @property
    def name(self) -> str:
        return "team_value"
    
    def get_team_data(self, team_code: str) -> Optional[Dict[str, Any]]:
        """获取球队身价数据"""
        value = self.TEAM_VALUES.get(team_code, self.TEAM_VALUES["_default"])
        
        return {
            "team_code": team_code,
            "team_value_millions": value,
            "team_value_rank": self._get_value_rank(value),
            "category": self._categorize_by_value(value)
        }
    
    def get_match_data(self, home_code: str, away_code: str) -> Optional[Dict[str, Any]]:
        """获取两队身价对比"""
        home_data = self.get_team_data(home_code)
        away_data = self.get_team_data(away_code)
        
        if not home_data or not away_data:
            return None
        
        home_value = home_data["team_value_millions"]
        away_value = away_data["team_value_millions"]
        
        # 计算身价差距因子 [-1, 1]
        # 使用对数缩放，避免差距过大
        import math
        if home_value + away_value > 0:
            value_ratio = (home_value - away_value) / (home_value + away_value)
        else:
            value_ratio = 0
        
        return {
            "home_value": home_value,
            "away_value": away_value,
            "value_diff": home_value - away_value,
            "value_factor": value_ratio,  # 正值主队身价更高
            "home_category": home_data["category"],
            "away_category": away_data["category"]
        }
    
    def _get_value_rank(self, value: int) -> int:
        """获取身价排名"""
        sorted_values = sorted(self.TEAM_VALUES.values(), reverse=True)
        try:
            return sorted_values.index(value) + 1
        except ValueError:
            return len(sorted_values)
    
    def _categorize_by_value(self, value: int) -> str:
        """按身价分类"""
        if value >= 800:
            return "tier1"  # 一流强队
        elif value >= 400:
            return "tier2"  # 二流强队
        elif value >= 200:
            return "tier3"  # 三流球队
        else:
            return "tier4"  # 弱旅


# 定价参考数据（可从数据库或API加载）
TEAM_VALUE_DATA = TeamValueProvider.TEAM_VALUES
