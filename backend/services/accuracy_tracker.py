"""
准确率追踪系统 - 记录每次预测vs实际结果
"""
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
import sqlite3
import json


@dataclass
class PredictionRecord:
    """预测记录"""
    id: str
    match_id: str
    home_code: str
    away_code: str
    stage: str
    predicted: str  # HOME_WIN / DRAW / AWAY_WIN
    predicted_at: str
    
    # 预测概率
    home_prob: float
    draw_prob: float
    away_prob: float
    
    # 置信度
    confidence_level: str
    confidence_value: float
    
    # 实际结果
    actual_result: Optional[str] = None
    is_correct: Optional[bool] = None
    verified_at: Optional[str] = None
    
    # 冷门标记
    was_upset: bool = False
    upset_detected: bool = False


class AccuracyTracker:
    """准确率追踪器"""
    
    def __init__(self, db_path: str = "/var/www/worldcup-predictor/backend/data/prediction_accuracy.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 预测记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_records (
                id TEXT PRIMARY KEY,
                match_id TEXT NOT NULL,
                home_code TEXT NOT NULL,
                away_code TEXT NOT NULL,
                stage TEXT NOT NULL,
                predicted TEXT NOT NULL,
                predicted_at TEXT NOT NULL,
                home_prob REAL,
                draw_prob REAL,
                away_prob REAL,
                confidence_level TEXT,
                confidence_value REAL,
                actual_result TEXT,
                is_correct INTEGER,
                verified_at TEXT,
                was_upset INTEGER DEFAULT 0,
                upset_detected INTEGER DEFAULT 0
            )
        """)
        
        # 准确率统计表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accuracy_stats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stage TEXT NOT NULL,
                total_predictions INTEGER DEFAULT 0,
                correct_predictions INTEGER DEFAULT 0,
                accuracy REAL DEFAULT 0,
                last_updated TEXT
            )
        """)
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_match ON prediction_records(match_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_stage ON prediction_records(stage)")
        
        conn.commit()
        conn.close()
    
    def record_prediction(
        self,
        match_id: str,
        home_code: str,
        away_code: str,
        stage: str,
        predicted: str,
        home_prob: float,
        draw_prob: float,
        away_prob: float,
        confidence_level: str,
        confidence_value: float,
        upset_detected: bool = False
    ) -> str:
        """记录预测"""
        import random
        record_id = f"pred_{match_id}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}_{random.randint(1000,9999)}"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO prediction_records 
            (id, match_id, home_code, away_code, stage, predicted, predicted_at,
             home_prob, draw_prob, away_prob, confidence_level, confidence_value, upset_detected)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record_id, match_id, home_code, away_code, stage, predicted,
            datetime.now().isoformat(),
            home_prob, draw_prob, away_prob, confidence_level, confidence_value,
            int(upset_detected)
        ))
        
        conn.commit()
        conn.close()
        
        return record_id
    
    def verify_prediction(self, match_id: str, actual_result: str) -> Dict:
        """验证预测"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 查找该比赛的预测
        cursor.execute("""
            SELECT * FROM prediction_records WHERE match_id = ?
        """, (match_id,))
        
        predictions = cursor.fetchall()
        
        results = []
        for pred in predictions:
            is_correct = (pred["predicted"] == actual_result)
            
            # 判断是否是冷门（预测与实际相反）
            was_upset = False
            if pred["predicted"] != actual_result:
                was_upset = True
            
            # 更新记录
            cursor.execute("""
                UPDATE prediction_records SET
                    actual_result = ?,
                    is_correct = ?,
                    verified_at = ?,
                    was_upset = ?
                WHERE id = ?
            """, (actual_result, int(is_correct), datetime.now().isoformat(), int(was_upset), pred["id"]))
            
            results.append({
                "id": pred["id"],
                "predicted": pred["predicted"],
                "actual": actual_result,
                "is_correct": is_correct,
                "was_upset": was_upset
            })
        
        conn.commit()
        
        # 更新统计
        self._update_stats(conn)
        
        conn.close()
        
        return results
    
    def _update_stats(self, conn):
        """更新统计"""
        cursor = conn.cursor()
        
        # 查询各阶段统计
        cursor.execute("""
            SELECT stage, 
                   COUNT(*) as total,
                   SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM prediction_records
            WHERE actual_result IS NOT NULL
            GROUP BY stage
        """)
        
        for row in cursor.fetchall():
            accuracy = row["correct"] / row["total"] if row["total"] > 0 else 0
            
            cursor.execute("""
                INSERT OR REPLACE INTO accuracy_stats (stage, total_predictions, correct_predictions, accuracy, last_updated)
                VALUES (?, ?, ?, ?, ?)
            """, (row["stage"], row["total"], row["correct"], accuracy, datetime.now().isoformat()))
        
        conn.commit()
    
    def get_accuracy_report(self) -> Dict:
        """获取准确率报告"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 总体统计
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct,
                SUM(CASE WHEN was_upset = 1 THEN 1 ELSE 0 END) as upsets,
                SUM(CASE WHEN upset_detected = 1 AND was_upset = 1 THEN 1 ELSE 0 END) as detected_upsets
            FROM prediction_records
            WHERE actual_result IS NOT NULL
        """)
        
        overall = cursor.fetchone()
        
        # 分阶段统计
        cursor.execute("""
            SELECT stage, total_predictions, correct_predictions, accuracy
            FROM accuracy_stats
            ORDER BY stage
        """)
        
        by_stage = {}
        for row in cursor.fetchall():
            by_stage[row["stage"]] = {
                "total": row["total_predictions"],
                "correct": row["correct_predictions"],
                "accuracy": round(row["accuracy"] * 100, 1)
            }
        
        # 分置信度统计
        cursor.execute("""
            SELECT confidence_level,
                   COUNT(*) as total,
                   SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) as correct
            FROM prediction_records
            WHERE actual_result IS NOT NULL
            GROUP BY confidence_level
        """)
        
        by_confidence = {}
        for row in cursor.fetchall():
            by_confidence[row["confidence_level"]] = {
                "total": row["total"],
                "correct": row["correct"],
                "accuracy": round(row["correct"] / row["total"] * 100, 1) if row["total"] > 0 else 0
            }
        
        # 冷门检测效果
        upset_detection_rate = 0
        if overall["upsets"] and overall["upsets"] > 0:
            upset_detection_rate = (overall["detected_upsets"] or 0) / overall["upsets"]
        
        conn.close()
        
        return {
            "overall": {
                "total_predictions": overall["total"] or 0,
                "correct_predictions": overall["correct"] or 0,
                "accuracy": round((overall["correct"] or 0) / (overall["total"] or 1) * 100, 1),
                "total_upsets": overall["upsets"] or 0,
                "upset_detection_rate": round(upset_detection_rate * 100, 1)
            },
            "by_stage": by_stage,
            "by_confidence": by_confidence,
            "last_updated": datetime.now().isoformat()
        }
    
    def get_recent_predictions(self, limit: int = 50) -> List[Dict]:
        """获取最近的预测记录"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM prediction_records
            ORDER BY predicted_at DESC
            LIMIT ?
        """, (limit,))
        
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return records
    
    def clear_all(self):
        """清空所有记录（用于重新测试）"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM prediction_records")
        cursor.execute("DELETE FROM accuracy_stats")
        
        conn.commit()
        conn.close()


def get_accuracy_tracker():
    """获取准确率追踪器"""
    return AccuracyTracker()