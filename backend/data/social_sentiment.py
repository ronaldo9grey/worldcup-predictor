"""
2026世界杯社交媒体情感数据
模拟球迷情绪分析，用于预测模型辅助判断
"""

from typing import Dict, List
from datetime import datetime
import random

# 社交平台数据源
SOCIAL_PLATFORMS = {
    "twitter": {"name": "Twitter/X", "weight": 0.30, "users": "全球"},
    "reddit": {"name": "Reddit", "weight": 0.20, "users": "北美+欧洲"},
    "weibo": {"name": "微博", "weight": 0.15, "users": "中国"},
    "instagram": {"name": "Instagram", "weight": 0.15, "users": "全球年轻用户"},
    "youtube": {"name": "YouTube", "weight": 0.10, "users": "全球"},
    "tiktok": {"name": "TikTok", "weight": 0.10, "users": "全球年轻用户"},
}

# 球队社交媒体情感数据（模拟2026世界杯前的球迷情绪）
TEAM_SENTIMENT = {
    # 热门球队
    "ARG": {
        "overall_sentiment": 0.78,  # 0-1范围，>0.5为正面
        "confidence_level": 0.82,  # 球迷信心度
        "buzz_score": 95,  # 讨论热度
        "recent_keywords": ["梅西最后一舞", "卫冕冠军", "团结", "冠军气质"],
        "negative_keywords": ["年龄", "伤病隐患"],
        "fan_expectation": "high",  # 高期望
        "pressure_level": "extreme",  # 极高压力
        "support_regions": ["阿根廷", "拉美", "全球梅西球迷"],
        "last_updated": "2026-05-25",
    },
    
    "FRA": {
        "overall_sentiment": 0.75,
        "confidence_level": 0.80,
        "buzz_score": 92,
        "recent_keywords": ["姆巴佩时代", "阵容深度", "2018冠军"],
        "negative_keywords": ["内讧传闻", "格列兹曼伤病"],
        "fan_expectation": "high",
        "pressure_level": "high",
        "support_regions": ["法国", "非洲法语区"],
        "last_updated": "2026-05-25",
    },
    
    "BRA": {
        "overall_sentiment": 0.72,
        "confidence_level": 0.78,
        "buzz_score": 90,
        "recent_keywords": ["维尼修斯崛起", "无内马尔", "新一代"],
        "negative_keywords": ["内马尔缺席", "防守不稳"],
        "fan_expectation": "high",
        "pressure_level": "extreme",
        "support_regions": ["巴西", "拉美"],
        "last_updated": "2026-05-25",
    },
    
    "ENG": {
        "overall_sentiment": 0.70,
        "confidence_level": 0.75,
        "buzz_score": 88,
        "recent_keywords": ["黄金一代", "贝林厄姆", "凯恩"],
        "negative_keywords": ["大赛软脚虾", "点球魔咒"],
        "fan_expectation": "high",
        "pressure_level": "high",
        "support_regions": ["英国", "英联邦"],
        "last_updated": "2026-05-25",
    },
    
    "GER": {
        "overall_sentiment": 0.65,
        "confidence_level": 0.70,
        "buzz_score": 85,
        "recent_keywords": ["穆西亚拉", "维尔茨", "复兴"],
        "negative_keywords": ["2018/2022失败", "诺伊尔年龄"],
        "fan_expectation": "moderate",
        "pressure_level": "high",
        "support_regions": ["德国", "欧洲"],
        "last_updated": "2026-05-25",
    },
    
    "ESP": {
        "overall_sentiment": 0.68,
        "confidence_level": 0.72,
        "buzz_score": 86,
        "recent_keywords": ["佩德里", "亚马尔", "年轻天才"],
        "negative_keywords": ["加维缺席", "缺乏射手"],
        "fan_expectation": "moderate",
        "pressure_level": "moderate",
        "support_regions": ["西班牙", "拉美西语区"],
        "last_updated": "2026-05-25",
    },
    
    "POR": {
        "overall_sentiment": 0.62,
        "confidence_level": 0.68,
        "buzz_score": 82,
        "recent_keywords": ["莱奥", "布鲁诺", "后C罗时代"],
        "negative_keywords": ["C罗争议", "依赖球星"],
        "fan_expectation": "moderate",
        "pressure_level": "moderate",
        "support_regions": ["葡萄牙", "葡萄牙侨民"],
        "last_updated": "2026-05-25",
    },
    
    "NED": {
        "overall_sentiment": 0.60,
        "confidence_level": 0.65,
        "buzz_score": 78,
        "recent_keywords": ["范迪克", "德容", "稳定"],
        "negative_keywords": ["缺乏超级球星"],
        "fan_expectation": "moderate",
        "pressure_level": "low",
        "support_regions": ["荷兰", "欧洲"],
        "last_updated": "2026-05-25",
    },
    
    # 中游球队
    "URU": {
        "overall_sentiment": 0.58,
        "confidence_level": 0.62,
        "buzz_score": 75,
        "recent_keywords": ["努涅斯", "老将传承"],
        "negative_keywords": [],
        "fan_expectation": "moderate",
        "pressure_level": "low",
        "support_regions": ["乌拉圭", "拉美"],
        "last_updated": "2026-05-25",
    },
    
    "BEL": {
        "overall_sentiment": 0.55,
        "confidence_level": 0.60,
        "buzz_score": 72,
        "recent_keywords": ["德布劳内", "黄金一代谢幕"],
        "negative_keywords": ["老化", "德布劳内伤病"],
        "fan_expectation": "low",
        "pressure_level": "moderate",
        "support_regions": ["比利时", "欧洲"],
        "last_updated": "2026-05-25",
    },
    
    "CRO": {
        "overall_sentiment": 0.57,
        "confidence_level": 0.62,
        "buzz_score": 70,
        "recent_keywords": ["莫德里奇最后一战", "2018/2022奇迹"],
        "negative_keywords": ["老龄化"],
        "fan_expectation": "moderate",
        "pressure_level": "low",
        "support_regions": ["克罗地亚", "巴尔干"],
        "last_updated": "2026-05-25",
    },
    
    # 东道主
    "USA": {
        "overall_sentiment": 0.65,
        "confidence_level": 0.70,
        "buzz_score": 80,
        "recent_keywords": ["主场优势", "普利西奇", "足球崛起"],
        "negative_keywords": ["经验不足"],
        "fan_expectation": "moderate",
        "pressure_level": "moderate",
        "support_regions": ["美国", "北美"],
        "last_updated": "2026-05-25",
    },
    
    "MEX": {
        "overall_sentiment": 0.60,
        "confidence_level": 0.65,
        "buzz_score": 78,
        "recent_keywords": ["第16场魔咒", "主场氛围"],
        "negative_keywords": ["近年低迷"],
        "fan_expectation": "moderate",
        "pressure_level": "high",
        "support_regions": ["墨西哥", "拉美", "美国墨西哥裔"],
        "last_updated": "2026-05-25",
    },
    
    "CAN": {
        "overall_sentiment": 0.55,
        "confidence_level": 0.60,
        "buzz_score": 65,
        "recent_keywords": ["主场", "新兴力量"],
        "negative_keywords": ["经验不足"],
        "fan_expectation": "low",
        "pressure_level": "low",
        "support_regions": ["加拿大"],
        "last_updated": "2026-05-25",
    },
    
    # 亚洲球队
    "JPN": {
        "overall_sentiment": 0.58,
        "confidence_level": 0.65,
        "buzz_score": 70,
        "recent_keywords": ["三笘薰", "技术流", "突破"],
        "negative_keywords": [],
        "fan_expectation": "moderate",
        "pressure_level": "moderate",
        "support_regions": ["日本", "东亚"],
        "last_updated": "2026-05-25",
    },
    
    "KOR": {
        "overall_sentiment": 0.56,
        "confidence_level": 0.62,
        "buzz_score": 68,
        "recent_keywords": ["孙兴慜", "不屈精神"],
        "negative_keywords": [],
        "fan_expectation": "moderate",
        "pressure_level": "moderate",
        "support_regions": ["韩国", "东亚"],
        "last_updated": "2026-05-25",
    },
    
    # 非洲球队
    "SEN": {
        "overall_sentiment": 0.55,
        "confidence_level": 0.60,
        "buzz_score": 65,
        "recent_keywords": ["马内", "2022突破"],
        "negative_keywords": [],
        "fan_expectation": "moderate",
        "pressure_level": "low",
        "support_regions": ["塞内加尔", "西非"],
        "last_updated": "2026-05-25",
    },
    
    "MAR": {
        "overall_sentiment": 0.60,
        "confidence_level": 0.68,
        "buzz_score": 72,
        "recent_keywords": ["2022奇迹", "非洲骄傲"],
        "negative_keywords": [],
        "fan_expectation": "moderate",
        "pressure_level": "low",
        "support_regions": ["摩洛哥", "北非", "阿拉伯世界"],
        "last_updated": "2026-05-25",
    },
}


