"""小组出线概率模拟API"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List
import random
from data.world_cup_2026 import get_groups as get_groups_dict
from services.ensemble_instance import get_ensemble

router = APIRouter(prefix="/api/groups", tags=["小组模拟"])

def simulate_group_stage(teams: List[Dict], ensemble) -> Dict[str, int]:
    """模拟一次小组赛，返回各队积分"""
    points = {t["code"]: 0 for t in teams}
    
    pairs = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
    for h_idx, a_idx in pairs:
        home, away = teams[h_idx], teams[a_idx]
        pred = ensemble.predict_match(home, away, "GROUP")
        bayesian = pred.bayesian_pred
        
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

@router.get("/{group_name}/qualification")
async def get_qualification_probability(group_name: str, simulations: int = 1000):
    """
    计算小组出线概率（蒙特卡洛模拟）
    
    Args:
        group_name: 小组名称（A-L）
        simulations: 模拟次数（默认1000）
    """
    groups_dict = get_groups_dict()
    teams = groups_dict.get(group_name.upper())
    
    if not teams or len(teams) < 4:
        raise HTTPException(status_code=404, detail="小组不存在")
    
    ensemble = get_ensemble()
    
    # 统计每个排名的出现次数
    position_counts = {t["code"]: [0, 0, 0, 0] for t in teams}  # [第1, 第2, 第3, 第4]
    
    # 蒙特卡洛模拟
    for _ in range(simulations):
        points = simulate_group_stage(teams, ensemble)
        
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
        top2 = (counts[0] + counts[1]) / simulations  # 出线概率（前2名）
        
        qualification_probs.append({
            "code": team["code"],
            "name": team.get("name", ""),
            "name_cn": team.get("name_cn", ""),
            "qualification_prob": round(top2 * 100, 1),
            "position_probs": [round(c / simulations * 100, 1) for c in counts]
        })
    
    # 按出线概率降序
    qualification_probs.sort(key=lambda x: x["qualification_prob"], reverse=True)
    
    return {
        "group": group_name.upper(),
        "simulations": simulations,
        "qualification_probability": qualification_probs
    }
