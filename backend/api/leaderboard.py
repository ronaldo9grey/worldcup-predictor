"""
排行榜系统 - 统一数据源
使用真实用户数据
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from datetime import datetime
import sqlite3

router = APIRouter(prefix="/api/leaderboard", tags=["排行榜"])

DB_PATH = "/var/www/worldcup-predictor/backend/data/world_cup.db"


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/")
async def get_leaderboard(
    sort_by: str = Query("points", description="排序方式: points, accuracy, predictions"),
    limit: int = Query(50, ge=1, le=100)
) -> Dict:
    """
    获取排行榜（使用真实用户数据）
    
    sort_by: 
    - points: 积分排行
    - accuracy: 准确率排行
    - predictions: 预测数量排行
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查 users 表是否有数据
    cursor.execute("SELECT COUNT(*) as count FROM users")
    user_count = cursor.fetchone()["count"]
    
    if user_count == 0:
        # 没有用户数据，返回空列表
        conn.close()
        return {
            "sort_by": sort_by,
            "total_users": 0,
            "leaderboard": [],
            "last_updated": datetime.now().isoformat(),
        }
    
    # 根据排序字段获取排行
    if sort_by == "points":
        order_clause = "total_points DESC, total_predictions DESC"
    elif sort_by == "accuracy":
        order_clause = "CASE WHEN total_predictions > 0 THEN CAST(correct_predictions AS REAL) / total_predictions ELSE 0 END DESC, total_predictions DESC"
    elif sort_by == "predictions":
        order_clause = "total_predictions DESC, total_points DESC"
    else:
        order_clause = "total_points DESC"
    
    cursor.execute(f"""
        SELECT 
            user_id,
            nickname,
            total_points,
            total_predictions,
            correct_predictions,
            CASE WHEN total_predictions > 0 THEN ROUND(CAST(correct_predictions AS REAL) / total_predictions * 100, 1) ELSE 0 END as accuracy,
            created_at
        FROM users
        ORDER BY {order_clause}
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    
    leaderboard = []
    for rank, row in enumerate(rows, 1):
        accuracy = row["accuracy"] if row["total_predictions"] > 0 else 0
        leaderboard.append({
            "rank": rank,
            "user_id": row["user_id"],
            "nickname": row["nickname"],
            "total_points": row["total_points"] or 0,
            "total_predictions": row["total_predictions"] or 0,
            "correct_predictions": row["correct_predictions"] or 0,
            "accuracy": accuracy,
            "level": get_user_level(row["total_points"] or 0),
            "level_name": get_user_level_name(row["total_points"] or 0),
            "badge": get_user_badge(accuracy, row["total_predictions"] or 0),
        })
    
    conn.close()
    
    return {
        "sort_by": sort_by,
        "total_users": user_count,
        "leaderboard": leaderboard,
        "last_updated": datetime.now().isoformat(),
    }


@router.get("/user/{user_id}")
async def get_user_ranking(user_id: str) -> Dict:
    """获取用户排名详情"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            user_id,
            nickname,
            total_points,
            total_predictions,
            correct_predictions,
            created_at
        FROM users
        WHERE user_id = ?
    """, (user_id,))
    
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    # 计算排名
    cursor.execute("""
        SELECT COUNT(*) as rank FROM users 
        WHERE total_points > ?
    """, (row["total_points"] or 0,))
    
    rank = cursor.fetchone()["rank"] + 1
    
    # 统计信息
    cursor.execute("""
        SELECT 
            AVG(total_points) as avg_points,
            MAX(total_points) as max_points,
            COUNT(*) as total_users
        FROM users
    """)
    
    stats = cursor.fetchone()
    
    accuracy = (row["correct_predictions"] / row["total_predictions"] * 100) if row["total_predictions"] > 0 else 0
    
    conn.close()
    
    return {
        "user_id": row["user_id"],
        "nickname": row["nickname"],
        "rank": rank,
        "total_points": row["total_points"] or 0,
        "total_predictions": row["total_predictions"] or 0,
        "correct_predictions": row["correct_predictions"] or 0,
        "accuracy": round(accuracy, 1),
        "level": get_user_level(row["total_points"] or 0),
        "level_name": get_user_level_name(row["total_points"] or 0),
        "badge": get_user_badge(accuracy, row["total_predictions"] or 0),
        "percentile": round((1 - rank / stats["total_users"]) * 100, 1) if stats["total_users"] > 0 else 0,
        "avg_points": round(stats["avg_points"] or 0, 1),
        "max_points": stats["max_points"] or 0,
    }


@router.get("/stats")
async def get_leaderboard_stats() -> Dict:
    """获取排行榜统计信息"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_users,
            SUM(total_predictions) as total_predictions,
            SUM(correct_predictions) as total_correct,
            AVG(CASE WHEN total_predictions > 0 THEN CAST(correct_predictions AS REAL) / total_predictions ELSE NULL END) as avg_accuracy,
            MAX(total_points) as max_points,
            AVG(total_points) as avg_points
        FROM users
    """)
    
    stats = cursor.fetchone()
    
    conn.close()
    
    return {
        "total_users": stats["total_users"] or 0,
        "total_predictions": stats["total_predictions"] or 0,
        "total_correct_predictions": stats["total_correct"] or 0,
        "avg_accuracy": round(stats["avg_accuracy"] * 100, 1) if stats["avg_accuracy"] else 0,
        "max_points": stats["max_points"] or 0,
        "avg_points": round(stats["avg_points"], 1) if stats["avg_points"] else 0,
    }


@router.get("/top-predictions")
async def get_top_predictions_today(limit: int = 10) -> List[Dict]:
    """获取今日热门预测（基于真实用户数据）"""
    from data.world_cup_2026 import get_team_lookup
    
    conn = get_db()
    cursor = conn.cursor()
    
    # 获取所有预测记录
    cursor.execute("""
        SELECT 
            p.group_name,
            p.match_idx,
            p.home_code,
            p.away_code,
            p.prediction,
            p.confidence,
            COUNT(*) as users_count
        FROM predictions p
        GROUP BY p.home_code, p.away_code, p.prediction
        ORDER BY p.home_code, p.away_code, users_count DESC
    """)
    
    rows = cursor.fetchall()
    
    # 获取球队信息
    team_lookup = get_team_lookup()
    
    # 按比赛分组，每组只保留预测最多的结果
    match_predictions = {}
    for row in rows:
        match_key = (row["home_code"], row["away_code"])
        
        # 如果该比赛还没有记录，或者当前记录的预测人数更多，则更新
        if match_key not in match_predictions or row["users_count"] > match_predictions[match_key]["users_count"]:
            match_predictions[match_key] = dict(row)
    
    # 转换为列表并按预测人数排序
    hot_list = list(match_predictions.values())
    hot_list.sort(key=lambda x: x["users_count"], reverse=True)
    hot_list = hot_list[:limit]
    
    # 统计每场比赛的信心程度分布
    for item in hot_list:
        cursor.execute("""
            SELECT 
                SUM(CASE WHEN confidence = 'HIGH' THEN 1 ELSE 0 END) as high_count,
                SUM(CASE WHEN confidence = 'MEDIUM' THEN 1 ELSE 0 END) as medium_count,
                SUM(CASE WHEN confidence = 'LOW' THEN 1 ELSE 0 END) as low_count
            FROM predictions
            WHERE home_code = ? AND away_code = ? AND prediction = ?
        """, (item["home_code"], item["away_code"], item["prediction"]))
        
        conf_stats = cursor.fetchone()
        item["high_count"] = conf_stats["high_count"] or 0
        item["medium_count"] = conf_stats["medium_count"] or 0
        item["low_count"] = conf_stats["low_count"] or 0
    
    hot_predictions = []
    for row in hot_list:
        home_team = team_lookup.get(row["home_code"], {})
        away_team = team_lookup.get(row["away_code"], {})
        
        # 翻译预测结果
        pred_map = {"HOME_WIN": "主胜", "DRAW": "平局", "AWAY_WIN": "客胜"}
        prediction_text = pred_map.get(row["prediction"], row["prediction"])
        
        # 判断主流信心程度
        if row["high_count"] >= row["medium_count"] and row["high_count"] > 0:
            confidence_text = "高信心"
        elif row["medium_count"] > 0:
            confidence_text = "中信心"
        else:
            confidence_text = "低信心"
        
        hot_predictions.append({
            "match": f"{home_team.get('name_cn', row['home_code'])} vs {away_team.get('name_cn', row['away_code'])}",
            "prediction": prediction_text,
            "confidence": confidence_text,
            "users_count": row["users_count"],
            "group": row["group_name"],
            "match_idx": row["match_idx"],
            "home_code": row["home_code"],
            "away_code": row["away_code"],
        })
    
    conn.close()
    
    # 如果没有预测数据，返回提示
    if not hot_predictions:
        hot_predictions = [
            {
                "match": "暂无热门预测",
                "prediction": "快来参与预测吧",
                "confidence": "-",
                "users_count": 0,
            }
        ]
    
    return hot_predictions


def get_user_level(points: int) -> int:
    """根据积分计算用户等级"""
    if points >= 1000:
        return 10
    elif points >= 800:
        return 9
    elif points >= 650:
        return 8
    elif points >= 500:
        return 7
    elif points >= 400:
        return 6
    elif points >= 300:
        return 5
    elif points >= 200:
        return 4
    elif points >= 100:
        return 3
    elif points >= 50:
        return 2
    else:
        return 1


def get_user_level_name(points: int) -> str:
    """获取等级名称"""
    level = get_user_level(points)
    names = {
        1: "新手球童",
        2: "替补球员",
        3: "首发球员",
        4: "主力球员",
        5: "明星球员",
        6: "超级巨星",
        7: "传奇球星",
        8: "球王",
        9: "预测大师",
        10: "神预测",
    }
    return names.get(level, "新手")


def get_user_badge(accuracy: float, predictions: int) -> str:
    """获取用户徽章"""
    if accuracy >= 80 and predictions >= 30:
        return "🏆 黄金徽章"
    elif accuracy >= 70 and predictions >= 20:
        return "🥈 白银徽章"
    elif accuracy >= 60 and predictions >= 10:
        return "🥉 青铜徽章"
    elif accuracy >= 50:
        return "⭐ 新星徽章"
    else:
        return ""
