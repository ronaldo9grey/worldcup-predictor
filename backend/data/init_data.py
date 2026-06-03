"""
世界杯预测系统 V3 - 数据初始化模块

负责将静态数据写入数据库，支持增量更新
"""
from typing import Dict, Any, List
from data.world_cup_2026 import GROUPS
from providers.h2h_provider import H2HProvider
from providers.team_value_provider import TeamValueProvider
from providers.wc_history_provider import WCHistoryProvider
from providers.form_provider import FormProvider


def init_database(db) -> None:
    """初始化数据库 - 写入所有静态数据"""
    print("📦 初始化数据库...")
    
    # 1. 写入球队基础数据
    teams_count = _seed_teams(db)
    print(f"  ✅ 写入 {teams_count} 支球队数据")
    
    # 2. 写入历史交锋数据
    h2h_count = _seed_h2h_data(db)
    print(f"  ✅ 写入 {h2h_count} 条历史交锋记录")
    
    # 3. 写入球队身价数据
    value_count = _seed_team_values(db)
    print(f"  ✅ 写入 {value_count} 条身价数据")
    
    # 4. 写入世界杯历史数据
    history_count = _seed_wc_history(db)
    print(f"  ✅ 写入 {history_count} 条世界杯历史数据")
    
    print("🎉 数据初始化完成！")


def _seed_teams(db) -> int:
    """写入球队基础数据"""
    count = 0
    for group_name, teams in GROUPS.items():
        for team in teams:
            team_data = dict(team)
            team_data["team_value"] = TeamValueProvider.TEAM_VALUES.get(
                team["code"], TeamValueProvider.TEAM_VALUES["_default"]
            )
            team_data["world_cup_experience"] = WCHistoryProvider.WC_HISTORY.get(
                team["code"], WCHistoryProvider.WC_HISTORY["_default"]
            )["appearances"]
            db.upsert_team(team_data)
            count += 1
    return count


def _seed_h2h_data(db) -> int:
    """写入历史交锋数据"""
    provider = H2HProvider(db)
    provider.seed_historical_data()
    
    # 查询已写入的记录数
    import sqlite3
    conn = sqlite3.connect(db.db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM head_to_head")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def _seed_team_values(db) -> int:
    """写入球队身价数据（合并到teams表）"""
    count = 0
    for code, value in TeamValueProvider.TEAM_VALUES.items():
        if code == "_default":
            continue
        team = db.get_team(code)
        if team:
            team_data = dict(team)
            team_data["team_value"] = value
            db.upsert_team(team_data)
            count += 1
    return count


def _seed_wc_history(db) -> int:
    """写入世界杯历史数据"""
    count = 0
    for code, history in WCHistoryProvider.WC_HISTORY.items():
        if code == "_default":
            continue
        db.upsert_wc_history(code, history)
        count += 1
    return count


def update_elo_ratings(db, ratings: Dict[str, int]) -> int:
    """
    更新Elo评分
    
    Args:
        db: 数据库实例
        ratings: {team_code: new_elo} 字典
    
    Returns:
        更新的球队数量
    """
    count = 0
    for code, new_elo in ratings.items():
        team = db.get_team(code)
        if team:
            team_data = dict(team)
            team_data["elo"] = new_elo
            db.upsert_team(team_data)
            count += 1
    return count


def update_team_form(db, form_updates: Dict[str, str]) -> int:
    """
    更新球队状态
    
    Args:
        db: 数据库实例
        form_updates: {team_code: "WDWWL"} 字典
    
    Returns:
        更新的球队数量
    """
    count = 0
    for code, new_form in form_updates.items():
        team = db.get_team(code)
        if team:
            team_data = dict(team)
            team_data["form"] = new_form
            db.upsert_team(team_data)
            count += 1
    return count
