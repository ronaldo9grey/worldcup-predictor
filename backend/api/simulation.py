"""锦标赛模拟API路由"""
from fastapi import APIRouter, Query
from typing import Dict, Any

from services.strict_simulation import StrictSimulationEngine
from data.world_cup_2026 import GROUPS, get_team_lookup

router = APIRouter(prefix="/worldcup/api", tags=["模拟"])


@router.get("/simulate")
async def simulate_tournament(
    mode: str = Query("strict", description="strict或prob"),
    deterministic: bool = Query(True, description="是否确定性模拟")
) -> Dict[str, Any]:
    """一键模拟整个锦标赛"""
    sim_engine = StrictSimulationEngine(GROUPS, get_team_lookup())
    return sim_engine.simulate_tournament(deterministic=(mode == "strict"))


@router.get("/simulate/groups")
async def simulate_groups_only() -> Dict[str, Any]:
    """仅模拟小组赛阶段"""
    sim_engine = StrictSimulationEngine(GROUPS, get_team_lookup())
    return sim_engine.simulate_groups()


@router.get("/simulate/knockout")
async def simulate_knockout_only() -> Dict[str, Any]:
    """仅模拟淘汰赛阶段（使用默认小组结果）"""
    sim_engine = StrictSimulationEngine(GROUPS, get_team_lookup())
    return sim_engine.simulate_knockout()


@router.get("/simulate/monte-carlo")
async def monte_carlo_simulation(
    iterations: int = Query(1000, ge=100, le=10000, description="模拟次数")
) -> Dict[str, Any]:
    """
    蒙特卡洛模拟 - 返回每支球队夺冠概率
    """
    all_teams = get_team_lookup()
    team_stats = {code: {
        "champion": 0,
        "final": 0,
        "semifinal": 0,
        "quarterfinal": 0,
        "round16": 0,
    } for code in all_teams}
    
    for _ in range(iterations):
        sim_engine = StrictSimulationEngine(GROUPS, get_team_lookup())
        result = sim_engine.simulate_tournament(deterministic=False)
        
        champion = result.get("champion", "")
        runner_up = result.get("runner_up", "")
        
        if champion in team_stats:
            team_stats[champion]["champion"] += 1
        if runner_up in team_stats:
            team_stats[runner_up]["final"] += 1
        
        # 从淘汰赛统计进入各阶段
        knockout = result.get("knockout", {})
        for round_name, matches in knockout.items():
            for m in matches:
                winner = m.get("winner", "")
                loser = m.get("loser", "")
                
                if round_name == "SF" and loser in team_stats:
                    team_stats[loser]["semifinal"] += 1
                elif round_name == "QF" and loser in team_stats:
                    team_stats[loser]["quarterfinal"] += 1
                elif round_name == "R16" and loser in team_stats:
                    team_stats[loser]["round16"] += 1
    
    # 转换为概率
    result_list = []
    for code, stats in team_stats.items():
        team_info = all_teams.get(code, {})
        result_list.append({
            "code": code,
            "name": team_info.get("name", code),
            "name_cn": team_info.get("name_cn", code),
            "rank": team_info.get("rank", 0),
            "champion_prob": round(stats["champion"] / iterations * 100, 1),
            "final_prob": round(stats["final"] / iterations * 100, 1),
            "semifinal_prob": round(stats["semifinal"] / iterations * 100, 1),
            "quarterfinal_prob": round(stats["quarterfinal"] / iterations * 100, 1),
        })
    
    # 按夺冠概率排序
    result_list.sort(key=lambda x: -x["champion_prob"])
    
    return {
        "iterations": iterations,
        "rankings": result_list
    }
