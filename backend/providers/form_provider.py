"""球队状态数据提供者"""
from typing import Dict, Any, Optional
from .base import DataProvider


class FormProvider(DataProvider):
    """
    球队近期状态数据提供者
    
    解析 form 字符串（如 "WWDWL"）并计算状态分数
    """
    
    # 各国联赛强度系数（用于调整状态权重）
    LEAGUE_STRENGTH = {
        "ENG": 1.0,   # 英超
        "ESP": 1.0,   # 西甲
        "ITA": 0.95,  # 意甲
        "GER": 0.95,  # 德甲
        "FRA": 0.9,   # 法甲
        "POR": 0.8,   # 葡超
        "NED": 0.75,  # 荷甲
        "BRA": 0.85,  # 巴甲
        "ARG": 0.8,   # 阿甲
        "_default": 0.6
    }
    
    def __init__(self, database=None):
        self.db = database
    
    @property
    def name(self) -> str:
        return "team_form"
    
    def get_team_data(self, team_code: str, form_str: str = None) -> Optional[Dict[str, Any]]:
        """解析球队状态"""
        if form_str is None:
            # 尝试从数据库获取
            if self.db:
                team = self.db.get_team(team_code)
                form_str = team.get("form", "WDWDW") if team else "WDWDW"
            else:
                form_str = "WDWDW"
        
        return {
            "team_code": team_code,
            "form_string": form_str,
            "form_score": self._calculate_form_score(form_str),
            "wins": form_str.count("W"),
            "draws": form_str.count("D"),
            "losses": form_str.count("L"),
            "goals_form": self._estimate_goals_form(form_str),
            "momentum": self._calculate_momentum(form_str)
        }
    
    def get_match_data(self, home_code: str, away_code: str, 
                       home_form: str = None, away_form: str = None) -> Optional[Dict[str, Any]]:
        """获取两队状态对比"""
        home_data = self.get_team_data(home_code, home_form)
        away_data = self.get_team_data(away_code, away_form)
        
        if not home_data or not away_data:
            return None
        
        # 状态差距因子 [-1, 1]
        home_score = home_data["form_score"]
        away_score = away_data["form_score"]
        
        if home_score + away_score > 0:
            form_factor = (home_score - away_score) / 100
        else:
            form_factor = 0
        
        return {
            "home_form_score": home_score,
            "away_form_score": away_score,
            "form_factor": form_factor,
            "home_momentum": home_data["momentum"],
            "away_momentum": away_data["momentum"],
            "momentum_diff": home_data["momentum"] - away_data["momentum"]
        }
    
    def _calculate_form_score(self, form: str) -> float:
        """
        计算状态分数（0-100）
        W=3分，D=1分，L=0分
        最近比赛权重更高
        """
        if not form:
            return 50
        
        score = 0
        weights = [3, 2.5, 2, 1.5, 1]  # 最近5场权重递减
        max_score = sum(w * 3 for w in weights)
        
        for i, result in enumerate(form[:5].upper()):
            if i >= len(weights):
                break
            if result == "W":
                score += weights[i] * 3
            elif result == "D":
                score += weights[i] * 1
        
        return round(score / max_score * 100, 1)
    
    def _calculate_momentum(self, form: str) -> float:
        """
        计算势头（-1到1）
        最近结果影响更大
        """
        if not form or len(form) < 3:
            return 0
        
        momentum = 0
        for i, result in enumerate(form[:5].upper()):
            weight = (5 - i) / 15  # 归一化权重
            if result == "W":
                momentum += weight
            elif result == "L":
                momentum -= weight
        
        return round(momentum, 2)
    
    def _estimate_goals_form(self, form: str) -> Dict[str, float]:
        """根据状态估算进球能力"""
        wins = form.count("W")
        draws = form.count("D")
        total = len(form) if form else 1
        
        # 粗略估算：胜场假设进2球，平局进1球
        goals_per_game = (wins * 2 + draws * 1) / total
        
        return {
            "estimated_goals_per_game": round(goals_per_game, 2),
            "attack_tier": "strong" if goals_per_game >= 1.5 else "moderate" if goals_per_game >= 1.0 else "weak"
        }
