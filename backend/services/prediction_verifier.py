"""
预测验证服务
验证预测结果并更新状态
"""
from datetime import datetime
from typing import Optional, Dict
from enum import Enum
from dataclasses import dataclass


class PredictionStatus(Enum):
    """预测状态"""
    PENDING = "待揭晓"
    CORRECT = "已命中"
    INCORRECT = "未命中"


@dataclass
class PredictionRecord:
    """预测记录"""
    match_id: str
    group_name: str
    match_index: int
    
    # 胜平负预测
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    final_prediction: str  # HOME_WIN, DRAW, AWAY_WIN
    
    # 比分预测
    score_prediction: str  # "2-1"
    expected_home_goals: float
    expected_away_goals: float
    
    # 大小球预测
    over_under_line: float
    over_prob: float
    under_prob: float
    over_under_recommendation: str
    
    # 状态
    status: PredictionStatus = PredictionStatus.PENDING
    actual_result: Optional[str] = None
    actual_score: Optional[str] = None
    
    # 时间戳
    created_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None


class PredictionVerifier:
    """
    预测验证器
    
    比赛结束后验证预测结果
    - 验证胜平负预测
    - 验证比分预测
    - 验证大小球预测
    - 更新准确率统计
    """
    
    def __init__(self, db_session):
        self.db = db_session
    
    async def verify_match_result(
        self,
        match_id: str,
        home_score: int,
        away_score: int
    ) -> Dict:
        """
        验证比赛结果
        
        参数：
        - match_id: 比赛ID
        - home_score: 主队实际进球
        - away_score: 客队实际进球
        
        返回：
        - 验证结果
        """
        
        # 1. 获取预测记录
        prediction = await self._get_prediction(match_id)
        
        if not prediction:
            return {
                "success": False,
                "error": "未找到预测记录"
            }
        
        # 2. 确定实际结果
        if home_score > away_score:
            actual_result = "HOME_WIN"
        elif home_score < away_score:
            actual_result = "AWAY_WIN"
        else:
            actual_result = "DRAW"
        
        actual_score = f"{home_score}-{away_score}"
        
        # 3. 验证胜平负预测
        win_draw_lose_correct = (prediction.final_prediction == actual_result)
        
        # 4. 验证比分预测
        score_correct = (prediction.score_prediction == actual_score)
        
        # 5. 验证大小球预测
        total_goals = home_score + away_score
        over_under_correct = self._verify_over_under(
            prediction, total_goals
        )
        
        # 6. 更新预测状态
        prediction.status = PredictionStatus.CORRECT if win_draw_lose_correct else PredictionStatus.INCORRECT
        prediction.actual_result = actual_result
        prediction.actual_score = actual_score
        prediction.verified_at = datetime.now()
        
        # 7. 保存记录
        await self._save_prediction(prediction)
        
        # 8. 更新模型准确率
        await self._update_model_accuracy(prediction)
        
        return {
            "success": True,
            "match_id": match_id,
            "actual_result": {
                "score": actual_score,
                "result": self._get_result_label(actual_result)
            },
            "verification": {
                "win_draw_lose": {
                    "predicted": self._get_result_label(prediction.final_prediction),
                    "actual": self._get_result_label(actual_result),
                    "correct": win_draw_lose_correct
                },
                "score": {
                    "predicted": prediction.score_prediction,
                    "actual": actual_score,
                    "correct": score_correct
                },
                "over_under": {
                    "predicted": prediction.over_under_recommendation,
                    "actual_total": total_goals,
                    "correct": over_under_correct
                }
            },
            "status": prediction.status.value
        }
    
    def _verify_over_under(self, prediction: PredictionRecord, total_goals: int) -> bool:
        """验证大小球预测"""
        
        if prediction.over_under_recommendation.startswith("大"):
            return total_goals > prediction.over_under_line
        elif prediction.over_under_recommendation.startswith("小"):
            return total_goals <= prediction.over_under_line
        else:
            return None  # 观望，不计入统计
    
    def _get_result_label(self, result: str) -> str:
        """获取结果标签"""
        labels = {
            "HOME_WIN": "主胜",
            "DRAW": "平局",
            "AWAY_WIN": "客胜"
        }
        return labels.get(result, result)
    
    async def _get_prediction(self, match_id: str) -> Optional[PredictionRecord]:
        """获取预测记录"""
        # TODO: 从数据库查询
        # 这里应该从数据库中查询预测记录
        # 目前返回 None，等待数据库实现
        return None
    
    async def _save_prediction(self, prediction: PredictionRecord):
        """保存预测记录"""
        # TODO: 保存到数据库
        pass
    
    async def _update_model_accuracy(self, prediction: PredictionRecord):
        """更新模型准确率统计"""
        # TODO: 更新模型的准确率
        pass
    
    async def get_prediction_status(self, match_id: str) -> Dict:
        """
        获取预测状态
        
        返回：
        - 预测详情和状态
        """
        
        prediction = await self._get_prediction(match_id)
        
        if not prediction:
            return {
                "success": False,
                "error": "未找到预测记录"
            }
        
        return {
            "success": True,
            "match_id": match_id,
            "prediction": {
                "win_draw_lose": {
                    "predicted": self._get_result_label(prediction.final_prediction),
                    "probabilities": {
                        "home_win": f"{prediction.home_win_prob * 100:.1f}%",
                        "draw": f"{prediction.draw_prob * 100:.1f}%",
                        "away_win": f"{prediction.away_win_prob * 100:.1f}%"
                    }
                },
                "score": {
                    "predicted": prediction.score_prediction,
                    "expected_goals": {
                        "home": prediction.expected_home_goals,
                        "away": prediction.expected_away_goals
                    }
                },
                "over_under": {
                    "line": prediction.over_under_line,
                    "predicted": prediction.over_under_recommendation,
                    "probabilities": {
                        "over": f"{prediction.over_prob:.1f}%",
                        "under": f"{prediction.under_prob:.1f}%"
                    }
                }
            },
            "status": prediction.status.value,
            "actual_result": {
                "score": prediction.actual_score,
                "result": self._get_result_label(prediction.actual_result) if prediction.actual_result else None
            },
            "created_at": prediction.created_at.isoformat() if prediction.created_at else None,
            "verified_at": prediction.verified_at.isoformat() if prediction.verified_at else None
        }


# 批量验证
async def batch_verify_predictions(matches: list):
    """
    批量验证多场比赛
    
    参数：
    - matches: 比赛结果列表 [{match_id, home_score, away_score}, ...]
    """
    
    verifier = PredictionVerifier(None)
    results = []
    
    for match in matches:
        result = await verifier.verify_match_result(
            match["match_id"],
            match["home_score"],
            match["away_score"]
        )
        results.append(result)
    
    return results
