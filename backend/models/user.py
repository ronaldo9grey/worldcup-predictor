"""
用户模块 - 数据模型

功能：
1. 用户注册/登录（简单模式）
2. 预测记录保存
3. 赛后验证与积分
"""
from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime


@dataclass
class User:
    """用户"""
    user_id: str
    nickname: str
    created_at: str
    last_login: str = ""
    total_points: int = 0
    correct_predictions: int = 0
    total_predictions: int = 0


@dataclass 
class UserPrediction:
    """用户预测记录"""
    id: str  # {user_id}_{match_id}
    user_id: str
    match_id: str
    group_name: str
    match_idx: int
    home_code: str
    away_code: str
    
    # 预测内容
    prediction: str  # HOME_WIN / DRAW / AWAY_WIN
    confidence: str  # HIGH / MEDIUM / LOW
    predicted_at: str
    
    # 验证结果
    actual_result: Optional[str] = None  # 赛后填写
    is_correct: Optional[bool] = None
    points_earned: int = 0
    verified_at: Optional[str] = None


@dataclass
class LeaderboardEntry:
    """排行榜条目"""
    rank: int
    user_id: str
    nickname: str
    total_points: int
    accuracy: float
    correct_predictions: int
    total_predictions: int
