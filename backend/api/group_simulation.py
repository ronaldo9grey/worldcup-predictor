"""小组出线概率模拟API - 优化版"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List
import random
from data.world_cup_2026 import get_groups as get_groups_dict
from services.ensemble_instance import get_ensemble
import asyncio
from datetime import datetime

router = APIRouter(prefix="/api/groups", tags=["小组模拟"])

# ====== 缓存层 ======
# 比赛预测缓存（避免重复计算）
PREDICTION_CACHE: Dict[str, any] = {}

# 小组出线概率缓存
QUALIFICATION_CACHE: Dict[str, dict] = {}

# 缓存更新时间
CACHE_UPDATED_AT: datetime = None


def get_cached_prediction(home_code: str, away_code: str, ensemble):
    """获取缓存的预测结果，缓存未命中则计算并缓存"""
    key = f"{home_code}-{away_code}"
    
    if key not in PREDICTION_CACHE:
        # 从全局数据中找到球队信息
        groups_dict = get_groups_dict()
        home_team = None
        away_team = None
        
        for group_teams in groups_dict.values():
            for t in group_teams:
                if t["code"] == home_code:
                    home_team = t
                elif t["code"] == away_code:
                    away_team = t
        
        if home_team and away_team:
            pred = ensemble.predict_match(home_team, away_team, "GROUP")
            PREDICTION_CACHE[key] = pred.bayesian_pred
    
    return PREDICTION_CACHE.get(key)


def simulate_group_stage_fast(teams: List[Dict], ensemble) -> Dict[str, int]:
    """优化版：使用缓存的预测结果进行模拟"""
    points = {t["code"]: 0 for t in teams}
    
    pairs = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
    for h_idx, a_idx in pairs:
        home, away = teams[h_idx], teams[a_idx]
        
        # 使用缓存的预测结果
        bayesian = get_cached_prediction(home["code"], away["code"], ensemble)
        if not bayesian:
            continue
        
        # 蒙特卡洛采样
        rand = random.random()
        home_win_prob = bayesian.home_win_prob
        draw_prob = bayesian.draw_prob
        
        if rand < home_win_prob:
            points[home["code"]] += 3
        elif rand < home_win_prob + draw_prob:
            points[home["code"]] += 1
            points[away["code"]] += 1
        else:
            points[away["code"]] += 3
    
    return points


def compute_qualification_probability(group_name: str, simulations: int = 1000) -> dict:
    """计算小组出线概率（内部函数，带缓存）"""
    # 检查缓存
    if group_name in QUALIFICATION_CACHE:
        return QUALIFICATION_CACHE[group_name]
    
    groups_dict = get_groups_dict()
    teams = groups_dict.get(group_name.upper())
    
    if not teams or len(teams) < 4:
        return None
    
    ensemble = get_ensemble()
    
    # 统计每个排名的出现次数
    position_counts = {t["code"]: [0, 0, 0, 0] for t in teams}
    
    # 蒙特卡洛模拟（使用缓存的预测）
    for _ in range(simulations):
        points = simulate_group_stage_fast(teams, ensemble)
        
        # 排序（积分降序，积分相同按FIFA排名）
        sorted_teams = sorted(
            teams,
            key=lambda t: (points[t["code"]], -t.get("rank", 50)),
            reverse=True
        )
        
        # 统计排名
        for i, team in enumerate(sorted_teams):
            position_counts[team["code"]][i] += 1
    
    # 计算概率
    qualification_probs = []
    for team in teams:
        counts = position_counts[team["code"]]
        top2 = (counts[0] + counts[1]) / simulations
        
        qualification_probs.append({
            "code": team["code"],
            "name": team.get("name", ""),
            "name_cn": team.get("name_cn", ""),
            "qualification_prob": round(top2 * 100, 1),
            "position_probs": [round(c / simulations * 100, 1) for c in counts]
        })
    
    # 按出线概率降序
    qualification_probs.sort(key=lambda x: x["qualification_prob"], reverse=True)
    
    result = {
        "group": group_name.upper(),
        "simulations": simulations,
        "qualification_probability": qualification_probs
    }
    
    # 缓存结果
    QUALIFICATION_CACHE[group_name] = result
    
    return result


async def precompute_all_qualifications():
    """启动时预计算所有小组出线概率"""
    global CACHE_UPDATED_AT
    
    print("🚀 开始预计算所有小组出线概率...")
    start_time = datetime.now()
    
    groups = "ABCDEFGHIJKL"
    for group_name in groups:
        try:
            compute_qualification_probability(group_name, simulations=1000)
            print(f"  ✅ {group_name}组完成")
        except Exception as e:
            print(f"  ❌ {group_name}组失败: {e}")
    
    CACHE_UPDATED_AT = datetime.now()
    elapsed = (CACHE_UPDATED_AT - start_time).total_seconds()
    print(f"✨ 预计算完成，耗时 {elapsed:.2f} 秒")


@router.get("/{group_name}/qualification")
async def get_qualification_probability(group_name: str, simulations: int = 1000, force_refresh: bool = False):
    """
    计算小组出线概率（蒙特卡洛模拟，带缓存）
    
    Args:
        group_name: 小组名称（A-L）
        simulations: 模拟次数（默认1000）
        force_refresh: 强制刷新缓存
    """
    group_name = group_name.upper()
    
    # 如果强制刷新或缓存不存在，重新计算
    if force_refresh or group_name not in QUALIFICATION_CACHE:
        result = compute_qualification_probability(group_name, simulations)
        if not result:
            raise HTTPException(status_code=404, detail="小组不存在")
        return result
    
    # 返回缓存结果
    return QUALIFICATION_CACHE[group_name]


@router.post("/cache/refresh")
async def refresh_all_cache():
    """手动刷新所有缓存"""
    global PREDICTION_CACHE, QUALIFICATION_CACHE
    
    PREDICTION_CACHE.clear()
    QUALIFICATION_CACHE.clear()
    
    await precompute_all_qualifications()
    
    return {
        "success": True,
        "message": "缓存已刷新",
        "cached_groups": list(QUALIFICATION_CACHE.keys()),
        "cached_predictions": len(PREDICTION_CACHE)
    }


@router.get("/cache/status")
async def get_cache_status():
    """查看缓存状态"""
    return {
        "prediction_cache_size": len(PREDICTION_CACHE),
        "qualification_cache": list(QUALIFICATION_CACHE.keys()),
        "last_updated": CACHE_UPDATED_AT.isoformat() if CACHE_UPDATED_AT else None
    }
