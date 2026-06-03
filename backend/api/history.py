"""
历史数据API路由 - 简化版
"""
from fastapi import APIRouter
from typing import Dict, Any, List

router = APIRouter(prefix="/api/data", tags=["历史数据"])


# 球队身价和历史数据（基于2026世界杯参赛队）
TEAM_DATA = {
    # 传统豪门
    "ARG": {"team_value": 850, "titles": 3, "finals": 5, "appearances": 18, "best_result": "冠军"},
    "BRA": {"team_value": 950, "titles": 5, "finals": 7, "appearances": 22, "best_result": "冠军"},
    "FRA": {"team_value": 900, "titles": 2, "finals": 3, "appearances": 16, "best_result": "冠军"},
    "GER": {"team_value": 750, "titles": 4, "finals": 8, "appearances": 20, "best_result": "冠军"},
    "ENG": {"team_value": 800, "titles": 1, "finals": 2, "appearances": 16, "best_result": "冠军"},
    "ESP": {"team_value": 700, "titles": 1, "finals": 2, "appearances": 16, "best_result": "冠军"},
    "ITA": {"team_value": 600, "titles": 4, "finals": 6, "appearances": 18, "best_result": "冠军"},
    "POR": {"team_value": 500, "titles": 0, "finals": 0, "appearances": 8, "best_result": "四强"},
    "NED": {"team_value": 600, "titles": 0, "finals": 3, "appearances": 11, "best_result": "亚军"},
    "BEL": {"team_value": 500, "titles": 0, "finals": 0, "appearances": 14, "best_result": "四强"},
    
    # 欧洲强队
    "CRO": {"team_value": 350, "titles": 0, "finals": 1, "appearances": 6, "best_result": "亚军"},
    "DEN": {"team_value": 300, "titles": 0, "finals": 0, "appearances": 6, "best_result": "四强"},
    "SWE": {"team_value": 250, "titles": 0, "finals": 1, "appearances": 12, "best_result": "亚军"},
    "NOR": {"team_value": 200, "titles": 0, "finals": 0, "appearances": 5, "best_result": "八强"},
    "AUT": {"team_value": 180, "titles": 0, "finals": 0, "appearances": 8, "best_result": "八强"},
    "TUR": {"team_value": 150, "titles": 0, "finals": 0, "appearances": 3, "best_result": "四强"},
    "UKR": {"team_value": 200, "titles": 0, "finals": 0, "appearances": 2, "best_result": "八强"},
    "SRB": {"team_value": 250, "titles": 0, "finals": 0, "appearances": 13, "best_result": "八强"},
    
    # 南美球队
    "URU": {"team_value": 400, "titles": 2, "finals": 2, "appearances": 14, "best_result": "冠军"},
    "COL": {"team_value": 250, "titles": 0, "finals": 0, "appearances": 6, "best_result": "八强"},
    "PAR": {"team_value": 150, "titles": 0, "finals": 0, "appearances": 11, "best_result": "八强"},
    "ECU": {"team_value": 200, "titles": 0, "finals": 0, "appearances": 4, "best_result": "十六强"},
    "VEN": {"team_value": 100, "titles": 0, "finals": 0, "appearances": 3, "best_result": "十六强"},
    
    # 北美球队
    "USA": {"team_value": 300, "titles": 0, "finals": 0, "appearances": 11, "best_result": "十六强"},
    "MEX": {"team_value": 180, "titles": 0, "finals": 0, "appearances": 17, "best_result": "八强"},
    "CAN": {"team_value": 100, "titles": 0, "finals": 0, "appearances": 2, "best_result": "小组赛"},
    
    # 亚洲球队
    "JPN": {"team_value": 150, "titles": 0, "finals": 0, "appearances": 7, "best_result": "十六强"},
    "KOR": {"team_value": 120, "titles": 0, "finals": 0, "appearances": 11, "best_result": "四强"},
    "AUS": {"team_value": 80, "titles": 0, "finals": 0, "appearances": 6, "best_result": "十六强"},
    "IRN": {"team_value": 50, "titles": 0, "finals": 0, "appearances": 6, "best_result": "小组赛"},
    "SAU": {"team_value": 60, "titles": 0, "finals": 0, "appearances": 6, "best_result": "小组赛"},
    "QAT": {"team_value": 40, "titles": 0, "finals": 0, "appearances": 1, "best_result": "小组赛"},
    "JOR": {"team_value": 30, "titles": 0, "finals": 0, "appearances": 2, "best_result": "小组赛"},
    "UZB": {"team_value": 25, "titles": 0, "finals": 0, "appearances": 2, "best_result": "小组赛"},
    "CHN": {"team_value": 50, "titles": 0, "finals": 0, "appearances": 2, "best_result": "小组赛"},
    
    # 非洲球队
    "SEN": {"team_value": 100, "titles": 0, "finals": 0, "appearances": 3, "best_result": "八强"},
    "MAR": {"team_value": 80, "titles": 0, "finals": 0, "appearances": 6, "best_result": "四强"},
    "NGA": {"team_value": 120, "titles": 0, "finals": 0, "appearances": 7, "best_result": "十六强"},
    "CIV": {"team_value": 100, "titles": 0, "finals": 0, "appearances": 4, "best_result": "小组赛"},
    "GHA": {"team_value": 90, "titles": 0, "finals": 0, "appearances": 4, "best_result": "十六强"},
    "CMR": {"team_value": 80, "titles": 0, "finals": 0, "appearances": 8, "best_result": "八强"},
    "COD": {"team_value": 50, "titles": 0, "finals": 0, "appearances": 1, "best_result": "小组赛"},
    "ALG": {"team_value": 70, "titles": 0, "finals": 0, "appearances": 5, "best_result": "十六强"},
    "EGY": {"team_value": 60, "titles": 0, "finals": 0, "appearances": 3, "best_result": "小组赛"},
    "TUN": {"team_value": 50, "titles": 0, "finals": 0, "appearances": 6, "best_result": "小组赛"},
    
    # 大洋洲
    "NZL": {"team_value": 30, "titles": 0, "finals": 0, "appearances": 3, "best_result": "小组赛"},
    
    # 其他参赛队（2026新增）
    "HAI": {"team_value": 20, "titles": 0, "finals": 0, "appearances": 1, "best_result": "小组赛"},
    "CUW": {"team_value": 15, "titles": 0, "finals": 0, "appearances": 1, "best_result": "小组赛"},
}


