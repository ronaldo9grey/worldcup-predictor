#!/usr/bin/env python3
"""
修正积分榜数据
WorldCup26.ir API的groups端点存在主客队数据颠倒的bug
需要基于比赛结果重新计算积分榜
"""
import asyncio
import aiohttp
import json
from typing import Dict, List
from collections import defaultdict

BASE_URL = "https://worldcup26.ir/get"


async def fetch_data(session: aiohttp.ClientSession, endpoint: str) -> Dict:
    """获取API数据"""
    url = f"{BASE_URL}/{endpoint}"
    async with session.get(url) as response:
        return await response.json()


async def get_teams_mapping(session: aiohttp.ClientSession) -> Dict[str, str]:
    """获取team_id到team_code的映射"""
    data = await fetch_data(session, "teams")
    return {t["id"]: t["fifa_code"] for t in data.get("teams", [])}


async def get_groups_teams(session: aiohttp.ClientSession) -> Dict[str, List[str]]:
    """获取每个小组的球队"""
    data = await fetch_data(session, "teams")
    groups = defaultdict(list)
    for t in data.get("teams", []):
        group = t.get("groups")
        if group:
            groups[group].append(t["fifa_code"])
    return dict(groups)


async def calculate_standings(session: aiohttp.ClientSession) -> Dict[str, List[Dict]]:
    """基于比赛结果计算积分榜"""
    # 获取比赛数据
    games_data = await fetch_data(session, "games")
    teams_mapping = await get_teams_mapping(session)
    
    # 初始化积分榜
    standings = defaultdict(lambda: {
        "points": 0,
        "w": 0,
        "d": 0,
        "l": 0,
        "gf": 0,
        "ga": 0,
        "gd": 0
    })
    
    # 统计比赛结果
    for game in games_data.get("games", []):
        if game.get("finished") != "TRUE":
            continue
        
        # 获取team_code
        home_id = game.get("home_team_id")
        away_id = game.get("away_team_id")
        home_code = teams_mapping.get(home_id, home_id)
        away_code = teams_mapping.get(away_id, away_id)
        
        # 解析比分
        try:
            home_score = int(game.get("home_score", 0))
            away_score = int(game.get("away_score", 0))
        except (ValueError, TypeError):
            continue
        
        # 更新积分榜
        standings[home_code]["gf"] += home_score
        standings[home_code]["ga"] += away_score
        standings[away_code]["gf"] += away_score
        standings[away_code]["ga"] += home_score  # 客队失球 = 主队进球
        
        if home_score > away_score:
            # 主胜
            standings[home_code]["points"] += 3
            standings[home_code]["w"] += 1
            standings[away_code]["l"] += 1
        elif home_score < away_score:
            # 客胜
            standings[away_code]["points"] += 3
            standings[away_code]["w"] += 1
            standings[home_code]["l"] += 1
        else:
            # 平局
            standings[home_code]["points"] += 1
            standings[away_code]["points"] += 1
            standings[home_code]["d"] += 1
            standings[away_code]["d"] += 1
        
        # 计算净胜球
        standings[home_code]["gd"] = standings[home_code]["gf"] - standings[home_code]["ga"]
        standings[away_code]["gd"] = standings[away_code]["gf"] - standings[away_code]["ga"]
    
    return dict(standings)


async def main():
    """主函数"""
    async with aiohttp.ClientSession() as session:
        # 计算正确的积分榜
        correct_standings = await calculate_standings(session)
        
        # 获取小组信息
        groups_teams = await get_groups_teams(session)
        
        # 输出结果
        print("=" * 60)
        print("修正后的积分榜数据")
        print("=" * 60)
        
        for group, teams in sorted(groups_teams.items()):
            print(f"\n{group}组:")
            
            # 构建小组积分榜
            group_standings = []
            for team_code in teams:
                stats = correct_standings.get(team_code, {})
                group_standings.append({
                    "code": team_code,
                    "points": stats.get("points", 0),
                    "w": stats.get("w", 0),
                    "d": stats.get("d", 0),
                    "l": stats.get("l", 0),
                    "gf": stats.get("gf", 0),
                    "ga": stats.get("ga", 0),
                    "gd": stats.get("gd", 0)
                })
            
            # 按积分排序（积分相同按净胜球、进球数排序）
            group_standings.sort(key=lambda x: (
                -x["points"], 
                -x["gd"], 
                -x["gf"]
            ))
            
            # 显示积分榜
            for i, team in enumerate(group_standings, 1):
                print(f"  {i}. {team['code']:3s} | "
                      f"{team['points']}分 | "
                      f"{team['w']}胜{team['d']}平{team['l']}负 | "
                      f"进{team['gf']}失{team['ga']} | "
                      f"净胜{team['gd']:+d}")
        
        print("\n" + "=" * 60)
        
        # 保存到JSON文件
        output = {
            "standings": correct_standings,
            "groups": groups_teams
        }
        
        with open("/var/www/worldcup-predictor/backend/data/correct_standings.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 已保存到 correct_standings.json")


if __name__ == "__main__":
    asyncio.run(main())
