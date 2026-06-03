"""
自动验证API
"""
from fastapi import APIRouter, Query, BackgroundTasks
from typing import Dict, Any

from services.auto_verification import get_auto_verification_system, get_match_result_fetcher

router = APIRouter(prefix="/api/auto-verify", tags=["自动验证"])


@router.get("/status")
async def get_verification_status() -> Dict[str, Any]:
    """
    获取自动验证状态
    
    返回：
    - 已验证比赛列表
    - 总验证数
    - 最后验证时间
    """
    system = get_auto_verification_system()
    return system.get_verification_status()


@router.post("/run")
async def run_auto_verification(background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    运行自动验证
    
    从网络获取已完成的比赛结果，自动验证所有预测
    """
    system = get_auto_verification_system()
    
    # 同步执行验证
    results = system.auto_verify_all()
    
    return {
        "success": True,
        "message": f"已完成验证 {results['verified']} 场比赛",
        "results": results
    }


@router.get("/completed-matches")
async def get_completed_matches() -> Dict[str, Any]:
    """
    获取已完成的比赛列表
    
    返回所有已完成的比赛结果
    """
    fetcher = get_match_result_fetcher()
    matches = fetcher.fetch_completed_matches("WC2026")
    
    return {
        "total": len(matches),
        "matches": matches
    }


@router.post("/match/{match_id}")
async def verify_single_match(match_id: str) -> Dict[str, Any]:
    """
    验证单场比赛
    
    Args:
        match_id: 比赛ID（如 A_0）
    """
    system = get_auto_verification_system()
    result = system.auto_verify_match(match_id)
    
    return {
        "success": True,
        "match_id": match_id,
        "verification": result
    }


@router.get("/check/{match_id}")
async def check_match_status(match_id: str) -> Dict[str, Any]:
    """
    检查比赛状态
    
    Returns:
        "not_started" - 未开始
        "in_progress" - 进行中
        "completed" - 已完成
    """
    fetcher = get_match_result_fetcher()
    status = fetcher.check_match_status(match_id)
    
    match_result = fetcher.fetch_by_match_id(match_id)
    
    return {
        "match_id": match_id,
        "status": status,
        "result": match_result
    }


@router.post("/simulate")
async def simulate_match_results() -> Dict[str, Any]:
    """
    模拟比赛结果（用于演示）
    
    使用历史世界杯数据作为模拟结果
    """
    system = get_auto_verification_system()
    results = system.auto_verify_all()
    
    return {
        "success": True,
        "message": "已使用模拟数据验证比赛结果",
        "verified": results["verified"],
        "accuracy": results["accuracy_report"]["overall"]["accuracy"]
    }