@router.get("/teams")
async def get_all_teams_data() -> Dict[str, Any]:
    """获取所有球队数据（含历史底蕴）"""
    # 合并身价和历史数据
    from data.world_cup_2026 import ALL_TEAMS
    
    result = []
    for team in ALL_TEAMS:
        code = team["code"]
        history = TEAM_DATA.get(code, {"team_value": 50, "titles": 0, "finals": 0, "appearances": 1, "best_result": "新军"})
        
        result.append({
            "code": code,
            "name": team.get("name", code),
            "name_cn": team.get("name_cn", code),
            "rank": team.get("rank", 50),
            "elo": team.get("elo", 1500),
            "form": team.get("form", "---"),
            "team_value": history["team_value"],
            "world_cup_experience": history["appearances"],
            "best_result": history["best_result"],
            "titles": history["titles"],
            "finals": history["finals"],
            "tier": get_tier(history["team_value"]),
            "pedigree": get_pedigree(history)
        })
    
    # 按身价排序
    result.sort(key=lambda x: -x.get("team_value", 0))
    
    return {
        "teams": result,
        "total": len(result)
    }


@router.get("/team/{team_code}")
async def get_team_history(team_code: str) -> Dict[str, Any]:
    """获取球队历史数据"""
    from data.world_cup_2026 import ALL_TEAMS
    
    team = next((t for t in ALL_TEAMS if t["code"] == team_code), None)
    if not team:
        return {"error": "球队不存在"}
    
    history = TEAM_DATA.get(team_code, {})
    
    return {
        "team": team,
        "history": history,
        "tier": get_tier(history.get("team_value", 50)),
        "pedigree": get_pedigree(history)
    }


@router.get("/h2h/{team_a}/{team_b}")
async def get_h2h(team_a: str, team_b: str) -> Dict[str, Any]:
    """获取两队历史交锋记录（模拟数据）"""
    # 基于球队实力生成模拟交锋数据
    from data.world_cup_2026 import ALL_TEAMS
    
    team_a_data = next((t for t in ALL_TEAMS if t["code"] == team_a), {"elo": 1500})
    team_b_data = next((t for t in ALL_TEAMS if t["code"] == team_b), {"elo": 1500})
    
    elo_diff = team_a_data.get("elo", 1500) - team_b_data.get("elo", 1500)
    
    # 根据实力差模拟历史交锋
    total = 10  # 模拟10场交锋
    if elo_diff > 100:
        team_a_wins = 6
        team_b_wins = 2
        draws = 2
    elif elo_diff > 50:
        team_a_wins = 5
        team_b_wins = 3
        draws = 2
    elif elo_diff > -50:
        team_a_wins = 4
        team_b_wins = 4
        draws = 2
    elif elo_diff > -100:
        team_a_wins = 3
        team_b_wins = 5
        draws = 2
    else:
        team_a_wins = 2
        team_b_wins = 6
        draws = 2
    
    return {
        "teams": {"home": team_a, "away": team_b},
        "summary": {
            "total": total,
            f"{team_a}_wins": team_a_wins,
            f"{team_b}_wins": team_b_wins,
            "draws": draws
        },
        "recent_matches": generate_mock_matches(team_a, team_b, team_a_wins, team_b_wins, draws)
    }


def get_tier(value: int) -> str:
    """获取球队等级"""
    if value >= 800:
        return "tier1"
    elif value >= 400:
        return "tier2"
    elif value >= 200:
        return "tier3"
    else:
        return "tier4"


def get_pedigree(history: dict) -> str:
    """获取底蕴等级"""
    titles = history.get("titles", 0)
    finals = history.get("finals", 0)
    appearances = history.get("appearances", 0)
    
    if titles >= 3:
        return "legendary"
    elif titles >= 1:
        return "champion"
    elif finals >= 1:
        return "finalist"
    elif appearances >= 10:
        return "regular"
    elif appearances >= 5:
        return "occasional"
    else:
        return "newcomer"


def generate_mock_matches(team_a: str, team_b: str, a_wins: int, b_wins: int, draws: int) -> List[dict]:
    """生成模拟交锋记录"""
    matches = []
    years = [2020, 2018, 2016, 2014, 2012, 2010, 2008, 2006, 2004, 2002]
    
    for i, year in enumerate(years[:a_wins]):
        matches.append({
            "year": year,
            "competition": "友谊赛",
            "result": f"{team_a}胜",
            "score": "2-1"
        })
    
    for i, year in enumerate(years[a_wins:a_wins+b_wins]):
        matches.append({
            "year": year,
            "competition": "友谊赛",
            "result": f"{team_b}胜",
            "score": "1-2"
        })
    
    for i, year in enumerate(years[a_wins+b_wins:]):
        matches.append({
            "year": year,
            "competition": "友谊赛",
            "result": "平局",
            "score": "1-1"
        })
    
    return matches