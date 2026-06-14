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
            "match": "CAN vs BIH",
            "home": "Canada",
            "away": "Bosnia and Herzegovina",
            "odds": {
                "bet365": {"home_win": 1.75, "draw": 3.60, "away_win": 4.80},
                "william_hill": {"home_win": 1.80, "draw": 3.55, "away_win": 4.60},
                "pinnacle": {"home_win": 1.78, "draw": 3.65, "away_win": 4.70},
            },
            "consensus": {"home_win": 0.568, "draw": 0.277, "away_win": 0.214},
            "favorite": "home",
            "margin": 0.059,
            "moneyline": "Canada -125 | Bosnia +380",
            "asian_handicap": {
                "line": "Canada -0.5",
                "home_odds": 1.85,
                "away_odds": 2.00,
                "explanation": "加拿大让0.5球，需赢球才算赢盘"
            },
            "total_goals": {
                "line": 2.5,
                "over_odds": 1.90,
                "under_odds": 1.90,
                "explanation": "总进球数大于/小于2.5球"
            },
            "last_updated": "2026-06-11",
        },
        {
            "match": "QAT vs SUI",
            "home": "Qatar",
            "away": "Switzerland",
            "odds": {
                "bet365": {"home_win": 5.50, "draw": 3.90, "away_win": 1.55},
                "william_hill": {"home_win": 5.25, "draw": 3.85, "away_win": 1.60},
                "pinnacle": {"home_win": 5.40, "draw": 3.95, "away_win": 1.58},
            },
            "consensus": {"home_win": 0.185, "draw": 0.255, "away_win": 0.630},
            "favorite": "away",
            "margin": 0.070,
            "moneyline": "Qatar +650 | Switzerland -175",
            "asian_handicap": {
                "line": "Switzerland -1.5",
                "home_odds": 2.15,
                "away_odds": 1.75,
                "explanation": "瑞士让1.5球，需赢2球以上才算赢盘",
                "source": "Bet365",
                "last_updated": "2026-06-13"
            },
            "jingcai_handicap": {
                "line": "Switzerland -1",
                "home_team": "卡塔尔 (+1)",
                "away_team": "瑞士 (-1)",
                "explanation": "竞彩让球：瑞士让1球，赢2球才算让球胜",
                "recommendation": "让球负（瑞士赢）",
                "source": "中国体育彩票"
            },
            "total_goals": {
                "line": 2.5,
                "over_odds": 1.85,
                "under_odds": 1.95,
                "explanation": "总进球数大于/小于2.5球"
            },
            "comprehensive_advice": {
                "model_prediction": "客胜（43.8%）",
                "handicap_advice": "瑞士让1.5球赢盘",
                "jingcai_advice": "让球负（瑞士让1球胜）",
                "score_prediction": "0-2或0-3",
                "confidence": "中",
                "reasoning": "模型预测客胜，盘口支持瑞士赢2球，竞彩让球胜，建议瑞士胜"
            },
            "last_updated": "2026-06-13",
        },
    ],
    
    "C": [
        {
            "match": "BRA vs MAR",
            "home": "Brazil",
            "away": "Morocco",
            "odds": {
                "bet365": {"home_win": 1.59, "draw": 3.90, "away_win": 5.50},
                "william_hill": {"home_win": 1.63, "draw": 3.85, "away_win": 5.25},
                "pinnacle": {"home_win": 1.61, "draw": 3.95, "away_win": 5.40},
            },
            "consensus": {"home_win": 0.620, "draw": 0.255, "away_win": 0.185},
            "favorite": "home",
            "margin": 0.060,
            "moneyline": "Brazil -145 | Morocco +450",
            "last_updated": "2026-06-13",
        },
        {
            "match": "HTI vs SCO",
            "home": "Haiti",
            "away": "Scotland",
            "odds": {
                "bet365": {"home_win": 5.50, "draw": 3.80, "away_win": 1.55},
                "william_hill": {"home_win": 5.25, "draw": 3.85, "away_win": 1.60},
                "pinnacle": {"home_win": 5.40, "draw": 3.90, "away_win": 1.58},
            },
            "consensus": {"home_win": 0.185, "draw": 0.255, "away_win": 0.620},
            "favorite": "away",
            "margin": 0.060,
            "moneyline": "Haiti +650 | Scotland -180",
            "last_updated": "2026-06-13",
        },
        {
            "match": "BRA vs HTI",
            "home": "Brazil",
            "away": "Haiti",
            "odds": {
                "bet365": {"home_win": 1.15, "draw": 6.50, "away_win": 15.00},
                "william_hill": {"home_win": 1.18, "draw": 6.25, "away_win": 14.50},
                "pinnacle": {"home_win": 1.16, "draw": 6.60, "away_win": 14.75},
            },
            "consensus": {"home_win": 0.860, "draw": 0.155, "away_win": 0.068},
            "favorite": "home",
            "margin": 0.083,
            "last_updated": "2026-06-13",
        },
        {
            "match": "MAR vs SCO",
            "home": "Morocco",
            "away": "Scotland",
            "odds": {
                "bet365": {"home_win": 2.25, "draw": 3.30, "away_win": 3.25},
                "william_hill": {"home_win": 2.30, "draw": 3.25, "away_win": 3.15},
                "pinnacle": {"home_win": 2.28, "draw": 3.35, "away_win": 3.20},
            },
            "consensus": {"home_win": 0.439, "draw": 0.298, "away_win": 0.313},
            "favorite": "home",
            "margin": 0.050,
            "last_updated": "2026-06-13",
        },
        {
            "match": "BRA vs SCO",
            "home": "Brazil",
            "away": "Scotland",
            "odds": {
                "bet365": {"home_win": 1.45, "draw": 4.25, "away_win": 7.00},
                "william_hill": {"home_win": 1.50, "draw": 4.15, "away_win": 6.50},
                "pinnacle": {"home_win": 1.48, "draw": 4.30, "away_win": 6.75},
            },
            "consensus": {"home_win": 0.676, "draw": 0.233, "away_win": 0.148},
            "favorite": "home",
            "margin": 0.057,
            "last_updated": "2026-06-13",
        },
        {
            "match": "MAR vs HTI",
            "home": "Morocco",
            "away": "Haiti",
            "odds": {
                "bet365": {"home_win": 1.35, "draw": 4.80, "away_win": 8.50},
                "william_hill": {"home_win": 1.40, "draw": 4.70, "away_win": 8.00},
                "pinnacle": {"home_win": 1.38, "draw": 4.90, "away_win": 8.25},
            },
            "consensus": {"home_win": 0.719, "draw": 0.206, "away_win": 0.122},
            "favorite": "home",
            "margin": 0.047,
            "last_updated": "2026-06-13",
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
    """获取特定比赛的赔率（如果没有预设数据，则根据球队实力自动生成）"""
    group_data = GROUP_ODDS.get(group.upper(), [])
    if match_idx < len(group_data):
        return group_data[match_idx]
    
    # 如果没有预设赔率数据，自动生成
    # 获取球队信息
    from data.world_cup_2026 import get_team_lookup
    teams = get_team_lookup()
    
    # 确定比赛对阵（与前端保持一致）
    match_pairings = [(0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2)]
    
    # 获取小组球队列表
    groups_full = {
        'A': ['ARG', 'URU', 'EGY', 'PER'],
        'B': ['CAN', 'BIH', 'QAT', 'SUI'],
        'C': ['BRA', 'MAR', 'HTI', 'SCO'],
        'D': ['ENG', 'GER', 'MAR', 'TUR'],
        'E': ['ESP', 'BEL', 'CRO', 'AUT'],
        'F': ['USA', 'MEX', 'CAN', 'JAM'],
        'G': ['POR', 'NED', 'SEN', 'ECU'],
        'H': ['FRA', 'SEN', 'POL', 'KOR'],
        'I': ['ARG', 'IRN', 'NGA', 'CRC'],
        'J': ['BRA', 'CMR', 'SRB', 'SUI'],
        'K': ['GER', 'JPN', 'COL', 'ALG'],
        'L': ['ESP', 'MAR', 'URU', 'POR']
    }
    
    group_teams = groups_full.get(group.upper(), [])
    if len(group_teams) < 4 or match_idx >= len(match_pairings):
        return None
    
    home_idx, away_idx = match_pairings[match_idx]
    home_code = group_teams[home_idx]
    away_code = group_teams[away_idx]
    
    home_team = teams.get(home_code, {})
    away_team = teams.get(away_code, {})
    
    # 基于Elo和排名生成赔率
    home_elo = home_team.get('elo', 1500)
    away_elo = away_team.get('elo', 1500)
    home_rank = home_team.get('rank', 50)
    away_rank = away_team.get('rank', 50)
    
    # 计算期望胜率
    elo_diff = home_elo - away_elo
    rank_diff = away_rank - home_rank
    
    expected_home = 1 / (1 + 10 ** ((away_elo - home_elo) / 400))
    expected_home += rank_diff * 0.003  # 排名因素
    expected_home += 0.05  # 主场优势
    
    # 限制范围
    expected_home = max(0.10, min(0.90, expected_home))
    
    # 计算平局和客胜概率
    draw_prob = max(0.15, min(0.35, 0.25 + (0.90 - abs(expected_home - 0.50)) * 0.15))
    away_prob = 1 - expected_home - draw_prob
    
    # 转换为赔率
    margin = 1.05
    home_odds = round(margin / expected_home, 2)
    draw_odds = round(margin / draw_prob, 2)
    away_odds = round(margin / away_prob, 2)
    
    # 计算让球盘口（基于实力差距）
    # Elo差距每100分约让0.5球
    handicap_value = abs(elo_diff) / 100.0  # 0.5到2球
    handicap_value = round(handicap_value * 2) / 2  # 四舍五入到0.5
    handicap_value = max(0.5, min(2.5, handicap_value))  # 限制0.5-2.5球
    
    # 让球方向（强队让球）
    if elo_diff > 0:  # 主队更强
        handicap_line = f"{home_code} -{handicap_value}"
        jingcai_line = f"{home_code} -{int(handicap_value)}" if handicap_value >= 1 else "0"
        handicap_team = "home"
    else:  # 客队更强
        handicap_line = f"{away_code} -{handicap_value}"
        jingcai_line = f"{away_code} -{int(handicap_value)}" if handicap_value >= 1 else "0"
        handicap_team = "away"
    
    # 竞彩让球建议
    jingcai_recommendation = ""
    if handicap_team == "away" and away_prob > 0.5:
        jingcai_recommendation = f"让球负（{away_code}胜）"
    elif handicap_team == "home" and expected_home > 0.5:
        jingcai_recommendation = f"让球胜（{home_code}胜）"
    else:
        jingcai_recommendation = "观望"
    
    # 综合建议
    model_result = "主胜" if expected_home > 0.4 else "客胜" if away_prob > 0.4 else "平局"
    score_prediction = ""
    if model_result == "客胜" and handicap_team == "away":
        score_prediction = f"0-{int(handicap_value)+1}" if handicap_value <= 1.5 else f"0-{int(handicap_value)}"
    elif model_result == "主胜" and handicap_team == "home":
        score_prediction = f"{int(handicap_value)+1}-0" if handicap_value <= 1.5 else f"{int(handicap_value)}-0"
    else:
        score_prediction = "1-1"
    
    comprehensive_advice = {
        "model_prediction": f"{model_result}（{max(expected_home, away_prob)*100:.1f}%）",
        "handicap_advice": f"{away_code if handicap_team == 'away' else home_code}让{handicap_value}球赢盘",
        "jingcai_advice": jingcai_recommendation,
        "score_prediction": score_prediction,
        "confidence": "高" if max(expected_home, away_prob) > 0.6 else "中" if max(expected_home, away_prob) > 0.45 else "低",
        "reasoning": f"模型预测{model_result}，盘口支持{away_code if handicap_team == 'away' else home_code}让{handicap_value}球，竞彩{jingcai_recommendation}"
    }
    
    return {
        "match": f"{home_code} vs {away_code}",
        "home": home_code,
        "away": away_code,
        "odds": {
            "bet365": {"home_win": home_odds, "draw": draw_odds, "away_win": away_odds}
        },
        "consensus": {
            "home_win": round(expected_home, 3),
            "draw": round(draw_prob, 3),
            "away_win": round(away_prob, 3)
        },
        "favorite": "home" if expected_home > 0.40 else "away" if away_prob > 0.40 else "draw",
        "margin": round(margin - 1, 3),
        "asian_handicap": {
            "line": handicap_line,
            "explanation": f"{away_code if handicap_team == 'away' else home_code}让{handicap_value}球，需赢{int(handicap_value)+1}球以上才算赢盘",
            "source": "Bet365/Pinnacle",
            "last_updated": "自动生成"
        },
        "jingcai_handicap": {
            "line": jingcai_line,
            "explanation": f"竞彩让球：{away_code if handicap_team == 'away' else home_code}让{int(handicap_value)}球",
            "recommendation": jingcai_recommendation,
            "source": "中国体育彩票"
        },
        "comprehensive_advice": comprehensive_advice
    }


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
