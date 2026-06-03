"""小组赛API路由"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from services.prediction_engine_v3 import create_prediction_engine, PredictionEngineV3
from data.world_cup_2026 import get_groups

# 使用兼容的GROUPS
GROUPS = get_groups()

router = APIRouter(prefix="/api/groups", tags=["小组赛"])


def get_engine() -> PredictionEngineV3:
    """获取预测引擎实例（依赖注入）"""
    # 这里可以注入数据库和提供者
    return create_prediction_engine()


@router.get("")
async def get_groups() -> Dict[str, Any]:
    """获取所有小组信息"""
    return {
        "groups": [
            {
                "group": gname,
                "teams": [
                    {
                        "code": t["code"],
                        "name": t["name"],
                        "name_cn": t["name_cn"],
                        "rank": t["rank"],
                        "elo": t["elo"]
                    }
                    for t in teams
                ]
            }
            for gname, teams in GROUPS.items()
        ]
    }


@router.get("/{group_name}")
async def get_group_detail(
    group_name: str,
    engine: PredictionEngineV3 = Depends(get_engine)
) -> Dict[str, Any]:
    """获取小组详情（积分榜 + 比赛预测）"""
    teams = GROUPS.get(group_name.upper())
    if not teams:
        return {"error": f"小组不存在: {group_name}"}
    
    # 生成小组赛对阵
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    matches = []
    
    for idx, (i, j) in enumerate(pairs):
        home, away = teams[i], teams[j]
        pred = engine.predict_match(home, away, stage="GROUP", is_neutral=True)
        
        matches.append({
            "idx": idx,
            "home": home["code"],
            "home_name_cn": home["name_cn"],
            "away": away["code"],
            "away_name_cn": away["name_cn"],
            "home_win_prob": pred.home_win_prob,
            "draw_prob": pred.draw_prob,
            "away_win_prob": pred.away_win_prob,
            "prediction": pred.prediction,
            "confidence": pred.confidence,
            "upset_score": pred.upset_score,
            "is_upset": pred.is_upset
        })
    
    # 模拟积分榜
    standings = simulate_group_standings(teams, matches)
    
    return {
        "group": group_name.upper(),
        "standings": standings,
        "matches": matches
    }


def simulate_group_standings(teams: list, matches: list) -> list:
    """模拟小组积分榜"""
    # 初始化积分
    table = {
        t["code"]: {"team": t, "points": 0, "w": 0, "d": 0, "l": 0, "gf": 0, "ga": 0}
        for t in teams
    }
    
    # 根据预测概率模拟结果
    import random
    for m in matches:
        probs = [m["home_win_prob"], m["draw_prob"], m["away_win_prob"]]
        result = random.choices(["HOME", "DRAW", "AWAY"], weights=probs)[0]
        
        home, away = m["home"], m["away"]
        
        if result == "HOME":
            table[home]["points"] += 3
            table[home]["w"] += 1
            table[away]["l"] += 1
            table[home]["gf"] += random.randint(1, 3)
            table[away]["ga"] += table[home]["gf"] - table[away]["gf"]
        elif result == "DRAW":
            table[home]["points"] += 1
            table[away]["points"] += 1
            table[home]["d"] += 1
            table[away]["d"] += 1
            goals = random.randint(0, 2)
            table[home]["gf"] += goals
            table[away]["gf"] += goals
        else:
            table[away]["points"] += 3
            table[away]["w"] += 1
            table[home]["l"] += 1
            table[away]["gf"] += random.randint(1, 3)
            table[home]["ga"] += table[away]["gf"] - table[home]["gf"]
    
    # 排序
    sorted_table = sorted(
        table.values(),
        key=lambda x: (x["points"], x["gf"] - x["ga"], x["gf"]),
        reverse=True
    )
    
    return [
        {
            "position": i + 1,
            "code": s["team"]["code"],
            "name": s["team"]["name"],
            "name_cn": s["team"]["name_cn"],
            "rank": s["team"]["rank"],
            "points": s["points"],
            "w": s["w"],
            "d": s["d"],
            "l": s["l"],
            "gf": s["gf"],
            "ga": s["ga"],
            "gd": s["gf"] - s["ga"]
        }
        for i, s in enumerate(sorted_table)
    ]