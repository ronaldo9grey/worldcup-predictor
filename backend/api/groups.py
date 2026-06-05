"""
小组赛API路由 - 改造版
接入 WorldCup26.ir 实时数据，展示预测 vs 实际积分对比
"""
from fastapi import APIRouter, Depends
from typing import Dict, Any, List
import asyncio

from services.prediction_engine_v3 import create_prediction_engine, PredictionEngineV3
from services.data_service import get_data_service
from data.world_cup_2026 import get_groups as get_groups_dict

# 使用兼容的GROUPS（用于预测引擎）
GROUPS = get_groups_dict()

router = APIRouter(prefix="/api/groups", tags=["小组赛"])


def get_engine() -> PredictionEngineV3:
    """获取预测引擎实例"""
    return create_prediction_engine()


@router.get("")
async def get_groups() -> Dict[str, Any]:
    """获取所有小组信息"""
    ds = get_data_service()
    
    # 从数据服务获取球队信息
    all_teams = await ds.get_all_teams()
    groups_data = await ds.get_groups()
    
    return {
        "groups": [
            {
                "group": gname,
                "teams": [
                    {
                        "code": t.get("code"),
                        "name": t.get("name"),
                        "name_cn": t.get("name_cn"),
                        "rank": t.get("rank"),
                        "elo": t.get("elo"),
                        "flag": f"https://flagcdn.com/w40/{t.get('code', '').lower()}.png"
                    }
                    for code in codes
                    for t in all_teams
                    if t.get("code") == code
                ]
            }
            for gname, codes in groups_data.items()
        ]
    }


@router.get("/{group_name}")
async def get_group_detail(
    group_name: str,
    engine: PredictionEngineV3 = Depends(get_engine)
) -> Dict[str, Any]:
    """
    获取小组详情（积分榜 + 比赛预测 + 实际积分）
    
    展示：
    - 预测积分榜（基于概率的期望值）
    - 实际积分榜（已揭晓的比赛）
    - 对比差异
    """
    group_name = group_name.upper()
    
    ds = get_data_service()
    
    # 获取球队数据
    teams = await ds.get_group_teams(group_name)
    if not teams:
        return {"error": f"小组不存在: {group_name}"}
    
    # 获取实际积分榜（WorldCup26.ir）
    actual_standings = await ds.get_standings(group_name)
    
    # 获取比赛数据（WorldCup26.ir）
    matches_data = await ds.get_matches(group=group_name)
    
    # 生成预测积分榜（期望值）
    predicted_standings = calculate_expected_standings(teams, matches_data, engine)
    
    # 合并预测和实际数据
    combined_standings = combine_standings(predicted_standings, actual_standings, teams)
    
    # 构建比赛列表（含预测 + 实际结果）
    matches_with_result = []
    for m in matches_data:
        # m 是字典格式
        home_code = m.get("home_code") or m.get("home")
        away_code = m.get("away_code") or m.get("away")
        
        home_team = next((t for t in teams if t["code"] == home_code), None)
        away_team = next((t for t in teams if t["code"] == away_code), None)
        
        if home_team and away_team:
            # 预测
            pred = engine.predict_match(home_team, away_team, stage="GROUP", is_neutral=True)
            
            matches_with_result.append({
                "idx": m.get("match_index"),
                "home": home_team["code"],
                "home_name_cn": home_team.get("name_cn", home_team["name"]),
                "away": away_team["code"],
                "away_name_cn": away_team.get("name_cn", away_team["name"]),
                # 预测数据
                "home_win_prob": pred.home_win_prob,
                "draw_prob": pred.draw_prob,
                "away_win_prob": pred.away_win_prob,
                "prediction": pred.prediction,
                "confidence": pred.confidence,
                # 实际数据
                "home_score": m.get("home_score"),
                "away_score": m.get("away_score"),
                "status": m.get("status"),  # scheduled, live, finished
                "scheduled_time": m.get("scheduled_time"),
                # 结果说明
                "result_text": get_result_text(m, pred)
            })
    
    return {
        "group": group_name,
        "standings": combined_standings,
        "matches": matches_with_result,
        "data_source": ds.source_name,
        "is_realtime": ds.is_realtime
    }