def get_team_sentiment(team_code: str) -> Dict:
    """获取球队社交媒体情感"""
    return TEAM_SENTIMENT.get(team_code, {
        "overall_sentiment": 0.50,
        "confidence_level": 0.50,
        "buzz_score": 50,
        "recent_keywords": [],
        "negative_keywords": [],
        "fan_expectation": "low",
        "pressure_level": "low",
        "support_regions": [],
        "last_updated": "2026-05-25",
    })


def get_sentiment_impact(team_code: str) -> float:
    """
    计算情感因素对比赛的影响 (-1到1)
    正值：球迷信心高，可能带来积极影响
    负值：球迷悲观，可能带来消极影响
    """
    sentiment = get_team_sentiment(team_code)
    
    # 综合情感和信心
    overall = sentiment["overall_sentiment"]
    confidence = sentiment["confidence_level"]
    pressure = sentiment.get("pressure_level", "low")
    
    # 基础影响
    impact = (overall - 0.5) * 2 + (confidence - 0.5) * 0.5
    
    # 压力调整（高压力可能反而产生负面影响）
    pressure_penalty = {
        "extreme": -0.05,  # 过高压力可能导致紧张
        "high": 0.0,
        "moderate": 0.02,
        "low": 0.03,
    }
    
    impact += pressure_penalty.get(pressure, 0)
    
    return max(-1, min(1, impact))


