"""
单场比赛预测计算过程API
"""
from fastapi import APIRouter
from typing import Dict, Any

from data.world_cup_2026 import GROUPS, ALL_TEAMS, get_groups as get_groups_dict
from data.players import get_team_squad, get_squad_strength, compare_squads
from data.coaches import get_coach_info, calculate_coach_rating, compare_coaches
from data.venue_weather import get_venue_factor_for_match, get_match_venue
from services.ensemble_instance import get_ensemble
from services.score_predictor import ScorePredictor

router = APIRouter(prefix="/api/calculation", tags=["计算过程"])


# 权重配置
WEIGHTS = {
    "elo_diff": 0.28,
    "form_diff": 0.18,
    "rank_diff": 0.10,
    "home_advantage": 0.08,
    "stage_factor": 0.15,
    "continent_factor": 0.05,
    "h2h": 0.07,
    "wc_experience": 0.07,
    # 新增因素
    "squad_strength": 0.12,
    "coach_rating": 0.08,
    "venue_factor": 0.05
}


def get_team_lookup():
    """获取球队查询表"""
    teams = {}
    groups_full = get_groups_dict()
    for gteams in groups_full.values():
        for t in gteams:
            teams[t["code"]] = t
    return teams


def format_value(val, decimals=2):
    """格式化数值，保留指定小数位"""
    if isinstance(val, (int, float)):
        return round(val, decimals)
    return val



