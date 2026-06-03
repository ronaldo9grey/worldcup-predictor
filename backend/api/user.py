"""用户功能API路由"""
from fastapi import APIRouter, Cookie, Response, Query
from typing import Dict, Any, Optional

from repositories.user_repo import UserRepository
from core.database import get_database
from data.world_cup_2026 import get_team_lookup, MATCH_SCHEDULE

router = APIRouter(prefix="/api/user", tags=["用户"])

# 队名查找表
TEAM_LOOKUP = get_team_lookup()
# 比赛时间表
SCHEDULE = MATCH_SCHEDULE


def get_user_repo() -> UserRepository:
    """获取用户仓库实例"""
    db = get_database()
    return UserRepository(db.db_path)


@router.post("/login")
async def login(nickname: str = Query(..., description="用户昵称")) -> Dict[str, Any]:
    """
    用户登录/注册
    
    简单模式：传入昵称即可，返回 user_id 存入 cookie
    相同昵称会返回已有用户，防止重复注册
    """
    repo = get_user_repo()
    user = repo.create_user(nickname)
    
    # 根据是否为已有用户返回不同提示
    if user.get("is_existing"):
        message = f"欢迎回来，{nickname}！已找到您的历史记录 🎉"
    else:
        message = f"欢迎，{nickname}！新用户注册成功 ✨"
    
    return {
        "success": True,
        "user": user,
        "is_existing": user.get("is_existing", False),
        "message": message
    }


@router.get("/me")
async def get_current_user(user_id: Optional[str] = Cookie(None)) -> Dict[str, Any]:
    """获取当前用户信息"""
    if not user_id:
        return {"error": "未登录", "logged_in": False}
    
    repo = get_user_repo()
    user = repo.get_user(user_id)
    
    if not user:
        return {"error": "用户不存在", "logged_in": False}
    
    # 获取用户排名
    rank = repo.get_user_rank(user_id)
    
    return {
        "logged_in": True,
        "user": user,
        "rank": rank
    }


@router.post("/predict")
async def save_prediction(
    match_id: str = Query(..., description="比赛ID"),
    group_name: str = Query(..., description="小组名"),
    match_idx: int = Query(..., description="比赛索引"),
    home_code: str = Query(..., description="主队代码"),
    away_code: str = Query(..., description="客队代码"),
    prediction: str = Query(..., description="预测结果: HOME_WIN/DRAW/AWAY_WIN"),
    confidence: str = Query(..., description="信心等级: HIGH/MEDIUM/LOW"),
    user_id: Optional[str] = Cookie(None)
) -> Dict[str, Any]:
    """保存用户预测"""
    if not user_id:
        return {"error": "请先登录", "success": False}
    
    repo = get_user_repo()
    
    # 确保用户存在
    user = repo.get_or_create_user(user_id)
    
    result = repo.save_prediction(
        user_id=user_id,
        match_id=match_id,
        group_name=group_name,
        match_idx=match_idx,
        home_code=home_code,
        away_code=away_code,
        prediction=prediction,
        confidence=confidence
    )
    
    # 添加中文队名到返回结果
    home_team = TEAM_LOOKUP.get(home_code)
    away_team = TEAM_LOOKUP.get(away_code)
    if home_team:
        result["home_name_cn"] = home_team["name_cn"]
    if away_team:
        result["away_name_cn"] = away_team["name_cn"]
    
    return {
        "success": True,
        "prediction": result,
        "message": "预测已保存"
    }


@router.get("/my-predictions")
async def get_my_predictions(
    user_id: Optional[str] = Cookie(None)
) -> Dict[str, Any]:
    """获取我的预测记录（含中文队名和比赛时间）"""
    if not user_id:
        return {"error": "请先登录", "predictions": []}
    
    repo = get_user_repo()
    predictions = repo.get_user_predictions(user_id)
    
    # 添加中文队名和比赛时间
    for pred in predictions:
        home_team = TEAM_LOOKUP.get(pred["home_code"])
        away_team = TEAM_LOOKUP.get(pred["away_code"])
        if home_team:
            pred["home_name_cn"] = home_team["name_cn"]
        if away_team:
            pred["away_name_cn"] = away_team["name_cn"]
        
        # 添加比赛时间
        match_id = f"{pred['group_name']}_{pred['match_idx']}"
        if match_id in SCHEDULE:
            pred["match_datetime"] = SCHEDULE[match_id]["datetime"]
            pred["match_date"] = SCHEDULE[match_id]["date"]
            pred["match_time"] = SCHEDULE[match_id]["time"]
    
    # 按小组分组
    grouped = {}
    for pred in predictions:
        group = pred["group_name"]
        if group not in grouped:
            grouped[group] = []
        grouped[group].append(pred)
    
    return {
        "total": len(predictions),
        "predictions": predictions,
        "by_group": grouped
    }


@router.get("/leaderboard")
async def get_leaderboard(limit: int = Query(50, ge=1, le=100)) -> Dict[str, Any]:
    """获取排行榜"""
    repo = get_user_repo()
    leaderboard = repo.get_leaderboard(limit)
    
    return {
        "leaderboard": leaderboard,
        "total": len(leaderboard)
    }


@router.get("/all-users")
async def get_all_users() -> Dict[str, Any]:
    """获取所有用户列表（昵称选择器用）"""
    repo = get_user_repo()
    users = repo.get_all_users()
    
    return {
        "users": users,
        "total": len(users)
    }


@router.delete("/delete/{user_id}")
async def delete_user(user_id: str) -> Dict[str, Any]:
    """删除用户及其所有预测记录"""
    repo = get_user_repo()
    
    # 删除用户
    success = repo.delete_user(user_id)
    
    if success:
        return {"success": True, "message": "用户已删除"}
    else:
        return {"success": False, "error": "用户不存在"}


@router.post("/verify/{match_id}")
async def verify_match_result(
    match_id: str,
    result: str = Query(..., description="比赛结果: HOME_WIN/DRAW/AWAY_WIN")
) -> Dict[str, Any]:
    """验证比赛结果（管理员功能）"""
    repo = get_user_repo()
    
    # 批量验证该比赛的所有预测
    verified = repo.verify_match(match_id, result)
    
    return {
        "success": True,
        "match_id": match_id,
        "result": result,
        "verified_count": len(verified),
        "details": verified
    }


@router.get("/match/{match_id}/predictions")
async def get_match_all_predictions(match_id: str) -> Dict[str, Any]:
    """获取某场比赛的所有用户预测"""
    repo = get_user_repo()
    predictions = repo.get_match_predictions(match_id)
    
    # 添加中文队名
    for pred in predictions:
        home_team = TEAM_LOOKUP.get(pred["home_code"])
        away_team = TEAM_LOOKUP.get(pred["away_code"])
        if home_team:
            pred["home_name_cn"] = home_team["name_cn"]
        if away_team:
            pred["away_name_cn"] = away_team["name_cn"]
    
    # 统计
    stats = {"HOME_WIN": 0, "DRAW": 0, "AWAY_WIN": 0}
    for pred in predictions:
        if pred["prediction"] in stats:
            stats[pred["prediction"]] += 1
    
    return {
        "match_id": match_id,
        "total": len(predictions),
        "predictions": predictions,
        "stats": stats
    }