def compare_sentiments(home_code: str, away_code: str) -> Dict:
    """比较两队社交媒体情感"""
    home_sentiment = get_team_sentiment(home_code)
    away_sentiment = get_team_sentiment(away_code)
    
    home_impact = get_sentiment_impact(home_code)
    away_impact = get_sentiment_impact(away_code)
    
    # 计算情感优势
    sentiment_diff = home_sentiment["overall_sentiment"] - away_sentiment["overall_sentiment"]
    confidence_diff = home_sentiment["confidence_level"] - away_sentiment["confidence_level"]
    buzz_diff = home_sentiment["buzz_score"] - away_sentiment["buzz_score"]
    
    return {
        "home_sentiment": home_sentiment,
        "away_sentiment": away_sentiment,
        "home_impact": round(home_impact, 3),
        "away_impact": round(away_impact, 3),
        "sentiment_advantage": round(sentiment_diff, 3),
        "confidence_advantage": round(confidence_diff, 3),
        "buzz_advantage": round(buzz_diff, 3),
        "overall_advantage": round(home_impact - away_impact, 3),
        "advantage_team": "home" if home_impact > away_impact + 0.05 else "away" if away_impact > home_impact + 0.05 else "even",
        "summary": generate_sentiment_summary(home_sentiment, away_sentiment),
    }


def generate_sentiment_summary(home: Dict, away: Dict) -> str:
    """生成情感对比摘要"""
    home_sentiment = home["overall_sentiment"]
    away_sentiment = away["overall_sentiment"]
    
    if home_sentiment > 0.7 and away_sentiment < 0.55:
        return f"主队球迷信心高涨({home_sentiment:.1%})，客队较为悲观({away_sentiment:.1%})"
    elif home_sentiment > 0.65 and away_sentiment > 0.65:
        return f"两队球迷信心都很充足，气氛热烈"
    elif home_sentiment < 0.55 and away_sentiment < 0.55:
        return f"两队球迷信心都不足，气氛低迷"
    elif home_sentiment > away_sentiment + 0.1:
        return f"主队球迷信心高于客队，心理优势"
    elif away_sentiment > home_sentiment + 0.1:
        return f"客队球迷信心更高，可能爆冷"
    else:
        return f"两队球迷信心相当"


def get_buzz_trending_teams() -> List[Dict]:
    """获取讨论热度最高的球队"""
    teams = sorted(
        [(code, data["buzz_score"]) for code, data in TEAM_SENTIMENT.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    return [
        {"team": code, "buzz_score": score, "rank": i + 1}
        for i, (code, score) in enumerate(teams[:10])
    ]


def get_pressure_analysis(team_code: str) -> Dict:
    """分析球队压力情况"""
    sentiment = get_team_sentiment(team_code)
    expectation = sentiment.get("fan_expectation", "low")
    pressure = sentiment.get("pressure_level", "low")
    
    # 压力风险评估
    if expectation == "high" and pressure == "extreme":
        risk = "critical"
        risk_label = "极高压力风险，可能影响发挥"
    elif expectation == "high" and pressure == "high":
        risk = "high"
        risk_label = "高压力，需要心理调适"
    elif expectation == "moderate":
        risk = "moderate"
        risk_label = "适中压力，正常范围"
    else:
        risk = "low"
        risk_label = "低压力，轻松心态"
    
    return {
        "team_code": team_code,
        "fan_expectation": expectation,
        "pressure_level": pressure,
        "pressure_risk": risk,
        "risk_label": risk_label,
        "recommendation": "保持冷静，专注比赛" if risk in ["critical", "high"] else "正常备战",
    }


def simulate_live_sentiment(team_code: str, match_progress: int = 0) -> Dict:
    """模拟比赛中实时情感变化（用于未来功能）"""
    base_sentiment = get_team_sentiment(team_code)
    
    # 模拟比赛中的情感波动
    if match_progress > 60:  # 比赛进行60分钟后
        volatility = 0.15  # 情感波动增大
        current_sentiment = base_sentiment["overall_sentiment"] + random.uniform(-volatility, volatility)
    else:
        volatility = 0.05
        current_sentiment = base_sentiment["overall_sentiment"] + random.uniform(-volatility, volatility)
    
    return {
        "team_code": team_code,
        "base_sentiment": round(base_sentiment["overall_sentiment"], 3),
        "current_sentiment": round(max(0, min(1, current_sentiment)), 3),
        "volatility": round(volatility, 3),
        "trending_keywords": base_sentiment["recent_keywords"][:3],
        "match_progress": match_progress,
    }