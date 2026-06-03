"""
2026世界杯球员伤病数据
追踪各队核心球员的伤病状态和恢复情况
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

# 伤病严重程度
INJURY_SEVERITY = {
    "minor": {"name": "轻伤", "impact": 0.15, "recovery_days": 7},
    "moderate": {"name": "中度伤病", "impact": 0.35, "recovery_days": 21},
    "severe": {"name": "重伤", "impact": 0.60, "recovery_days": 60},
    "season_ending": {"name": "赛季报销", "impact": 1.0, "recovery_days": 180},
}

# 伤病类型
INJURY_TYPES = {
    "muscle": "肌肉伤病",
    "knee": "膝盖伤病",
    "ankle": "脚踝伤病",
    "hamstring": "腿筋伤病",
    "groin": "腹股沟伤病",
    "back": "背部伤病",
    "shoulder": "肩部伤病",
    "concussion": "脑震荡",
    "covid": "新冠阳性",
    "fatigue": "疲劳累积",
}

# 球员伤病数据（模拟2026世界杯前实际情况）
INJURY_DATA = {
    # 阿根廷
    "ARG": [
        {
            "player_name": "Lionel Messi",
            "player_name_cn": "梅西",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态良好",
            "last_updated": "2026-05-20",
        },
        {
            "player_name": "Julián Álvarez",
            "player_name_cn": "阿尔瓦雷斯",
            "status": "doubtful",
            "injury_type": "ankle",
            "severity": "minor",
            "expected_return": "2026-06-05",
            "notes": "轻微脚踝扭伤，预计世界杯前复出",
            "last_updated": "2026-05-25",
        },
    ],
    
    # 法国
    "FRA": [
        {
            "player_name": "Kylian Mbappé",
            "player_name_cn": "姆巴佩",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态极佳",
            "last_updated": "2026-05-20",
        },
        {
            "player_name": "Antoine Griezmann",
            "player_name_cn": "格列兹曼",
            "status": "questionable",
            "injury_type": "muscle",
            "severity": "moderate",
            "expected_return": "2026-06-10",
            "notes": "小腿肌肉疲劳，预计首场小组赛复出",
            "last_updated": "2026-05-27",
        },
    ],
    
    # 巴西
    "BRA": [
        {
            "player_name": "Vinícius Jr.",
            "player_name_cn": "维尼修斯",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态巅峰",
            "last_updated": "2026-05-20",
        },
        {
            "player_name": "Neymar",
            "player_name_cn": "内马尔",
            "status": "out",
            "injury_type": "knee",
            "severity": "severe",
            "expected_return": "2026-08-01",
            "notes": "十字韧带撕裂，康复中，可能缺席世界杯",
            "last_updated": "2026-05-15",
        },
    ],
    
    # 德国
    "GER": [
        {
            "player_name": "Jamal Musiala",
            "player_name_cn": "穆西亚拉",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态出色",
            "last_updated": "2026-05-20",
        },
        {
            "player_name": "Manuel Neuer",
            "player_name_cn": "诺伊尔",
            "status": "questionable",
            "injury_type": "shoulder",
            "severity": "moderate",
            "expected_return": "2026-06-08",
            "notes": "肩部伤病恢复中，有望赶上世界杯",
            "last_updated": "2026-05-26",
        },
    ],
    
    # 英格兰
    "ENG": [
        {
            "player_name": "Harry Kane",
            "player_name_cn": "凯恩",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态稳定",
            "last_updated": "2026-05-20",
        },
        {
            "player_name": "Jude Bellingham",
            "player_name_cn": "贝林厄姆",
            "status": "doubtful",
            "injury_type": "fatigue",
            "severity": "minor",
            "expected_return": "2026-06-01",
            "notes": "赛季末疲劳累积，休息调整中",
            "last_updated": "2026-05-24",
        },
    ],
    
    # 西班牙
    "ESP": [
        {
            "player_name": "Pedri",
            "player_name_cn": "佩德里",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态良好",
            "last_updated": "2026-05-20",
        },
        {
            "player_name": "Gavi",
            "player_name_cn": "加维",
            "status": "out",
            "injury_type": "knee",
            "severity": "severe",
            "expected_return": "2026-09-01",
            "notes": "十字韧带手术，缺席世界杯",
            "last_updated": "2026-05-10",
        },
    ],
    
    # 葡萄牙
    "POR": [
        {
            "player_name": "Rafael Leão",
            "player_name_cn": "莱奥",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态良好",
            "last_updated": "2026-05-20",
        },
        {
            "player_name": "Cristiano Ronaldo",
            "player_name_cn": "C罗",
            "status": "doubtful",
            "injury_type": "muscle",
            "severity": "minor",
            "expected_return": "2026-06-05",
            "notes": "小腿轻微拉伤，预计康复",
            "last_updated": "2026-05-22",
        },
    ],
    
    # 荷兰
    "NED": [
        {
            "player_name": "Frenkie de Jong",
            "player_name_cn": "德容",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态良好",
            "last_updated": "2026-05-20",
        },
        {
            "player_name": "Virgil van Dijk",
            "player_name_cn": "范迪克",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态稳定",
            "last_updated": "2026-05-20",
        },
    ],
    
    # 乌拉圭
    "URU": [
        {
            "player_name": "Darwin Núñez",
            "player_name_cn": "努涅斯",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态良好",
            "last_updated": "2026-05-20",
        },
    ],
    
    # 克罗地亚
    "CRO": [
        {
            "player_name": "Luka Modrić",
            "player_name_cn": "莫德里奇",
            "status": "doubtful",
            "injury_type": "fatigue",
            "severity": "minor",
            "expected_return": "2026-06-01",
            "notes": "年龄因素，疲劳管理",
            "last_updated": "2026-05-23",
        },
    ],
    
    # 比利时
    "BEL": [
        {
            "player_name": "Kevin De Bruyne",
            "player_name_cn": "德布劳内",
            "status": "questionable",
            "injury_type": "hamstring",
            "severity": "moderate",
            "expected_return": "2026-06-10",
            "notes": "腿筋伤病恢复中，可能缺席首场",
            "last_updated": "2026-05-26",
        },
    ],
    
    # 塞内加尔
    "SEN": [
        {
            "player_name": "Sadio Mané",
            "player_name_cn": "马内",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态良好",
            "last_updated": "2026-05-20",
        },
    ],
    
    # 韩国
    "KOR": [
        {
            "player_name": "Son Heung-min",
            "player_name_cn": "孙兴慜",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态良好",
            "last_updated": "2026-05-20",
        },
    ],
    
    # 日本
    "JPN": [
        {
            "player_name": "Kaoru Mitoma",
            "player_name_cn": "三笘薰",
            "status": "healthy",
            "injury_type": None,
            "severity": None,
            "expected_return": None,
            "notes": "状态出色",
            "last_updated": "2026-05-20",
        },
    ],
}


def get_team_injuries(team_code: str) -> List[Dict]:
    """获取球队伤病名单"""
    return INJURY_DATA.get(team_code, [])


def get_injury_impact(team_code: str) -> float:
    """
    计算球队伤病影响系数 (0-1)
    0 = 无伤病影响
    1 = 严重伤病危机
    """
    injuries = INJURY_DATA.get(team_code, [])
    if not injuries:
        return 0.0
    
    total_impact = 0.0
    key_player_multiplier = 1.5  # 核心球员伤病影响更大
    
    for injury in injuries:
        if injury["status"] in ["out", "season_ending"]:
            severity = injury.get("severity", "moderate")
            impact = INJURY_SEVERITY.get(severity, INJURY_SEVERITY["moderate"])["impact"]
            
            # 检查是否为核心球员（从players.py可以获取）
            # 这里简化处理，假设伤病名单中的都是重要球员
            total_impact += impact * key_player_multiplier
        elif injury["status"] in ["doubtful", "questionable"]:
            severity = injury.get("severity", "minor")
            impact = INJURY_SEVERITY.get(severity, INJURY_SEVERITY["minor"])["impact"]
            total_impact += impact * 0.5  # 不确定缺席，影响减半
    
    # 归一化到 0-1 范围
    return min(1.0, total_impact / 2.0)


def get_injury_report(team_code: str) -> Dict:
    """生成球队伤病报告"""
    injuries = INJURY_DATA.get(team_code, [])
    impact = get_injury_impact(team_code)
    
    # 统计各类伤病状态
    status_count = {
        "healthy": 0,
        "doubtful": 0,
        "questionable": 0,
        "out": 0,
    }
    
    for injury in injuries:
        status = injury.get("status", "healthy")
        status_count[status] = status_count.get(status, 0) + 1
    
    # 生成风险等级
    if impact > 0.5:
        risk_level = "critical"
        risk_label = "严重伤病危机"
    elif impact > 0.3:
        risk_level = "high"
        risk_label = "伤病影响较大"
    elif impact > 0.15:
        risk_level = "moderate"
        risk_label = "有一定伤病影响"
    else:
        risk_level = "low"
        risk_label = "伤病情况良好"
    
    return {
        "team_code": team_code,
        "injury_list": injuries,
        "injury_count": len([i for i in injuries if i["status"] in ["out", "doubtful", "questionable"]]),
        "status_breakdown": status_count,
        "impact_coefficient": round(impact, 3),
        "risk_level": risk_level,
        "risk_label": risk_label,
        "last_updated": max([i["last_updated"] for i in injuries]) if injuries else "2026-05-20",
    }


def compare_injuries(home_code: str, away_code: str) -> Dict:
    """比较两队伤病情况"""
    home_report = get_injury_report(home_code)
    away_report = get_injury_report(away_code)
    
    # 计算伤病优势（对方伤病更严重则己方优势）
    home_advantage = away_report["impact_coefficient"] - home_report["impact_coefficient"]
    
    return {
        "home_injuries": home_report,
        "away_injuries": away_report,
        "home_advantage": round(home_advantage, 3),
        "advantage_team": "home" if home_advantage > 0.05 else "away" if home_advantage < -0.05 else "even",
        "summary": generate_injury_summary(home_report, away_report, home_advantage),
    }


def generate_injury_summary(home: Dict, away: Dict, advantage: float) -> str:
    """生成伤病情况文字摘要"""
    home_count = home["injury_count"]
    away_count = away["injury_count"]
    
    if advantage > 0.1:
        return f"主队伤病情况良好，客队有{away_count}名球员伤缺，主队占优"
    elif advantage > 0.05:
        return f"主队伤病情况略优于客队"
    elif advantage < -0.1:
        return f"客队伤病情况良好，主队有{home_count}名球员伤缺，客队占优"
    elif advantage < -0.05:
        return f"客队伤病情况略优于主队"
    else:
        return f"两队伤病情况相当，主队{home_count}人伤缺，客队{away_count}人伤缺"
