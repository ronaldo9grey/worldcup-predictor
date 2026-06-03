"""世界杯历史数据提供者"""
from typing import Dict, Any, Optional
from .base import DataProvider


class WCHistoryProvider(DataProvider):
    """
    世界杯历史表现数据提供者
    
    用于评估球队的"大赛经验"和"世界杯底蕴"
    """
    
    # 世界杯历史数据
    WC_HISTORY = {
        # 传统强队
        "BRA": {"appearances": 22, "best_result": "Champion", "titles": 5, "finals": 7, "semifinals": 11},
        "GER": {"appearances": 20, "best_result": "Champion", "titles": 4, "finals": 8, "semifinals": 13},
        "ITA": {"appearances": 18, "best_result": "Champion", "titles": 4, "finals": 6, "semifinals": 8},
        "ARG": {"appearances": 18, "best_result": "Champion", "titles": 3, "finals": 6, "semifinals": 6},
        "FRA": {"appearances": 16, "best_result": "Champion", "titles": 2, "finals": 4, "semifinals": 7},
        "URU": {"appearances": 14, "best_result": "Champion", "titles": 2, "finals": 2, "semifinals": 5},
        "ENG": {"appearances": 16, "best_result": "Champion", "titles": 1, "finals": 2, "semifinals": 4},
        "ESP": {"appearances": 16, "best_result": "Champion", "titles": 1, "finals": 2, "semifinals": 4},
        "NED": {"appearances": 11, "best_result": "Final", "titles": 0, "finals": 3, "semifinals": 5},
        
        # 新兴强队
        "POR": {"appearances": 8, "best_result": "Semi-final", "titles": 0, "finals": 0, "semifinals": 2},
        "CRO": {"appearances": 6, "best_result": "Final", "titles": 0, "finals": 2, "semifinals": 2},
        "BEL": {"appearances": 14, "best_result": "Semi-final", "titles": 0, "finals": 0, "semifinals": 2},
        "COL": {"appearances": 6, "best_result": "Quarter-final", "titles": 0, "finals": 0, "semifinals": 0},
        
        # 其他球队
        "MEX": {"appearances": 17, "best_result": "Quarter-final", "titles": 0, "finals": 0, "semifinals": 2},
        "USA": {"appearances": 11, "best_result": "Semi-final", "titles": 0, "finals": 0, "semifinals": 1},
        "JPN": {"appearances": 7, "best_result": "Round of 16", "titles": 0, "finals": 0, "semifinals": 0},
        "KOR": {"appearances": 11, "best_result": "Semi-final", "titles": 0, "finals": 0, "semifinals": 1},
        "SEN": {"appearances": 3, "best_result": "Quarter-final", "titles": 0, "finals": 0, "semifinals": 0},
        "MAR": {"appearances": 6, "best_result": "Semi-final", "titles": 0, "finals": 0, "semifinals": 1},
        
        # 默认
        "_default": {"appearances": 1, "best_result": "Group Stage", "titles": 0, "finals": 0, "semifinals": 0}
    }
    
    def __init__(self, database=None):
        self.db = database
    
    @property
    def name(self) -> str:
        return "world_cup_history"
    
    def get_team_data(self, team_code: str) -> Optional[Dict[str, Any]]:
        """获取球队世界杯历史数据"""
        history = self.WC_HISTORY.get(team_code, self.WC_HISTORY["_default"])
        
        return {
            "team_code": team_code,
            "appearances": history["appearances"],
            "best_result": history["best_result"],
            "titles": history["titles"],
            "finals": history["finals"],
            "semifinals": history["semifinals"],
            "experience_score": self._calculate_experience_score(history),
            "pedigree_level": self._get_pedigree_level(history)
        }
    
    def get_match_data(self, home_code: str, away_code: str) -> Optional[Dict[str, Any]]:
        """获取两队世界杯经验对比"""
        home_data = self.get_team_data(home_code)
        away_data = self.get_team_data(away_code)
        
        if not home_data or not away_data:
            return None
        
        # 计算经验差距因子
        home_exp = home_data["experience_score"]
        away_exp = away_data["experience_score"]
        
        if home_exp + away_exp > 0:
            exp_factor = (home_exp - away_exp) / (home_exp + away_exp)
        else:
            exp_factor = 0
        
        return {
            "home_experience_score": home_exp,
            "away_experience_score": away_exp,
            "experience_factor": exp_factor,  # 正值主队经验更丰富
            "home_pedigree": home_data["pedigree_level"],
            "away_pedigree": away_data["pedigree_level"]
        }
    
    def _calculate_experience_score(self, history: Dict) -> float:
        """
        计算经验分数（0-100）
        考虑：参赛次数、冠军、决赛、半决赛
        """
        score = 0
        
        # 参赛次数（最多20分）
        score += min(history["appearances"] * 1.0, 20)
        
        # 冠军（每个20分）
        score += history["titles"] * 20
        
        # 决赛（不含冠军，每个8分）
        score += max(0, history["finals"] - history["titles"]) * 8
        
        # 半决赛（不含决赛，每个4分）
        score += max(0, history["semifinals"] - history["finals"]) * 4
        
        return min(score, 100)
    
    def _get_pedigree_level(self, history: Dict) -> str:
        """获取底蕴等级"""
        titles = history["titles"]
        appearances = history["appearances"]
        
        if titles >= 3:
            return "legendary"  # 传奇（巴西、德国、意大利、阿根廷）
        elif titles >= 1:
            return "champion"   # 冠军底蕴
        elif history["finals"] >= 1:
            return "finalist"   # 决赛经验
        elif appearances >= 10:
            return "regular"    # 常客
        elif appearances >= 5:
            return "occasional" # 偶尔参赛
        else:
            return "newcomer"   # 新军
