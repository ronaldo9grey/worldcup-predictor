"""用户数据访问层"""
import sqlite3
import json
import uuid
from typing import Optional, List, Dict, Any
from datetime import datetime
from contextlib import contextmanager


class UserRepository:
    """用户数据仓库"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_tables()
    
    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _init_tables(self):
        """初始化用户相关表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    nickname TEXT NOT NULL,
                    device_key TEXT,
                    created_at TEXT NOT NULL,
                    last_login TEXT,
                    total_points INTEGER DEFAULT 0,
                    correct_predictions INTEGER DEFAULT 0,
                    total_predictions INTEGER DEFAULT 0
                )
            """)
            
            # 预测记录表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    match_id TEXT NOT NULL,
                    group_name TEXT NOT NULL,
                    match_idx INTEGER NOT NULL,
                    home_code TEXT NOT NULL,
                    away_code TEXT NOT NULL,
                    prediction TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    predicted_at TEXT NOT NULL,
                    actual_result TEXT,
                    is_correct INTEGER,
                    points_earned INTEGER DEFAULT 0,
                    verified_at TEXT,
                    UNIQUE(user_id, match_id)
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_predictions_match ON predictions(match_id)")
            
            conn.commit()
    
    # ========== 用户操作 ==========
    
    def create_user(self, nickname: str, device_key: str = None) -> Dict[str, Any]:
        """创建用户（如果昵称已存在则验证device_key）"""
        # 昵称黑名单验证
        forbidden_nicknames = ["王超", "万哥", "wange", "王 超", "万 哥"]
        if nickname in forbidden_nicknames:
            return {
                "error": "该昵称已被保留，请换一个昵称",
                "nickname_taken": True,
                "forbidden": True
            }
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE nickname = ?", (nickname,))
            existing = cursor.fetchone()
            
            if existing:
                # 昵称已存在，验证device_key
                user_id = existing["user_id"]
                stored_device_key = existing["device_key"] if "device_key" in existing.keys() else None
                
                # 如果没有存储device_key，则更新
                if not stored_device_key and device_key:
                    cursor.execute("UPDATE users SET device_key = ? WHERE user_id = ?", (device_key, user_id))
                    conn.commit()
                    self.update_login(user_id)
                    return {
                        "user_id": user_id,
                        "nickname": nickname,
                        "created_at": existing["created_at"],
                        "total_points": existing["total_points"],
                        "is_existing": True
                    }
                
                # 验证device_key
                if stored_device_key and device_key and stored_device_key != device_key:
                    # device_key不匹配，拒绝登录
                    return {
                        "error": "该昵称已被其他设备使用，请换一个昵称",
                        "nickname_taken": True
                    }
                
                # device_key匹配或未设置，允许登录
                self.update_login(user_id)
                return {
                    "user_id": user_id,
                    "nickname": nickname,
                    "created_at": existing["created_at"],
                    "total_points": existing["total_points"],
                    "is_existing": True
                }
        
        # 创建新用户
        user_id = f"u_{uuid.uuid4().hex[:12]}"
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (user_id, nickname, device_key, created_at, last_login)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, nickname, device_key, now, now))
            conn.commit()
        
        return {
            "user_id": user_id,
            "nickname": nickname,
            "created_at": now,
            "total_points": 0,
            "is_existing": False
        }
    
    def get_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """获取用户"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_login(self, user_id: str) -> None:
        """更新登录时间"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users SET last_login = ? WHERE user_id = ?
            """, (datetime.now().isoformat(), user_id))
            conn.commit()
    
    def get_or_create_user(self, user_id: str, nickname: str = None) -> Dict[str, Any]:
        """获取或创建用户"""
        user = self.get_user(user_id)
        if user:
            self.update_login(user_id)
            return user
        
        # 创建新用户
        if not nickname:
            nickname = f"用户{user_id[-6:]}"
        return self.create_user(nickname)
    
    # ========== 预测操作 ==========
    
    def save_prediction(self, user_id: str, match_id: str, group_name: str, 
                        match_idx: int, home_code: str, away_code: str,
                        prediction: str, confidence: str) -> Dict[str, Any]:
        """保存预测"""
        pred_id = f"{user_id}_{match_id}"
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查是否已预测
            cursor.execute("""
                SELECT * FROM predictions WHERE user_id = ? AND match_id = ?
            """, (user_id, match_id))
            existing = cursor.fetchone()
            
            if existing:
                # 更新预测
                cursor.execute("""
                    UPDATE predictions SET
                        prediction = ?, confidence = ?, predicted_at = ?
                    WHERE id = ?
                """, (prediction, confidence, now, existing["id"]))
                pred_id = existing["id"]
            else:
                # 新预测
                cursor.execute("""
                    INSERT INTO predictions 
                    (id, user_id, match_id, group_name, match_idx, home_code, away_code, 
                     prediction, confidence, predicted_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (pred_id, user_id, match_id, group_name, match_idx, 
                      home_code, away_code, prediction, confidence, now))
                
                # 更新用户预测总数
                cursor.execute("""
                    UPDATE users SET total_predictions = total_predictions + 1
                    WHERE user_id = ?
                """, (user_id,))
            
            conn.commit()
        
        return {
            "id": pred_id,
            "user_id": user_id,
            "match_id": match_id,
            "prediction": prediction,
            "confidence": confidence,
            "predicted_at": now
        }
    
    def get_user_predictions(self, user_id: str) -> List[Dict[str, Any]]:
        """获取用户所有预测"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM predictions 
                WHERE user_id = ? 
                ORDER BY predicted_at DESC
            """, (user_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    def get_match_predictions(self, match_id: str) -> List[Dict[str, Any]]:
        """获取某场比赛的所有预测"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT p.*, u.nickname FROM predictions p
                JOIN users u ON p.user_id = u.user_id
                WHERE p.match_id = ?
                ORDER BY p.predicted_at DESC
            """, (match_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== 验证操作 ==========
    
    def verify_prediction(self, pred_id: str, actual_result: str) -> Dict[str, Any]:
        """验证预测结果"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取预测
            cursor.execute("SELECT * FROM predictions WHERE id = ?", (pred_id,))
            pred = cursor.fetchone()
            if not pred:
                return None
            
            # 判断是否正确
            is_correct = (pred["prediction"] == actual_result)
            
            # 计算积分
            points = 0
            if is_correct:
                base_points = {"HIGH": 10, "MEDIUM": 15, "LOW": 20}
                points = base_points.get(pred["confidence"], 10)
            
            # 更新预测
            now = datetime.now().isoformat()
            cursor.execute("""
                UPDATE predictions SET
                    actual_result = ?, is_correct = ?, points_earned = ?, verified_at = ?
                WHERE id = ?
            """, (actual_result, int(is_correct), points, now, pred_id))
            
            # 更新用户积分
            if is_correct:
                cursor.execute("""
                    UPDATE users SET
                        total_points = total_points + ?,
                        correct_predictions = correct_predictions + 1
                    WHERE user_id = ?
                """, (points, pred["user_id"]))
            
            conn.commit()
        
        return {
            "pred_id": pred_id,
            "is_correct": is_correct,
            "points_earned": points
        }
    
    def verify_match(self, match_id: str, actual_result: str) -> List[Dict[str, Any]]:
        """批量验证某场比赛的所有预测"""
        predictions = self.get_match_predictions(match_id)
        results = []
        
        for pred in predictions:
            result = self.verify_prediction(pred["id"], actual_result)
            if result:
                results.append(result)
        
        return results
    
    # ========== 排行榜 ==========
    
    def get_leaderboard(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取排行榜"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, nickname, total_points, 
                       correct_predictions, total_predictions,
                       CASE WHEN total_predictions > 0 
                            THEN ROUND(correct_predictions * 100.0 / total_predictions, 1)
                            ELSE 0 END as accuracy
                FROM users
                WHERE total_predictions > 0
                ORDER BY total_points DESC, accuracy DESC
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            leaderboard = []
            for i, row in enumerate(rows, 1):
                leaderboard.append({
                    "rank": i,
                    "user_id": row["user_id"],
                    "nickname": row["nickname"],
                    "total_points": row["total_points"],
                    "correct_predictions": row["correct_predictions"],
                    "total_predictions": row["total_predictions"],
                    "accuracy": row["accuracy"]
                })
            
            return leaderboard
    
    def get_user_rank(self, user_id: str) -> Optional[int]:
        """获取用户排名"""
        leaderboard = self.get_leaderboard(limit=1000)
        for entry in leaderboard:
            if entry["user_id"] == user_id:
                return entry["rank"]
        return None
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """获取所有用户列表（昵称选择器用）"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, nickname, created_at, last_login, 
                       total_points, total_predictions
                FROM users
                ORDER BY last_login DESC, created_at DESC
            """)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def delete_user(self, user_id: str) -> bool:
        """删除用户及其所有预测记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查用户是否存在
            cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
            if not cursor.fetchone():
                return False
            
            # 删除用户的所有预测记录
            cursor.execute("DELETE FROM predictions WHERE user_id = ?", (user_id,))
            
            # 删除用户
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            
            conn.commit()
            return True