def calculate_match_prediction(home_code: str, away_code: str, group: str, match_index: int) -> Dict[str, Any]:
    """
    计算单场比赛的完整预测过程
    
    返回详细的计算步骤和数据
    """
    teams = get_team_lookup()
    home_team = teams.get(home_code, {"code": home_code, "elo": 1500, "rank": 50, "continent": "EU"})
    away_team = teams.get(away_code, {"code": away_code, "elo": 1500, "rank": 50, "continent": "EU"})
    
    # 步骤1: 提取原始数据
    elo_diff_raw = home_team.get("elo", 1500) - away_team.get("elo", 1500)
    rank_diff_raw = away_team.get("rank", 50) - home_team.get("rank", 50)  # 排名越小越好
    
    # 步骤2: 标准化因子
    factors = {
        "elo_diff": {
            "raw": format_value(elo_diff_raw),
            "normalized": normalize(elo_diff_raw, 300),
            "meaning": "主队Elo评分" + ("更高" if elo_diff_raw > 0 else "更低" if elo_diff_raw < 0 else "相当")
        },
        "rank_diff": {
            "raw": format_value(rank_diff_raw),
            "normalized": normalize(rank_diff_raw, 50),
            "meaning": "主队排名" + ("更高" if rank_diff_raw > 0 else "更低" if rank_diff_raw < 0 else "相当")
        },
        "form_diff": {
            "raw": 0,
            "normalized": 0.0,
            "meaning": "两队状态相当"
        },
        "stage_factor": {
            "raw": 1.0,
            "normalized": 0.5,
            "meaning": "小组赛阶段"
        },
        "home_advantage": {
            "raw": format_value(0 if group in ["A", "B", "C", "D", "E", "F", "G", "H"] else 50),
            "normalized": 0.0 if group in ["A", "B", "C", "D", "E", "F", "G", "H"] else 0.15,
            "meaning": "中立场（无主场优势）" if group in ["A", "B", "C", "D", "E", "F", "G", "H"] else "东道主优势"
        },
        "continent_factor": {
            "raw": 1 if home_team.get("continent") == away_team.get("continent") else 0,
            "normalized": 0.1 if home_team.get("continent") == "EU" and away_team.get("continent") != "EU" else -0.05 if home_team.get("continent") != "EU" and away_team.get("continent") == "EU" else 0.0,
            "meaning": "同洲对决" if home_team.get("continent") == away_team.get("continent") else "欧洲球队占优" if away_team.get("continent") == "EU" else "非欧洲球队"
        },
        "h2h": {
            "raw": 0,
            "normalized": 0.0,
            "meaning": "历史交锋记录不足"
        },
        "wc_experience": {
            "raw": format_value(home_team.get("wc_titles", 0) - away_team.get("wc_titles", 0)),
            "normalized": normalize(home_team.get("wc_titles", 0) - away_team.get("wc_titles", 0), 5),
            "meaning": f"主队{home_team.get('wc_titles', 0)}次夺冠 vs 客队{away_team.get('wc_titles', 0)}次"
        },
        # 新增因素：球员阵容
        "squad_strength": {
            "raw": format_value(get_squad_strength(home_code) - get_squad_strength(away_code)),
            "normalized": normalize(get_squad_strength(home_code) - get_squad_strength(away_code), 30),
            "meaning": "阵容实力相当"
        },
        # 新增因素：教练能力
        "coach_rating": {
            "raw": format_value(calculate_coach_rating(home_code) - calculate_coach_rating(away_code)),
            "normalized": normalize(calculate_coach_rating(home_code) - calculate_coach_rating(away_code), 20),
            "meaning": compare_coaches(home_code, away_code)['analysis']
        },
        # 新增因素：场地影响
        "venue_factor": {
            "raw": format_value(get_venue_factor_for_match(group, home_code, away_code)['home_advantage'] * 100),
            "normalized": get_venue_factor_for_match(group, home_code, away_code)['home_advantage'],
            "meaning": get_venue_factor_for_match(group, home_code, away_code)['analysis']
        }
    }
    
    # 步骤3: 计算加权贡献
    total_contribution = sum(
        factors[key]["normalized"] * weight 
        for key, weight in WEIGHTS.items()
    )
    
    # 步骤4: 计算概率
    import math
    
    # 使用逻辑函数计算概率
    home_base = 0.35 + total_contribution * 0.5
    draw_base = 0.30 - abs(total_contribution) * 0.2
    away_base = 0.35 - total_contribution * 0.5
    
    # 归一化
    total = home_base + draw_base + away_base
    probabilities = {
        "home_win": max(0.05, min(0.85, home_base / total)),
        "draw": max(0.05, min(0.35, draw_base / total)),
        "away_win": max(0.05, min(0.85, away_base / total))
    }
    
    # 确保概率和为1
    prob_total = sum(probabilities.values())
    probabilities = {k: v/prob_total for k, v in probabilities.items()}
    
    # 确定预测结果
    if probabilities["home_win"] > probabilities["away_win"] and probabilities["home_win"] > probabilities["draw"]:
        prediction = "HOME_WIN"
    elif probabilities["away_win"] > probabilities["home_win"] and probabilities["away_win"] > probabilities["draw"]:
        prediction = "AWAY_WIN"
    else:
        prediction = "DRAW"
    
    # 确定置信度
    max_prob = max(probabilities.values())
    if max_prob > 0.6:
        confidence = "高"
    elif max_prob > 0.45:
        confidence = "中"
    else:
        confidence = "低"
    
    return {
        # 比赛信息
        "match_id": f"{group}_{match_index}",
        "group": group,
        "match_index": match_index,
        
        # 球队信息
        "home": {
            "code": home_code,
            "name_cn": home_team.get("name_cn", home_code),
            "elo": home_team.get("elo", 1500),
            "rank": home_team.get("rank", 50),
            "form": home_team.get("form", "---"),
            "continent": home_team.get("continent", "EU"),
            "wc_titles": home_team.get("wc_titles", 0)
        },
        "away": {
            "code": away_code,
            "name_cn": away_team.get("name_cn", away_code),
            "elo": away_team.get("elo", 1500),
            "rank": away_team.get("rank", 50),
            "form": away_team.get("form", "---"),
            "continent": away_team.get("continent", "EU"),
            "wc_titles": away_team.get("wc_titles", 0)
        },
        
        # 因子详情
        "factors": factors,
        
        # 权重配置
        "weights": WEIGHTS,
        
        # 计算结果
        "total_contribution": total_contribution,
        "probabilities": probabilities,
        "prediction": prediction,
        "confidence": confidence,
        
        # 新增：球员阵容信息
        "squad_info": compare_squads(home_code, away_code),
        
        # 新增：教练信息
        "coach_info": compare_coaches(home_code, away_code),
        
        # 新增：场地天气信息
        "venue_info": get_venue_factor_for_match(group, home_code, away_code)
    }


def normalize(value: float, scale: float) -> float:
    """标准化到[-1, 1]区间"""
    return max(-1, min(1, value / scale))


