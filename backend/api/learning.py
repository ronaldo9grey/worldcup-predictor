"""
在线学习API
提供实时学习和模型更新的接口
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Optional
from pydantic import BaseModel

from services.online_learning import get_online_learning
from services.model_ensemble import get_ensemble

router = APIRouter(prefix="/api/learning", tags=["learning"])


class MatchResultInput(BaseModel):
    """比赛结果输入"""
    match_id: str
    home_code: str
    away_code: str
    predicted: str
    actual: str
    model_used: str = "ensemble"
    confidence: float = 0.5


@router.get("/stats")
async def get_learning_stats():
    """
    获取学习统计
    
    返回在线学习的统计数据
    """
    learning = get_online_learning()
    
    return learning.get_learning_stats()


@router.get("/report")
async def get_learning_report():
    """
    获取学习报告
    
    返回详细的学习报告
    """
    learning = get_online_learning()
    
    return learning.export_learning_report()


@router.post("/feedback")
async def submit_match_feedback(result: MatchResultInput):
    """
    提交比赛结果反馈
    
    用于在线学习，实时更新模型权重
    """
    learning = get_online_learning()
    ensemble = get_ensemble()
    
    # 处理反馈
    feedback_result = learning.process_match_result(
        match_id=result.match_id,
        home_code=result.home_code,
        away_code=result.away_code,
        predicted=result.predicted,
        actual=result.actual,
        model_used=result.model_used,
        confidence=result.confidence,
        current_weights=ensemble.model_weights
    )
    
    # 如果权重调整了，更新集成模型
    if feedback_result['weight_adjusted']:
        ensemble.update_weights(feedback_result['new_weights'])
    
    return {
        "success": True,
        "message": "反馈已处理",
        "result": feedback_result
    }


@router.get("/history")
async def get_learning_history(limit: int = Query(20, description="返回数量")):
    """
    获取学习历史
    
    返回最近的学习事件
    """
    learning = get_online_learning()
    
    events = learning.learning_history[-limit:]
    
    return {
        "total": len(learning.learning_history),
        "events": [
            {
                "timestamp": e.timestamp,
                "match": f"{e.home_code} vs {e.away_code}",
                "predicted": e.predicted,
                "actual": e.actual,
                "correct": e.is_correct,
                "model": e.model_used,
                "weight_adjusted": e.weights_before != e.weights_after,
                "reason": e.adjustment_reason
            }
            for e in events
        ]
    }


@router.post("/reset")
async def reset_learning():
    """
    重置学习状态
    
    清空所有学习历史和统计数据
    """
    learning = get_online_learning()
    learning.reset_learning()
    
    # 重置模型权重
    ensemble = get_ensemble()
    ensemble.model_weights = {
        'bayesian': 0.4,
        'neural_network': 0.3,
        'random_forest': 0.3
    }
    
    return {
        "success": True,
        "message": "学习状态已重置"
    }


@router.get("/drift-check")
async def check_concept_drift():
    """
    检测概念漂移
    
    分析是否存在数据分布变化
    """
    learning = get_online_learning()
    stats = learning.get_learning_stats()
    
    drift_status = "normal"
    drift_message = "模型表现稳定"
    
    accuracy_drop = stats['baseline_accuracy'] - stats['recent_accuracy']
    
    if accuracy_drop > learning.drift_threshold:
        drift_status = "warning"
        drift_message = f"警告: 准确率下降 {accuracy_drop:.1%}，可能存在概念漂移"
    elif accuracy_drop > learning.drift_threshold * 0.5:
        drift_status = "attention"
        drift_message = f"注意: 准确率略降 {accuracy_drop:.1%}"
    
    return {
        "status": drift_status,
        "message": drift_message,
        "baseline_accuracy": stats['baseline_accuracy'],
        "current_accuracy": stats['recent_accuracy'],
        "accuracy_drop": accuracy_drop,
        "threshold": learning.drift_threshold,
        "recommendation": _get_drift_recommendation(drift_status)
    }


@router.post("/adjust-learning-rate")
async def adjust_learning_rate(rate: float = Query(..., ge=0.01, le=0.5)):
    """
    调整学习率
    
    手动设置在线学习的学习率
    """
    learning = get_online_learning()
    learning.learning_rate = rate
    
    return {
        "success": True,
        "message": f"学习率已调整为 {rate}",
        "learning_rate": rate
    }


def _get_drift_recommendation(status: str) -> str:
    """获取漂移建议"""
    recommendations = {
        "normal": "继续观察，无需调整",
        "attention": "建议关注后续比赛结果，准备调整模型权重",
        "warning": "建议重新训练模型或调整集成权重，增加适应性强的模型权重"
    }
    return recommendations.get(status, "未知状态")
