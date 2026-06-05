"""
小组赛API路由 - 独立版（不依赖 prediction_engine_v3）
直接使用 ensemble 进行预测，包含三模型对比数据
"""
from fastapi import APIRouter
from typing import Dict, Any, List

import asyncio
import logging

from services.data_service import get_data_service
from services.ensemble_instance import get_ensemble
from data.world_cup_2026 import get_groups as get_groups_dict

from services.prediction_engine_v3 import create_prediction_engine, PredictionEngineV3

logger = logging.getLogger(__name__)

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
async def get_group_detail(group_name: str) -> Dict[str, Any]:
    """
    获取小组详情（积分榜 + 比赛预测 + 实际积分）
    
    包含：
    - 预测积分榜（期望值）
    - 实际积分榜（已揭晓的比赛）
    - 三模型对比
    - 贝叶斯因子
    """
    group_name = group_name.upper()
    logger.info(f"🔍 请求小组: {group_name}")
    
    ds = get_data_service()
    ensemble = get_ensemble()
    
    # 获取球队数据
    teams = await ds.get_group_teams(group_name)
    logger.info(f"🔍 球队数: {len(teams)}")
    if not teams:
        return {"error": f"小组不存在: {group_name}"}
    
    # 获取实际积分榜
    actual_standings = await ds.get_standings(group_name)
    logger.info(f"🔍 积分榜: {len(actual_standings)}")
    
    # 获取比赛数据
    matches_data = await ds.get_matches(group=group_name)
    logger.info(f"🔍 比赛数: {len(matches_data)}")
    
    # 构建积分榜（预测期望值 + 实际积分）
    standings = build_standings(teams, matches_data, ensemble, actual_standings)
    
    # 构建比赛列表（包含三模型对比）
    matches = build_matches(teams, matches_data, ensemble)
    logger.info(f"🔍 构建完成: standings={len(standings)}, matches={len(matches)}")
    
    return {
        "group": group_name,
        "standings": standings,
        "matches": matches,
        "data_source": ds.source_name,
        "is_realtime": ds.is_realtime
    }


def build_standings(teams: List, matches: List, ensemble, actual_standings: List) -> List[Dict]:
    """构建积分榜（预测期望值 + 实际积分）"""
    # 初始化积分
    table = {t["code"]: {
        "team": t,
        "expected_points": 0.0,
        "expected_w": 0.0,
        "expected_d": 0.0,
        "expected_l": 0.0
    } for t in teams}
    
    # 计算期望积分
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    for i, j in pairs:
        if i >= len(teams) or j >= len(teams):
            continue
        home, away = teams[i], teams[j]
        try:
            pred = ensemble.predict_match(home, away, "GROUP")
            bayesian = pred.bayesian_pred
            
            home_code = home["code"]
            away_code = away["code"]
            
            # 期望积分
            table[home_code]["expected_points"] += bayesian.home_win_prob * 3 + bayesian.draw_prob * 1
            table[away_code]["expected_points"] += bayesian.away_win_prob * 3 + bayesian.draw_prob * 1
            
            table[home_code]["expected_w"] += bayesian.home_win_prob
            table[home_code]["expected_d"] += bayesian.draw_prob
            table[home_code]["expected_l"] += bayesian.away_win_prob
            
            table[away_code]["expected_w"] += bayesian.away_win_prob
            table[away_code]["expected_d"] += bayesian.draw_prob
            table[away_code]["expected_l"] += bayesian.home_win_prob
        except Exception as e:
            logger.warning(f"预测失败: {e}")
    
    # 排序
    sorted_table = sorted(table.values(), key=lambda x: x["expected_points"], reverse=True)
    
    # 合并实际积分
    actual_map = {s["code"]: s for s in actual_standings}
    
    result = []
    for i, s in enumerate(sorted_table):
        team = s["team"]
        code = team["code"]
        act = actual_map.get(code, {})
        
        result.append({
            "position": i + 1,
            "code": code,
            "name": team.get("name"),
            "name_cn": team.get("name_cn"),
            "rank": team.get("rank", 99),
            # 预测
            "expected_points": round(s["expected_points"], 1),
            "expected_w": round(s["expected_w"], 1),
            "expected_d": round(s["expected_d"], 1),
            "expected_l": round(s["expected_l"], 1),
            # 实际
            "actual_points": act.get("points", 0),
            "actual_w": act.get("w", 0),
            "actual_d": act.get("d", 0),
            "actual_l": act.get("l", 0),
            "actual_gf": act.get("gf", 0),
            "actual_ga": act.get("ga", 0),
            "actual_gd": act.get("gd", 0),
            # 差异
            "diff": round(act.get("points", 0) - s["expected_points"], 1),
            "diff_text": "待比赛" if act.get("points", 0) == 0 else "符合预期"
        })
    
    return result


