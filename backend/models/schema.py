"""数据模型定义"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from enum import Enum


class MatchStatus(str, Enum):
    SCHEDULED = "SCHEDULED"
    LIVE = "LIVE"
    FINISHED = "FINISHED"
    POSTPONED = "POSTPONED"
    CUSTOM = "CUSTOM"  # 自定义预测


class PredictionType(str, Enum):
    HOME_WIN = "HOME_WIN"
    DRAW = "DRAW"
    AWAY_WIN = "AWAY_WIN"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


# ========== 数据库模型 ==========

class TeamBase(BaseModel):
    """球队基础信息"""
    fifa_code: str  # FIFA国家代码
    name: str
    name_cn: Optional[str] = None  # 中文名
    fifa_rank: int  # FIFA排名
    elo_rating: float  # Elo评分
    continent: str  # 所属洲
    group: Optional[str] = None  # 小组赛分组
    logo_url: Optional[str] = None


class TeamStats(TeamBase):
    """球队统计信息"""
    recent_form: str  # 近5场战绩，如 "WWDLW"
    goals_scored_last5: int
    goals_conceded_last5: int
    win_rate: float
    draw_rate: float
    loss_rate: float
    updated_at: datetime


class MatchBase(BaseModel):
    """比赛基础信息"""
    match_id: str
    home_team: str  # FIFA代码
    away_team: str
    match_time: datetime
    venue: Optional[str] = None
    stage: str  # 小组赛/16强/8强等
    status: MatchStatus = MatchStatus.SCHEDULED


class MatchWithPrediction(MatchBase):
    """比赛及预测"""
    home_team_name: str
    away_team_name: str
    home_team_rank: int
    away_team_rank: int
    
    # 预测结果
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    
    # 冷门分析
    upset_score: float  # 冷门指数 0-100
    upset_factors: List[str]  # 冷门因子
    is_potential_upset: bool  # 是否潜在冷门
    
    # 推荐方向
    prediction: PredictionType
    confidence: Confidence
    
    # 赔率信息
    home_odds: Optional[float] = None
    draw_odds: Optional[float] = None
    away_odds: Optional[float] = None
    
    # 实际结果（比赛结束后）
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    prediction_correct: Optional[bool] = None


# ========== API请求/响应模型 ==========

class MatchListResponse(BaseModel):
    """比赛列表响应"""
    matches: List[MatchWithPrediction]
    total: int
    upcoming_count: int
    upset_matches: int


class PredictionRequest(BaseModel):
    """预测请求"""
    home_team: str
    away_team: str
    include_odds: bool = False


class PredictionResponse(BaseModel):
    """预测响应"""
    home_team: TeamStats
    away_team: TeamStats
    prediction: MatchWithPrediction
    analysis: dict


class UpsetMatchList(BaseModel):
    """冷门比赛列表"""
    high_upset: List[MatchWithPrediction]  # 高冷门潜力
    medium_upset: List[MatchWithPrediction]  # 中等冷门潜力


class StatisticsResponse(BaseModel):
    """统计响应"""
    total_predictions: int
    correct_predictions: int
    accuracy_rate: float
    upset_predictions: int
    upset_correct: int
    upset_accuracy: float
    by_stage: dict


# ========== Elo评分系统 ==========

class EloRating:
    """Elo评分计算"""
    
    K = 32  # K因子
    
    @classmethod
    def expected_score(cls, rating_a: float, rating_b: float) -> float:
        """计算预期得分"""
        return 1 / (1 + 10 ** ((rating_b - rating_a) / 400))
    
    @classmethod
    def update_rating(cls, rating: float, expected: float, actual: float) -> float:
        """更新评分"""
        return rating + cls.K * (actual - expected)
    
    @classmethod
    def win_probability(cls, rating_home: float, rating_away: float, home_advantage: float = 100) -> dict:
        """计算胜率（含主场优势）"""
        effective_home = rating_home + home_advantage
        home_win = cls.expected_score(effective_home, rating_away)
        away_win = cls.expected_score(rating_away, effective_home)
        draw = 1 - home_win - away_win
        
        # 归一化
        total = home_win + draw + away_win
        return {
            "home_win": round(home_win / total, 3),
            "draw": round(max(0.1, draw / total), 3),  # 平局概率下限
            "away_win": round(away_win / total, 3)
        }