def calculate_expected_standings(
    teams: List[Dict],
    matches_data: List[Any],
    engine: PredictionEngineV3
) -> List[Dict]:
    """
    计算预测积分榜（期望值）
    
    期望积分 = 主胜概率 × 3 + 平局概率 × 1
    """
    # 初始化积分
    table = {t["code"]: {
        "team": t,
        "expected_points": 0.0,
        "expected_w": 0.0,
        "expected_d": 0.0,
        "expected_l": 0.0
    } for t in teams}
    
    # 对每场比赛计算期望积分
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    
    for idx, (i, j) in enumerate(pairs):
        if i >= len(teams) or j >= len(teams):
            continue
        
        home, away = teams[i], teams[j]
        pred = engine.predict_match(home, away, stage="GROUP", is_neutral=True)
        
        home_code = home["code"]
        away_code = away["code"]
        
        # 期望积分 = P(主胜) × 3 + P(平) × 1
        table[home_code]["expected_points"] += pred.home_win_prob * 3 + pred.draw_prob * 1
        table[away_code]["expected_points"] += pred.away_win_prob * 3 + pred.draw_prob * 1
        
        # 期望胜/平/负场数
        table[home_code]["expected_w"] += pred.home_win_prob
        table[home_code]["expected_d"] += pred.draw_prob
        table[home_code]["expected_l"] += pred.away_win_prob
        
        table[away_code]["expected_w"] += pred.away_win_prob
        table[away_code]["expected_d"] += pred.draw_prob
        table[away_code]["expected_l"] += pred.home_win_prob
    
    # 排序
    sorted_table = sorted(
        table.values(),
        key=lambda x: x["expected_points"],
        reverse=True
    )
    
    return [
        {
            "position": i + 1,
            "code": s["team"]["code"],
            "name": s["team"]["name"],
            "name_cn": s["team"].get("name_cn", s["team"]["name"]),
            "rank": s["team"].get("rank", 99),
            "expected_points": round(s["expected_points"], 1),
            "expected_w": round(s["expected_w"], 1),
            "expected_d": round(s["expected_d"], 1),
            "expected_l": round(s["expected_l"], 1)
        }
        for i, s in enumerate(sorted_table)
    ]


def combine_standings(
    predicted: List[Dict],
    actual: List[Dict],
    teams: List[Dict]
) -> List[Dict]:
    """
    合并预测积分和实际积分
    """
    # 构建映射
    predicted_map = {s["code"]: s for s in predicted}
    actual_map = {s["code"]: s for s in actual}
    
    combined = []
    
    for team in teams:
        code = team["code"]
        pred = predicted_map.get(code, {})
        act = actual_map.get(code, {})
        
        # 实际积分（如果有的话）
        actual_points = act.get("points", 0)
        actual_w = act.get("w", 0)
        actual_d = act.get("d", 0)
        actual_l = act.get("l", 0)
        actual_gf = act.get("gf", 0)
        actual_ga = act.get("ga", 0)
        actual_gd = act.get("gd", 0)
        
        # 预测积分
        expected_points = pred.get("expected_points", 0)
        expected_w = pred.get("expected_w", 0)
        expected_d = pred.get("expected_d", 0)
        expected_l = pred.get("expected_l", 0)
        
        # 计算差异
        diff = actual_points - expected_points
        
        combined.append({
            "position": pred.get("position", 0),
            "code": code,
            "name": team.get("name", code),
            "name_cn": team.get("name_cn", code),
            "rank": team.get("rank", 99),
            
            # 预测数据
            "expected_points": expected_points,
            "expected_w": expected_w,
            "expected_d": expected_d,
            "expected_l": expected_l,
            
            # 实际数据
            "actual_points": actual_points,
            "actual_w": actual_w,
            "actual_d": actual_d,
            "actual_l": actual_l,
            "actual_gf": actual_gf,
            "actual_ga": actual_ga,
            "actual_gd": actual_gd,
            
            # 差异
            "diff": round(diff, 1),
            "diff_text": get_diff_text(diff, actual_points)
        })
    
    # 按实际积分排序（如果没有，按预测积分）
    combined.sort(key=lambda x: (
        -x.get("actual_points", 0),  # 实际积分降序
        -x.get("actual_gd", 0),      # 净胜球
        -x.get("actual_gf", 0),      # 进球数
        -x.get("expected_points", 0)  # 预测积分
    ))
    
    # 更新排名
    for i, s in enumerate(combined):
        s["position"] = i + 1
    
    return combined


def get_diff_text(diff: float, actual_points: int) -> str:
    """获取差异说明文本"""
    if actual_points == 0:
        return "待比赛"
    elif diff > 0.5:
        return f"超出预期 +{diff:.1f}"
    elif diff < -0.5:
        return f"低于预期 {diff:.1f}"
    else:
        return "符合预期"


def get_result_text(match: Dict, pred) -> str:
    """获取比赛结果说明"""
    status = match.get("status", "scheduled")
    home_score = match.get("home_score")
    away_score = match.get("away_score")
    
    if status == "scheduled":
        confidence = pred.confidence
        if isinstance(confidence, str):
            return f"预测: {pred.prediction} ({confidence})"
        else:
            return f"预测: {pred.prediction} ({confidence:.0%})"
    elif status == "live":
        return f"进行中: {home_score} - {away_score}"
    else:  # finished
        if home_score is not None and away_score is not None:
            if home_score > away_score:
                result = "主胜"
            elif home_score < away_score:
                result = "客胜"
            else:
                result = "平局"
            return f"已揭晓: {home_score}-{away_score} ({result})"
        return "已结束"