def build_matches(teams: List, matches_data: List, ensemble) -> List[Dict]:
    """构建比赛列表（包含三模型对比）"""
    result = []
    
    for m in matches_data:
        home_code = m.get("home") or m.get("home_code")
        away_code = m.get("away") or m.get("away_code")
        
        home_team = next((t for t in teams if t["code"] == home_code), None)
        away_team = next((t for t in teams if t["code"] == away_code), None)
        
        if not home_team or not away_team:
            logger.warning(f"找不到球队: {home_code} vs {away_code}")
            continue
        
        try:
            pred = ensemble.predict_match(home_team, away_team, "GROUP")
            bayesian = pred.bayesian_pred
            nn_pred = pred.nn_pred
            rf_pred = pred.rf_pred
            
            # 构建三模型对比
            models_comparison = {
                "bayesian": {
                    "home_win": round(bayesian.home_win_prob, 3) if bayesian else 0,
                    "draw": round(bayesian.draw_prob, 3) if bayesian else 0,
                    "away_win": round(bayesian.away_win_prob, 3) if bayesian else 0,
                    "result": "主胜" if bayesian and bayesian.home_win_prob > 0.5 else "平局" if bayesian and bayesian.draw_prob > 0.3 else "客胜"
                },
                "neural_network": {
                    "home_win": round(nn_pred.home_win_prob, 3) if nn_pred else 0.33,
                    "draw": round(nn_pred.draw_prob, 3) if nn_pred else 0.34,
                    "away_win": round(nn_pred.away_win_prob, 3) if nn_pred else 0.33,
                    "result": "主胜" if nn_pred and nn_pred.home_win_prob > 0.4 else "-"
                },
                "random_forest": {
                    "home_win": round(rf_pred.home_win_prob, 3) if rf_pred else 0.33,
                    "draw": round(rf_pred.draw_prob, 3) if rf_pred else 0.34,
                    "away_win": round(rf_pred.away_win_prob, 3) if rf_pred else 0.33,
                    "result": "主胜" if rf_pred and rf_pred.home_win_prob > 0.45 else "-"
                },
                "ensemble": {
                    "home_win": round(pred.ensemble_home_prob, 3),
                    "draw": round(pred.ensemble_draw_prob, 3),
                    "away_win": round(pred.ensemble_away_prob, 3),
                    "result": pred.ensemble_prediction
                }
            }
            
            # 贝叶斯因子
            bayesian_factors = {
                "elo_diff": home_team.get("elo", 1500) - away_team.get("elo", 1500),
                "rank_gap": away_team.get("rank", 99) - home_team.get("rank", 99),
                "confidence": round(bayesian.confidence, 2) if bayesian else 0
            } if bayesian else None
            
            result.append({
                "match_id": m.get("match_id"),
                "idx": m.get("match_index"),
                "home": home_code,
                "home_name_cn": home_team.get("name_cn", home_team.get("name")),
                "away": away_code,
                "away_name_cn": away_team.get("name_cn", away_team.get("name")),
                # 预测
                "home_win_prob": round(pred.ensemble_home_prob, 3),
                "draw_prob": round(pred.ensemble_draw_prob, 3),
                "away_win_prob": round(pred.ensemble_away_prob, 3),
                "prediction": pred.ensemble_prediction,
                "confidence": "高" if pred.ensemble_home_prob > 0.6 else "中" if pred.ensemble_home_prob > 0.4 else "低",
                # 实际
                "home_score": m.get("home_score"),
                "away_score": m.get("away_score"),
                "status": m.get("status"),
                "scheduled_time": m.get("scheduled_time"),
                # 三模型对比
                "models_comparison": models_comparison,
                # 贝叶斯因子
                "bayesian_factors": bayesian_factors,
                # 结果说明
                "result_text": f"预测: {pred.ensemble_prediction}"
            })
        except Exception as e:
            logger.error(f"构建比赛数据失败: {e}")
            result.append({
                "match_id": m.get("match_id"),
                "home": home_code,
                "away": away_code,
                "error": str(e)
            })
    
    logger.info(f"✅ 构建完成: {len(result)} 场比赛")
    return result