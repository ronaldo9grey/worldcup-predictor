"""
排行榜系统 - 第九轮迭代
用户积分、准确率排行
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Optional
from datetime import datetime
import sqlite3
import os

router = APIRouter(prefix="/api/leaderboard", tags=["排行榜"])

DB_PATH = "/var/www/worldcup-predictor/backend/data/world_cup.db"


def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/")
async def get_leaderboard(
    sort_by: str = "points",  # points, accuracy, predictions
    limit: int = 50
) -> Dict:
    """
    获取排行榜
    
    sort_by: 
    - points: 积分排行
    - accuracy: 准确率排行
    - predictions: 预测数量排行
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # 检查表是否存在，不存在则创建
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_rankings (
            user_id INTEGER PRIMARY KEY,
            nickname TEXT NOT NULL,
            total_points INTEGER DEFAULT 0,
            total_predictions INTEGER DEFAULT 0,
            correct_predictions INTEGER DEFAULT 0,
            accuracy REAL DEFAULT 0.0,
            last_prediction_time TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # 检查是否有数据，没有则初始化模拟数据
    cursor.execute("SELECT COUNT(*) as count FROM user_rankings")
    if cursor.fetchone()["count"] == 0:
        # 创建模拟排行榜数据
        mock_users = [
            ("足球大师", 850, 45, 32, 71.1),
            ("预测专家", 720, 40, 28, 70.0),
            ("球迷小王", 680, 38, 26, 68.4),
            ("阿根廷铁粉", 650, 35, 25, 71.4),
            ("数据分析师", 600, 42, 29, 69.0),
            ("足球小将", 580, 33, 23, 69.7),
            ("绿茵场", 550, 30, 21, 70.0),
            ("世界杯达人", 520, 36, 25, 69.4),
            ("球迷老张", 500, 28, 19, 67.9),
            ("足球先生", 480, 32, 22, 68.8),
        ]
        
        for i, (nickname, points, total, correct, accuracy) in enumerate(mock_users):
            cursor.execute("""
                INSERT INTO user_rankings 
                (user_id, nickname, total_points, total_predictions, correct_predictions, accuracy)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (i + 1, nickname, points, total, correct, accuracy))
    
    conn.commit()
    
    # 根据排序字段获取排行
    if sort_by == "points":
        order_clause = "total_points DESC"
    elif sort_by == "accuracy":
        order_clause = "accuracy DESC, total_predictions DESC"
    elif sort_by == "predictions":
        order_clause = "total_predictions DESC"
    else:
        order_clause = "total_points DESC"
    
    cursor.execute(f"""
        SELECT 
            user_id,
            nickname,
            total_points,
            total_predictions,
            correct_predictions,
            accuracy,
            last_prediction_time
        FROM user_rankings
        ORDER BY {order_clause}
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    
    leaderboard = []
    for rank, row in enumerate(rows, 1):
        leaderboard.append({
            "rank": rank,
            "user_id": row["user_id"],
            "nickname": row["nickname"],
            "total_points": row["total_points"],
            "total_predictions": row["total_predictions"],
            "correct_predictions": row["correct_predictions"],
            "accuracy": round(row["accuracy"], 1),
            "level": get_user_level(row["total_points"]),
            "level_name": get_user_level_name(row["total_points"]),
            "badge": get_user_badge(row["accuracy"], row["total_predictions"]),
        })
    
    conn.close()
    
    return {
        "sort_by": sort_by,
        "total_users": len(leaderboard),
        "leaderboard": leaderboard,
        "last_updated": datetime.now().isoformat(),
    }


@router.get("/user/{user_id}")
async def get_user_ranking(user_id: int) -> Dict:
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
            accuracy,
            last_prediction_time,
            created_at
        FROM user_rankings
        WHERE user_id = ?
    """, (user_id,))
    
    row = cursor.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="用户未找到")
    
    # 计算排名
    cursor.execute("""
        SELECT COUNT(*) as rank FROM user_rankings 
        WHERE total_points > ?
    """, (row["total_points"],))
    
    rank = cursor.fetchone()["rank"] + 1
    
    # 统计信息
    cursor.execute("""
        SELECT 
            AVG(total_points) as avg_points,
            MAX(total_points) as max_points,
            COUNT(*) as total_users
        FROM user_rankings
    """)
    
    stats = cursor.fetchone()
    
    conn.close()
    
    return {
        "user_id": row["user_id"],
        "nickname": row["nickname"],
        "rank": rank,
        "total_points": row["total_points"],
        "total_predictions": row["total_predictions"],
        "correct_predictions": row["correct_predictions"],
        "accuracy": round(row["accuracy"], 1),
        "level": get_user_level(row["total_points"]),
        "level_name": get_user_level_name(row["total_points"]),
        "badge": get_user_badge(row["accuracy"], row["total_predictions"]),
        "percentile": round((1 - rank / stats["total_users"]) * 100, 1),
        "avg_points": round(stats["avg_points"], 1),
        "max_points": stats["max_points"],
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
            AVG(accuracy) as avg_accuracy,
            MAX(total_points) as max_points,
            AVG(total_points) as avg_points
        FROM user_rankings
    """)
    
    stats = cursor.fetchone()
    
    conn.close()
    
    return {
        "total_users": stats["total_users"],
        "total_predictions": stats["total_predictions"],
        "total_correct_predictions": stats["total_correct"],
        "avg_accuracy": round(stats["avg_accuracy"], 1),
        "max_points": stats["max_points"],
        "avg_points": round(stats["avg_points"], 1),
    }


@router.get("/top-predictions")
async def get_top_predictions_today(limit: int = 10) -> List[Dict]:
    """获取今日热门预测"""
    # 模拟热门预测
    return [
        {
            "match": "阿根廷 vs 巴西",
            "prediction": "阿根廷胜",
            "confidence": "高信心",
            "users_count": 156,
            "odds": 2.15
        },
        {
            "match": "法国 vs 德国",
            "prediction": "法国胜",
            "confidence": "中信心",
            "users_count": 142,
            "odds": 1.85
        },
        {
            "match": "英格兰 vs 西班牙",
            "prediction": "平局",
            "confidence": "低信心",
            "users_count": 98,
            "odds": 3.40
        },
    ]


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
