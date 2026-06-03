"""
2026世界杯赛前赔率数据
接入主流博彩公司赔率，用于预测模型校准
"""

from typing import Dict, List, Optional
from datetime import datetime

# 博彩公司数据源
BOOKMAKERS = {
    "bet365": {"name": "Bet365", "weight": 0.25, "margin": 0.05},
    "william_hill": {"name": "威廉希尔", "weight": 0.20, "margin": 0.055},
    "pinnacle": {"name": "Pinnacle", "weight": 0.25, "margin": 0.03},
    "draftkings": {"name": "DraftKings", "weight": 0.15, "margin": 0.05},
    "fan duel": {"name": "FanDuel", "weight": 0.15, "margin": 0.05},
}

# 小组赛赔率数据（模拟2026世界杯开盘赔率）
GROUP_ODDS = {
    "A": [
        {
            "match": "ARG vs URU",
            "home": "Argentina",
            "away": "Uruguay",
            "odds": {
                "bet365": {"home_win": 1.65, "draw": 3.80, "away_win": 5.50},
                "william_hill": {"home_win": 1.70, "draw": 3.75, "away_win": 5.25},
                "pinnacle": {"home_win": 1.68, "draw": 3.85, "away_win": 5.40},
            },
            "consensus": {"home_win": 0.588, "draw": 0.261, "away_win": 0.185},
            "favorite": "home",
            "margin": 0.034,
        },
        {
            "match": "ARG vs EGY",
            "home": "Argentina",
            "away": "Egypt",
            "odds": {
                "bet365": {"home_win": 1.35, "draw": 5.00, "away_win": 8.50},
                "william_hill": {"home_win": 1.40, "draw": 4.80, "away_win": 8.00},
                "pinnacle": {"home_win": 1.38, "draw": 5.10, "away_win": 8.25},
            },
            "consensus": {"home_win": 0.719, "draw": 0.197, "away_win": 0.118},
            "favorite": "home",
            "margin": 0.036,
        },
    ],
    
    "B": [
        {
            "match": "FRA vs NED",
            "home": "France",
            "away": "Netherlands",
            "odds": {
                "bet365": {"home_win": 1.85, "draw": 3.60, "away_win": 4.50},
                "william_hill": {"home_win": 1.90, "draw": 3.50, "away_win": 4.40},
                "pinnacle": {"home_win": 1.88, "draw": 3.65, "away_win": 4.45},
            },
            "consensus": {"home_win": 0.532, "draw": 0.274, "away_win": 0.224},
            "favorite": "home",
            "margin": 0.032,
        },
        {
            "match": "FRA vs SEN",
            "home": "France",
            "away": "Senegal",
            "odds": {
                "bet365": {"home_win": 1.45, "draw": 4.50, "away_win": 7.00},
                "william_hill": {"home_win": 1.50, "draw": 4.40, "away_win": 6.50},
                "pinnacle": {"home_win": 1.48, "draw": 4.55, "away_win": 6.75},
            },
            "consensus": {"home_win": 0.676, "draw": 0.220, "away_win": 0.149},
            "favorite": "home",
            "margin": 0.034,
        },
    ],
    
    "C": [
        {
            "match": "BRA vs POR",
            "home": "Brazil",
            "away": "Portugal",
            "odds": {
                "bet365": {"home_win": 2.10, "draw": 3.40, "away_win": 3.50},
                "william_hill": {"home_win": 2.15, "draw": 3.35, "away_win": 3.40},
                "pinnacle": {"home_win": 2.12, "draw": 3.45, "away_win": 3.45},
            },
            "consensus": {"home_win": 0.472, "draw": 0.290, "away_win": 0.290},
            "favorite": "home",
            "margin": 0.028,
        },
        {
            "match": "BRA vs JPN",
            "home": "Brazil",
            "away": "Japan",
            "odds": {
                "bet365": {"home_win": 1.25, "draw": 5.50, "away_win": 11.00},
                "william_hill": {"home_win": 1.30, "draw": 5.25, "away_win": 10.50},
                "pinnacle": {"home_win": 1.27, "draw": 5.60, "away_win": 10.75},
            },
            "consensus": {"home_win": 0.787, "draw": 0.179, "away_win": 0.093},
            "favorite": "home",
            "margin": 0.035,
        },
    ],
    
    "D": [
        {
            "match": "ENG vs GER",
            "home": "England",
            "away": "Germany",
            "odds": {
                "bet365": {"home_win": 2.60, "draw": 3.20, "away_win": 2.80},
                "william_hill": {"home_win": 2.65, "draw": 3.15, "away_win": 2.75},
                "pinnacle": {"home_win": 2.62, "draw": 3.25, "away_win": 2.78},
            },
            "consensus": {"home_win": 0.382, "draw": 0.308, "away_win": 0.360},
            "favorite": "home",
            "margin": 0.030,
        },
        {
            "match": "ENG vs MAR",
            "home": "England",
            "away": "Morocco",
            "odds": {
                "bet365": {"home_win": 1.55, "draw": 4.00, "away_win": 6.00},
                "william_hill": {"home_win": 1.60, "draw": 3.90, "away_win": 5.75},
                "pinnacle": {"home_win": 1.58, "draw": 4.05, "away_win": 5.85},
            },
            "consensus": {"home_win": 0.633, "draw": 0.247, "away_win": 0.171},
            "favorite": "home",
            "margin": 0.033,
        },
    ],
    
    "E": [
        {
            "match": "ESP vs BEL",
            "home": "Spain",
            "away": "Belgium",
            "odds": {
                "bet365": {"home_win": 2.30, "draw": 3.30, "away_win": 3.20},
                "william_hill": {"home_win": 2.35, "draw": 3.25, "away_win": 3.10},
                "pinnacle": {"home_win": 2.32, "draw": 3.35, "away_win": 3.15},
            },
            "consensus": {"home_win": 0.431, "draw": 0.299, "away_win": 0.317},
            "favorite": "home",
            "margin": 0.031,
        },
        {
            "match": "ESP vs CRO",
            "home": "Spain",
            "away": "Croatia",
            "odds": {
                "bet365": {"home_win": 1.70, "draw": 3.80, "away_win": 5.00},
                "william_hill": {"home_win": 1.75, "draw": 3.70, "away_win": 4.80},
                "pinnacle": {"home_win": 1.72, "draw": 3.85, "away_win": 4.90},
            },
            "consensus": {"home_win": 0.581, "draw": 0.260, "away_win": 0.205},
            "favorite": "home",
            "margin": 0.034,
        },
    ],
    
    "F": [
        {
            "match": "USA vs MEX",
            "home": "USA",
            "away": "Mexico",
            "odds": {
                "bet365": {"home_win": 2.40, "draw": 3.20, "away_win": 3.00},
                "william_hill": {"home_win": 2.45, "draw": 3.15, "away_win": 2.95},
                "pinnacle": {"home_win": 2.42, "draw": 3.25, "away_win": 2.98},
            },
            "consensus": {"home_win": 0.413, "draw": 0.308, "away_win": 0.336},
            "favorite": "home",
            "margin": 0.032,
        },
        {
            "match": "USA vs CAN",
            "home": "USA",
            "away": "Canada",
            "odds": {
                "bet365": {"home_win": 1.80, "draw": 3.60, "away_win": 4.50},
                "william_hill": {"home_win": 1.85, "draw": 3.50, "away_win": 4.40},
                "pinnacle": {"home_win": 1.82, "draw": 3.65, "away_win": 4.45},
            },
            "consensus": {"home_win": 0.549, "draw": 0.274, "away_win": 0.224},
            "favorite": "home",
            "margin": 0.033,
        },
    ],
}

