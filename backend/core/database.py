"""数据库连接管理 - 高内聚、可替换实现"""
import sqlite3
import json
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from pathlib import Path


class Database:
    """SQLite 数据库封装，支持依赖注入"""
    
    def __init__(self, db_path: str = "world_cup.db"):
        self.db_path = db_path
        self._init_schema()
    
    def _init_schema(self):
        """初始化数据库表结构"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 球队表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS teams (
                    code TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    name_cn TEXT,
                    rank INTEGER,
                    elo INTEGER,
                    continent TEXT,
                    form TEXT,
                    team_value REAL,
                    world_cup_experience INTEGER DEFAULT 0,
                    last_updated TEXT
                )
            """)
            
            # 历史交锋表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS head_to_head (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    home_code TEXT NOT NULL,
                    away_code TEXT NOT NULL,
                    home_score INTEGER,
                    away_score INTEGER,
                    match_date TEXT,
                    competition TEXT,
                    UNIQUE(home_code, away_code, match_date, competition)
                )
            """)
            
            # 世界杯历史表现
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS world_cup_history (
                    team_code TEXT PRIMARY KEY,
                    appearances INTEGER DEFAULT 0,
                    best_result TEXT,
                    titles INTEGER DEFAULT 0,
                    finals INTEGER DEFAULT 0,
                    semifinals INTEGER DEFAULT 0,
                    last_updated TEXT
                )
            """)
            
            # 预测缓存表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prediction_cache (
                    match_key TEXT PRIMARY KEY,
                    prediction_json TEXT,
                    created_at TEXT,
                    expires_at TEXT
                )
            """)
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """获取数据库连接的上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    # ========== 球队数据 ==========
    
    def upsert_team(self, team_data: Dict[str, Any]) -> None:
        """插入或更新球队数据"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO teams (code, name, name_cn, rank, elo, continent, form, team_value, world_cup_experience, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(code) DO UPDATE SET
                    name = excluded.name,
                    name_cn = excluded.name_cn,
                    rank = excluded.rank,
                    elo = excluded.elo,
                    form = excluded.form,
                    team_value = excluded.team_value,
                    last_updated = datetime('now')
            """, (
                team_data["code"],
                team_data["name"],
                team_data.get("name_cn", ""),
                team_data.get("rank", 50),
                team_data.get("elo", 1500),
                team_data.get("continent", "EU"),
                team_data.get("form", "WDWDW"),
                team_data.get("team_value", 0.0),
                team_data.get("world_cup_experience", 0)
            ))
            conn.commit()
    
    def get_team(self, code: str) -> Optional[Dict[str, Any]]:
        """获取单个球队数据"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teams WHERE code = ?", (code,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_teams(self) -> List[Dict[str, Any]]:
        """获取所有球队数据"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM teams ORDER BY rank")
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== 历史交锋数据 ==========
    
    def add_h2h_match(self, h2h_data: Dict[str, Any]) -> None:
        """添加历史交锋记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO head_to_head 
                (home_code, away_code, home_score, away_score, match_date, competition)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                h2h_data["home_code"],
                h2h_data["away_code"],
                h2h_data["home_score"],
                h2h_data["away_score"],
                h2h_data.get("match_date", ""),
                h2h_data.get("competition", "")
            ))
            conn.commit()
    
    def get_h2h_record(self, team_a: str, team_b: str) -> Dict[str, Any]:
        """获取两队历史交锋记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 查询两个方向的交锋
            cursor.execute("""
                SELECT * FROM head_to_head 
                WHERE (home_code = ? AND away_code = ?) 
                   OR (home_code = ? AND away_code = ?)
                ORDER BY match_date DESC
            """, (team_a, team_b, team_b, team_a))
            
            matches = [dict(row) for row in cursor.fetchall()]
            
            # 统计
            team_a_wins = sum(1 for m in matches if 
                (m["home_code"] == team_a and m["home_score"] > m["away_score"]) or
                (m["away_code"] == team_a and m["away_score"] > m["home_score"]))
            team_b_wins = sum(1 for m in matches if 
                (m["home_code"] == team_b and m["home_score"] > m["away_score"]) or
                (m["away_code"] == team_b and m["away_score"] > m["home_score"]))
            draws = len(matches) - team_a_wins - team_b_wins
            
            return {
                "total": len(matches),
                "team_a_wins": team_a_wins,
                "team_b_wins": team_b_wins,
                "draws": draws,
                "matches": matches[:10]  # 最近10场
            }
    
    # ========== 世界杯历史数据 ==========
    
    def upsert_wc_history(self, team_code: str, history_data: Dict[str, Any]) -> None:
        """更新世界杯历史数据"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO world_cup_history (team_code, appearances, best_result, titles, finals, semifinals, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                ON CONFLICT(team_code) DO UPDATE SET
                    appearances = excluded.appearances,
                    best_result = excluded.best_result,
                    titles = excluded.titles,
                    finals = excluded.finals,
                    semifinals = excluded.semifinals,
                    last_updated = datetime('now')
            """, (
                team_code,
                history_data.get("appearances", 0),
                history_data.get("best_result", ""),
                history_data.get("titles", 0),
                history_data.get("finals", 0),
                history_data.get("semifinals", 0)
            ))
            conn.commit()
    
    def get_wc_history(self, team_code: str) -> Optional[Dict[str, Any]]:
        """获取球队世界杯历史"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM world_cup_history WHERE team_code = ?", (team_code,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ========== 预测缓存 ==========
    
    def get_cached_prediction(self, match_key: str) -> Optional[Dict[str, Any]]:
        """获取缓存的预测结果"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT prediction_json FROM prediction_cache 
                WHERE match_key = ? AND expires_at > datetime('now')
            """, (match_key,))
            row = cursor.fetchone()
            if row:
                return json.loads(row["prediction_json"])
            return None
    
    def cache_prediction(self, match_key: str, prediction: Dict[str, Any], ttl_hours: int = 24) -> None:
        """缓存预测结果"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO prediction_cache (match_key, prediction_json, created_at, expires_at)
                VALUES (?, ?, datetime('now'), datetime('now', '+' || ? || ' hours'))
            """, (match_key, json.dumps(prediction), ttl_hours))
            conn.commit()


# 单例模式 - 但支持测试时注入
_db_instance: Optional[Database] = None


def get_database(db_path: Optional[str] = None) -> Database:
    """获取数据库实例（依赖注入入口）"""
    global _db_instance
    if _db_instance is None:
        _db_instance = Database(db_path or "/var/www/worldcup-predictor/backend/data/world_cup.db")
    return _db_instance


def reset_database(db_path: Optional[str] = None) -> Database:
    """重置数据库实例（用于测试）"""
    global _db_instance
    _db_instance = Database(db_path) if db_path else None
    return _db_instance