@router.get("/match/{group}/{match_index}")
async def get_match_calculation(group: str, match_index: int) -> Dict[str, Any]:
    """
    获取单场比赛的计算过程
    
    使用集成模型的贝叶斯部分，确保与三模型对比数据一致
    
    Args:
        group: 小组名称 (A-L)
        match_index: 比赛索引 (0-5)
    """
    # 获取小组球队（使用完整队伍信息）
    groups_full = get_groups_dict()
    group_teams = groups_full.get(group.upper(), [])
    if len(group_teams) < 4:
        return {"error": "小组不存在"}
    
    # 确定比赛对阵（与前端 generate_match_schedule 保持一致）
    match_pairings = [(0, 1), (2, 3), (0, 2), (1, 3), (0, 3), (1, 2)]
    
    if match_index < 0 or match_index >= len(match_pairings):
        return {"error": "比赛索引无效"}
    
    home_idx, away_idx = match_pairings[match_index]
    home_team = group_teams[home_idx]
    away_team = group_teams[away_idx]
    home_code = home_team["code"]
    away_code = away_team["code"]
    
    # 获取实时比赛数据
    match_status = "待揭晓"
    home_score = None
    away_score = None
    
    # 球队代码映射（API返回的代码 -> 本地代码）
    code_mapping = {
        "RSA": "ZAF",  # South Africa
        "KSA": "SAU",  # Saudi Arabia
    }
    
    try:
        from services.data_service import get_data_service
        import logging
        logger = logging.getLogger(__name__)
        
        ds = get_data_service()
        matches = await ds.get_matches(group=group)
        
        logger.info(f"📊 查找比赛: {home_code} vs {away_code}, 共{len(matches)}场比赛")
        
        # 查找对应的比赛
        for match in matches:
            # 获取比赛的主客队代码，并映射到本地代码
            match_home = match.get('home') or match.home_code
            match_away = match.get('away') or match.away_code
            
            # 映射到本地代码
            local_home = code_mapping.get(match_home, match_home)
            local_away = code_mapping.get(match_away, match_away)
            
            logger.info(f"  比赛: {match_home}({local_home}) vs {match_away}({local_away}), 状态: {match.get('status')}")
            
            if local_home == home_code and local_away == away_code:
                match_status_raw = match.get('status')
                match_status = "已结束" if match_status_raw == "finished" else "进行中" if match_status_raw == "live" else "待开始"
                home_score = match.get('home_score')
                away_score = match.get('away_score')
                logger.info(f"  ✅ 找到比赛: {home_code} vs {away_code}, 状态: {match_status}, 比分: {home_score}-{away_score}")
                break
    except Exception as e:
        # 获取失败，使用默认值
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"❌ 获取比赛数据失败: {e}", exc_info=True)
    
    # 使用集成模型预测（确保与三模型对比数据一致）
    ensemble = get_ensemble()
    prediction = ensemble.predict_match(home_team, away_team, "GROUP")
    bayesian_pred = prediction.bayesian_pred
    
    # 构建计算过程展示
    elo_diff = home_team.get("elo", 1500) - away_team.get("elo", 1500)
    rank_diff = away_team.get("rank", 50) - home_team.get("rank", 50)
    
    factors = {
        "elo_diff": {
            "raw": format_value(elo_diff),
            "normalized": normalize(elo_diff, 300),
            "meaning": "主队Elo评分" + ("更高" if elo_diff > 0 else "更低" if elo_diff < 0 else "相当")
        },
        "rank_diff": {
            "raw": format_value(rank_diff),
            "normalized": normalize(rank_diff, 50),
            "meaning": "主队排名" + ("更高" if rank_diff > 0 else "更低" if rank_diff < 0 else "相当")
        },
        "form_diff": {"raw": 0, "normalized": 0.0, "meaning": "两队状态相当"},
        "stage_factor": {"raw": 1.0, "normalized": 0.5, "meaning": "小组赛阶段"},
        "home_advantage": {"raw": 0, "normalized": 0.0, "meaning": "中立场（无主场优势）"},
        "continent_factor": {"raw": 0, "normalized": 0.1, "meaning": "非欧洲球队"},
        "h2h": {"raw": 0, "normalized": 0.0, "meaning": "历史交锋记录不足"},
        "wc_experience": {
            "raw": format_value(home_team.get("wc_titles", 0) - away_team.get("wc_titles", 0)),
            "normalized": 0.0,
            "meaning": f"主队{home_team.get('wc_titles', 0)}次夺冠 vs 客队{away_team.get('wc_titles', 0)}次"
        },
        "squad_strength": {
            "raw": format_value(get_squad_strength(home_code) - get_squad_strength(away_code)),
            "normalized": normalize(get_squad_strength(home_code) - get_squad_strength(away_code), 30),
            "meaning": "阵容实力相当"
        },
        "coach_rating": {
            "raw": format_value(calculate_coach_rating(home_code) - calculate_coach_rating(away_code)),
            "normalized": normalize(calculate_coach_rating(home_code) - calculate_coach_rating(away_code), 20),
            "meaning": compare_coaches(home_code, away_code)['analysis']
        },
        "venue_factor": {
            "raw": format_value(get_venue_factor_for_match(group, home_code, away_code)['home_advantage'] * 100),
            "normalized": get_venue_factor_for_match(group, home_code, away_code)['home_advantage'],
            "meaning": get_venue_factor_for_match(group, home_code, away_code)['analysis']
        }
    }
    
    # 比分预测
    score_predictor = ScorePredictor()
    score_pred = score_predictor.predict(home_team, away_team)
    
    return {
        "match_id": f"{group}_{match_index}",
        "group": group,
        "match_index": match_index,
        "home": {
            "code": home_code,
            "name_cn": home_team.get("name_cn", ""),
            "elo": home_team.get("elo", 1500),
            "rank": home_team.get("rank", 50),
            "form": home_team.get("form", "---"),
            "continent": home_team.get("continent", "EU"),
            "wc_titles": home_team.get("wc_titles", 0)
        },
        "away": {
            "code": away_code,
            "name_cn": away_team.get("name_cn", ""),
            "elo": away_team.get("elo", 1500),
            "rank": away_team.get("rank", 50),
            "form": away_team.get("form", "---"),
            "continent": away_team.get("continent", "EU"),
            "wc_titles": away_team.get("wc_titles", 0)
        },
        "factors": factors,
        "weights": WEIGHTS,
        "total_contribution": bayesian_pred.home_win_prob - 0.35 if bayesian_pred.home_win_prob > 0.35 else 0,
        "probabilities": {
            "home_win": bayesian_pred.home_win_prob,
            "draw": bayesian_pred.draw_prob,
            "away_win": bayesian_pred.away_win_prob
        },
        "prediction": "主胜" if bayesian_pred.home_win_prob > bayesian_pred.draw_prob and bayesian_pred.home_win_prob > bayesian_pred.away_win_prob else "客胜" if bayesian_pred.away_win_prob > bayesian_pred.home_win_prob else "平局",
        "confidence": "高" if bayesian_pred.confidence > 0.5 else "中" if bayesian_pred.confidence > 0.3 else "低",
        "status": match_status,
        # 新增：实际比分
        "actual_score": {
            "home_score": home_score,
            "away_score": away_score,
            "result": f"{home_score}-{away_score}" if home_score is not None and away_score is not None else None
        } if home_score is not None else None,
        # 新增：比分预测
        "score_prediction": {
            "expected_goals": score_pred["expected_goals"],
            "top_predictions": score_pred["score_predictions"]
        },
        # 新增：大小球预测
        "over_under": score_pred["over_under"],
        "squad_info": _build_squad_info(home_code, away_code),
        "coach_info": _build_coach_info(home_code, away_code),
        "venue_info": _build_venue_info(group, home_code, away_code, match_index)
    }