# 冠军赔率（模拟开盘数据）
OUTRIGHT_ODDS = {
    "favorites": [
        {"team": "Argentina", "odds": 5.50, "probability": 0.182, "rank": 1},
        {"team": "France", "odds": 6.00, "probability": 0.167, "rank": 2},
        {"team": "Brazil", "odds": 6.50, "probability": 0.154, "rank": 3},
        {"team": "England", "odds": 8.00, "probability": 0.125, "rank": 4},
        {"team": "Germany", "odds": 9.00, "probability": 0.111, "rank": 5},
        {"team": "Spain", "odds": 10.00, "probability": 0.100, "rank": 6},
    ],
    "dark_horses": [
        {"team": "Portugal", "odds": 14.00, "probability": 0.071},
        {"team": "Netherlands", "odds": 16.00, "probability": 0.063},
        {"team": "Belgium", "odds": 20.00, "probability": 0.050},
        {"team": "Uruguay", "odds": 25.00, "probability": 0.040},
    ],
    "outsiders": [
        {"team": "USA", "odds": 50.00, "probability": 0.020},
        {"team": "Mexico", "odds": 60.00, "probability": 0.017},
        {"team": "Japan", "odds": 80.00, "probability": 0.012},
        {"team": "Senegal", "odds": 100.00, "probability": 0.010},
    ],
}


