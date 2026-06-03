"""
准确率追踪API
"""
from fastapi import APIRouter, Query
from typing import Dict, Any

from services.prediction_engine_v4 import create_v4_engine
from services.accuracy_tracker import get_accuracy_tracker
from services.model_trainer import get_default_trainer
from data.historical_world_cups import get_world_cup_stats, get_world_cup_upsets

router = APIRouter(prefix="/api/accuracy", tags=["准确率追踪"])


@router.get("/report")
async def get_accuracy_report() -> Dict[str, Any]:
    """
    获取准确率报告
    
    包含：
    - 总体准确率
    - 分阶段准确率
    - 分置信度准确率
    - 冷门检测效果
    """
    tracker = get_accuracy_tracker()
    report = tracker.get_accuracy_report()
    
    # 添加历史数据准确率
    trainer = get_default_trainer()
    trainer_report = trainer.get_accuracy_report()
    
    report["historical_training"] = trainer_report
    
    return report


@router.get("/predictions")
async def get_recent_predictions(limit: int = Query(50, ge=1, le=200)) -> Dict[str, Any]:
    """
    获取最近的预测记录
    
    用于查看预测历史和验证状态
    """
    tracker = get_accuracy_tracker()
    predictions = tracker.get_recent_predictions(limit)
    
    return {
        "total": len(predictions),
        "predictions": predictions
    }


@router.get("/stats")
async def get_world_cup_stats() -> Dict[str, Any]:
    """
    获取世界杯历史统计
    
    包含：
    - 分析的比赛数量
    - 冷门数量
    - 冷门规律
    - 各洲球队表现
    """
    stats = get_world_cup_stats()
    
    return stats


@router.get("/upsets")
async def get_upsets(min_severity: int = Query(3, ge=1, le=5)) -> Dict[str, Any]:
    """
    获取历史冷门比赛
    
    用于学习冷门规律
    """
    upsets = get_world_cup_upsets(min_severity)
    
    return {
        "total": len(upsets),
        "upsets": upsets
    }


@router.post("/verify/{match_id}")
async def verify_prediction(match_id: str, result: str = Query(...)) -> Dict[str, Any]:
    """
    验证比赛结果并更新准确率
    
    Args:
        match_id: 比赛ID（如 A_0）
        result: 实际结果（HOME_WIN/DRAW/AWAY_WIN）
    """
    tracker = get_accuracy_tracker()
    results = tracker.verify_prediction(match_id, result)
    
    # 获取更新后的准确率
    report = tracker.get_accuracy_report()
    
    return {
        "success": True,
        "verified_count": len(results),
        "verification_details": results,
        "updated_accuracy": report
    }


@router.post("/clear")
async def clear_predictions() -> Dict[str, Any]:
    """
    清空所有预测记录
    
    用于重新测试或重置
    """
    tracker = get_accuracy_tracker()
    tracker.clear_all()
    
    return {
        "success": True,
        "message": "所有预测记录已清空"
    }


@router.get("/weights")
async def get_optimized_weights() -> Dict[str, Any]:
    """
    获取优化后的权重
    
    用于理解模型如何决策
    """
    trainer = get_default_trainer()
    weights = trainer.get_optimized_weights()
    report = trainer.get_accuracy_report()
    
    return {
        "weights": weights,
        "training_accuracy": report["overall_accuracy"],
        "training_years": report["training_years"],
        "total_matches": report["total_matches"]
    }