@router.get("/teams/{home_code}/{away_code}")
async def get_teams_calculation(home_code: str, away_code: str) -> Dict[str, Any]:
    """
    获取任意两支球队的对决计算过程
    
    Args:
        home_code: 主队代码
        away_code: 客队代码
    """
    return calculate_match_prediction(home_code, away_code, "X", 0)


@router.get("/weights")
async def get_weights_info() -> Dict[str, Any]:
    """
    获取权重配置信息
    """
    return {
        "weights": WEIGHTS,
        "total_weight": sum(WEIGHTS.values()),
        "explanation": {
            "elo_diff": "Elo评分系统，反映球队真实实力",
            "form_diff": "近期比赛状态（最近5场）",
            "rank_diff": "FIFA官方排名",
            "home_advantage": "东道主或主场加成",
            "stage_factor": "赛事阶段重要性",
            "continent_factor": "洲际因素（欧洲球队略占优）",
            "h2h": "历史交锋记录",
            "wc_experience": "世界杯历史经验"
        },
        "training_accuracy": 53.1,
        "training_data": "2018+2022世界杯（128场比赛）"
    }


def _build_squad_info(home_code: str, away_code: str) -> Dict[str, Any]:
    home_squad = get_team_squad(home_code)
    away_squad = get_team_squad(away_code)
    # squad可能返回dict或list，处理兼容
    home_players = list(home_squad.values())[:3] if isinstance(home_squad, dict) else (home_squad[:3] if home_squad else [])
    away_players = list(away_squad.values())[:3] if isinstance(away_squad, dict) else (away_squad[:3] if away_squad else [])
    return {
        "home": {"strength": get_squad_strength(home_code), "key_players": home_players},
        "away": {"strength": get_squad_strength(away_code), "key_players": away_players},
        "comparison": compare_squads(home_code, away_code)
    }

def _build_coach_info(home_code: str, away_code: str) -> Dict[str, Any]:
    return {
        "home": get_coach_info(home_code),
        "away": get_coach_info(away_code),
        "comparison": compare_coaches(home_code, away_code)
    }

def _build_venue_info(group: str, home_code: str, away_code: str, match_index: int = 0) -> Dict[str, Any]:
    venue_data = get_venue_factor_for_match(group, home_code, away_code)
    return {
        "venue": get_match_venue(group, match_index),
        **venue_data
    }