def odds_to_probability(home_odds: float, draw_odds: float, away_odds: float) -> Dict[str, float]:
    """将赔率转换为概率（考虑博彩公司margin）"""
    raw_probs = {
        "home_win": 1 / home_odds,
        "draw": 1 / draw_odds,
        "away_win": 1 / away_odds,
    }
    
    total = sum(raw_probs.values())
    margin = total - 1
    
    # 归一化
    normalized = {k: v / total for k, v in raw_probs.items()}
    
    return normalized


def get_match_odds(group: str, match_idx: int) -> Optional[Dict]:
    """获取特定比赛的赔率"""
    group_data = GROUP_ODDS.get(group.upper(), [])
    if match_idx < len(group_data):
        return group_data[match_idx]
    return None


def get_consensus_odds(group: str, match_idx: int) -> Optional[Dict]:
    """获取市场共识概率（多家博彩公司加权平均）"""
    match_data = get_match_odds(group, match_idx)
    if not match_data:
        return None
    
    # 已经计算好的共识概率
    return {
        "match": match_data["match"],
        "consensus": match_data["consensus"],
        "favorite": match_data["favorite"],
        "margin": match_data["margin"],
    }


def compare_model_vs_market(model_probs: Dict, market_probs: Dict) -> Dict:
    """比较模型预测与市场赔率的差异"""
    diff = {
        "home_win": model_probs.get("home_win", 0) - market_probs.get("home_win", 0),
        "draw": model_probs.get("draw", 0) - market_probs.get("draw", 0),
        "away_win": model_probs.get("away_win", 0) - market_probs.get("away_win", 0),
    }
    
    # 识别价值投注
    value_bets = []
    for outcome, delta in diff.items():
        if delta > 0.05:  # 模型概率高于市场5%
            value_bets.append({
                "outcome": outcome,
                "model_prob": model_probs.get(outcome, 0),
                "market_prob": market_probs.get(outcome, 0),
                "edge": delta,
                "recommendation": "value_bet",
            })
    
    return {
        "model": model_probs,
        "market": market_probs,
        "difference": diff,
        "value_bets": value_bets,
        "agreement": max(abs(diff["home_win"]), abs(diff["draw"]), abs(diff["away_win"])) < 0.1,
    }


def get_championship_odds() -> Dict:
    """获取冠军赔率数据"""
    return OUTRIGHT_ODDS


def calculate_implied_probability(odds: float) -> float:
    """计算隐含概率"""
    return 1 / odds if odds > 0 else 0


def get_value_rating(model_prob: float, market_odds: float) -> Dict:
    """评估投注价值"""
    market_prob = calculate_implied_probability(market_odds)
    edge = model_prob - market_prob
    
    if edge > 0.10:
        rating = "excellent"
        label = "极佳价值"
    elif edge > 0.05:
        rating = "good"
        label = "良好价值"
    elif edge > 0.02:
        rating = "fair"
        label = "尚可价值"
    else:
        rating = "poor"
        label = "无价值"
    
    return {
        "model_probability": round(model_prob, 3),
        "market_probability": round(market_prob, 3),
        "edge": round(edge, 3),
        "rating": rating,
        "label": label,
    }
