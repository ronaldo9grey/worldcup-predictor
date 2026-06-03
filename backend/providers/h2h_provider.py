"""历史交锋数据提供者"""
from typing import Dict, Any, Optional
from .base import DataProvider


class H2HProvider(DataProvider):
    """
    历史交锋数据提供者
    
    数据来源：
    1. 数据库缓存
    2. 未来可接入 football-data.org API
    """
    
    def __init__(self, database):
        self.db = database
    
    @property
    def name(self) -> str:
        return "head_to_head"
    
    def get_team_data(self, team_code: str) -> Optional[Dict[str, Any]]:
        """历史交锋数据以比赛为单位，不提供单队数据"""
        return None
    
    def get_match_data(self, home_code: str, away_code: str) -> Optional[Dict[str, Any]]:
        """获取两队历史交锋数据"""
        h2h_record = self.db.get_h2h_record(home_code, away_code)
        
        if h2h_record["total"] == 0:
            return None
        
        # 计算历史胜率因子
        total = h2h_record["total"]
        home_wins = h2h_record["team_a_wins"]
        away_wins = h2h_record["team_b_wins"]
        
        # 归一化到 [-1, 1]
        if total > 0:
            win_diff = (home_wins - away_wins) / total
        else:
            win_diff = 0
        
        return {
            "total_matches": total,
            "home_wins": home_wins,
            "away_wins": away_wins,
            "draws": h2h_record["draws"],
            "h2h_factor": win_diff,  # 正值偏向主队，负值偏向客队
            "recent_matches": h2h_record["matches"][:5]
        }
    
    def seed_historical_data(self):
        """
        种子历史交锋数据（关键比赛）
        可以从 CSV 导入或手动添加
        """
        historical_matches = [
            # 经典对决
            {"home_code": "ARG", "away_code": "BRA", "home_score": 1, "away_score": 0, 
             "match_date": "1990-06-24", "competition": "WC Round of 16"},
            {"home_code": "BRA", "away_code": "ARG", "home_score": 2, "away_score": 1, 
             "match_date": "2019-07-02", "competition": "Copa America Semi-final"},
            {"home_code": "ARG", "away_code": "FRA", "home_score": 0, "away_score": 4, 
             "match_date": "2018-06-30", "competition": "WC Round of 16"},
            {"home_code": "FRA", "away_code": "ARG", "home_score": 3, "away_score": 0, 
             "match_date": "2018-06-30", "competition": "WC Round of 16"},
            
            # 英德大战
            {"home_code": "ENG", "away_code": "GER", "home_score": 4, "away_score": 2, 
             "match_date": "2010-06-27", "competition": "WC Round of 16"},
            {"home_code": "GER", "away_code": "ENG", "home_score": 4, "away_score": 1, 
             "match_date": "2010-06-27", "competition": "WC Round of 16"},
            {"home_code": "GER", "away_code": "ENG", "home_score": 1, "away_score": 2, 
             "match_date": "2021-06-29", "competition": "Euro Round of 16"},
            
            # 经典比赛可继续添加...
        ]
        
        for match in historical_matches:
            self.db.add_h2h_match(match)
