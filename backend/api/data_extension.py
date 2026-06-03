"""
数据扩展API - 第八轮迭代
提供伤病、赔率、情感数据接口
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional

# 导入数据模块
import sys
sys.path.append('/var/www/worldcup-predictor/backend')
from data.injuries import (
    get_team_injuries, get_injury_report, compare_injuries, get_injury_impact
)
from data.odds import (
    get_match_odds, get_consensus_odds, compare_model_vs_market,
    get_championship_odds, get_value_rating, calculate_implied_probability
)
from data.social_sentiment import (
    get_team_sentiment, compare_sentiments, get_buzz_trending_teams,
    get_pressure_analysis, get_sentiment_impact
)

router = APIRouter(prefix="/api/data-extension", tags=["数据扩展"])


# ==================== 伤病数据API ====================

@router.get("/injuries/{team_code}")
async def api_get_team_injuries(team_code: str) -> Dict:
    """获取球队伤病名单"""
    return get_injury_report(team_code.upper())


@router.get("/injuries/compare/{home_code}/{away_code}")
async def api_compare_injuries(home_code: str, away_code: str) -> Dict:
    """比较两队伤病情况"""
    return compare_injuries(home_code.upper(), away_code.upper())


@router.get("/injuries/impact/{team_code}")
async def api_get_injury_impact(team_code: str) -> Dict:
    """获取球队伤病影响系数"""
    impact = get_injury_impact(team_code.upper())
    report = get_injury_report(team_code.upper())
    
    return {
        "team_code": team_code.upper(),
        "impact_coefficient": impact,
        "injury_count": report["injury_count"],
        "risk_level": report["risk_level"],
        "risk_label": report["risk_label"],
    }


# ==================== 赔率数据API ====================

@router.get("/odds/group/{group}/match/{match_idx}")
async def api_get_match_odds(group: str, match_idx: int) -> Dict:
    """获取特定比赛的赔率"""
    odds_data = get_match_odds(group.upper(), match_idx)
    
    if not odds_data:
        raise HTTPException(status_code=404, detail="未找到该比赛的赔率数据")
    
    return {
        "match": odds_data["match"],
        "bookmaker_odds": odds_data["odds"],
        "consensus_probability": odds_data["consensus"],
        "favorite": odds_data["favorite"],
        "market_margin": odds_data["margin"],
    }


@router.get("/odds/consensus/{group}/{match_idx}")
async def api_get_consensus(group: str, match_idx: int) -> Dict:
    """获取市场共识概率"""
    consensus = get_consensus_odds(group, match_idx)
    
    if not consensus:
        raise HTTPException(status_code=404, detail="未找到共识概率数据")
    
    return consensus


@router.post("/odds/compare-model")
async def api_compare_model_market(
    model_home: float,
    model_draw: float,
    model_away: float,
    group: str,
    match_idx: int
) -> Dict:
    """比较模型预测与市场赔率"""
    model_probs = {
        "home_win": model_home,
        "draw": model_draw,
        "away_win": model_away,
    }
    
    consensus = get_consensus_odds(group, match_idx)
    
    if not consensus:
        raise HTTPException(status_code=404, detail="未找到市场赔率")
    
    comparison = compare_model_vs_market(model_probs, consensus["consensus"])
    
    return {
        "match": consensus["match"],
        "comparison": comparison,
    }


@router.get("/odds/championship")
async def api_get_championship_odds() -> Dict:
    """获取冠军赔率"""
    return get_championship_odds()


@router.get("/odds/value-rating")
async def api_get_value_rating(
    model_prob: float,
    market_odds: float
) -> Dict:
    """评估投注价值"""
    return get_value_rating(model_prob, market_odds)


# ==================== 社交情感API ====================
# 注意：具体路径必须在参数化路径之前定义！

@router.get("/sentiment/trending")
async def api_get_trending_teams() -> List[Dict]:
    """获取讨论热度排名"""
    return get_buzz_trending_teams()


@router.get("/sentiment/{team_code}")
async def api_get_team_sentiment(team_code: str) -> Dict:
    """获取球队社交媒体情感"""
    return get_team_sentiment(team_code.upper())


@router.get("/sentiment/compare/{home_code}/{away_code}")
async def api_compare_sentiments(home_code: str, away_code: str) -> Dict:
    """比较两队社交媒体情感"""
    return compare_sentiments(home_code.upper(), away_code.upper())


@router.get("/sentiment/impact/{team_code}")
async def api_get_sentiment_impact(team_code: str) -> Dict:
    """获取情感对比赛的影响"""
    impact = get_sentiment_impact(team_code.upper())
    sentiment = get_team_sentiment(team_code.upper())
    
    return {
        "team_code": team_code.upper(),
        "impact_score": impact,
        "overall_sentiment": sentiment["overall_sentiment"],
        "confidence_level": sentiment["confidence_level"],
        "buzz_score": sentiment["buzz_score"],
    }


@router.get("/sentiment/pressure/{team_code}")
async def api_get_pressure_analysis(team_code: str) -> Dict:
    """分析球队压力情况"""
    return get_pressure_analysis(team_code.upper())


# ==================== 综合数据API ====================

@router.get("/comprehensive/{home_code}/{away_code}")
async def api_get_comprehensive_data(
    home_code: str,
    away_code: str,
    group: Optional[str] = None,
    match_idx: Optional[int] = None
) -> Dict:
    """获取比赛的综合数据（伤病+赔率+情感）"""
    
    result = {
        "home_team": home_code.upper(),
        "away_team": away_code.upper(),
        "injuries": compare_injuries(home_code.upper(), away_code.upper()),
        "sentiment": compare_sentiments(home_code.upper(), away_code.upper()),
    }
    
    # 如果提供了比赛信息，添加赔率数据
    if group and match_idx is not None:
        odds_data = get_match_odds(group.upper(), match_idx)
        if odds_data:
            result["odds"] = {
                "bookmaker_odds": odds_data["odds"],
                "consensus_probability": odds_data["consensus"],
                "favorite": odds_data["favorite"],
            }
    
    # 计算综合优势
    injury_advantage = result["injuries"]["home_advantage"]
    sentiment_advantage = result["sentiment"]["overall_advantage"]
    
    result["composite_advantage"] = {
        "injury_factor": injury_advantage,
        "sentiment_factor": sentiment_advantage,
        "combined_score": round((injury_advantage + sentiment_advantage) / 2, 3),
        "advantage_team": "home" if (injury_advantage + sentiment_advantage) / 2 > 0.05 
                         else "away" if (injury_advantage + sentiment_advantage) / 2 < -0.05 
                         else "even",
    }
    
    return result


@router.get("/data-sources")
async def api_get_data_sources() -> Dict:
    """获取数据源信息"""
    return {
        "injuries": {
            "description": "球员伤病追踪系统",
            "update_frequency": "每日",
            "teams_covered": 15,
        },
        "odds": {
            "description": "博彩市场赔率数据",
            "bookmakers": ["Bet365", "William Hill", "Pinnacle", "DraftKings", "FanDuel"],
            "update_frequency": "实时",
        },
        "sentiment": {
            "description": "社交媒体情感分析",
            "platforms": ["Twitter/X", "Reddit", "微博", "Instagram", "YouTube", "TikTok"],
            "update_frequency": "每小时",
        },
    }
