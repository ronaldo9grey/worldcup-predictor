"""用户功能API路由"""
from fastapi import APIRouter, Cookie, Response, Query, Body
from typing import Dict, Any, Optional
from pydantic import BaseModel

from repositories.user_repo import UserRepository
from core.database import get_database
from data.world_cup_2026 import get_team_lookup, MATCH_SCHEDULE

router = APIRouter(prefix="/api/user", tags=["用户"])

# 队名查找表
TEAM_LOOKUP = get_team_lookup()
# 比赛时间表
SCHEDULE = MATCH_SCHEDULE


class PredictRequest(BaseModel):
    """预测请求模型"""
    nickname: str
    device_key: str = None  # 设备密钥（可选）
    group: str
    match_idx: int
    prediction: str  # HOME_WIN/DRAW/AWAY_WIN
    confidence: str  # HIGH/MEDIUM/LOW
    home_code: str
    away_code: str


def get_user_repo() -> UserRepository:
    """获取用户仓库实例"""
    db = get_database()
    return UserRepository(db.db_path)


@router.post("/login")
async def login(
    nickname: str = Query(..., description="用户昵称"),
    device_key: str = Query(None, description="设备密钥"),
    response: Response = None
) -> Dict[str, Any]:
    """
    用户登录/注册
    
    简单模式：传入昵称和device_key即可
    - 首次登录：自动创建用户并绑定device_key
    - 再次登录：验证device_key，防止冒用
    """
    repo = get_user_repo()
    user = repo.create_user(nickname, device_key)
    
    # 检查是否被拒绝
    if user.get("error"):
        return {
            "success": False,
            "error": user["error"],
            "nickname_taken": user.get("nickname_taken", False)
        }
    
    # 设置Cookie（30天有效期）
    if response and user.get("user_id"):
        response.set_cookie(
            key="user_id",
            value=user["user_id"],
            max_age=30*24*60*60,  # 30天
            httponly=False,
            samesite="lax"
        )
    
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


@router.post("/predict-simple")
async def save_prediction_simple(request: PredictRequest = Body(...)) -> Dict[str, Any]:
    """简化预测接口 - 只需昵称即可参与"""
    repo = get_user_repo()
    
    # 创建/获取用户，验证device_key
    user = repo.create_user(request.nickname, request.device_key)
    
    # 检查是否被拒绝
    if user.get("error"):
        return {
            "success": False,
            "error": user["error"],
            "nickname_taken": user.get("nickname_taken", False)
        }
    
    # 检查比赛是否已结束
    # 直接使用 WorldCup26Source 获取实时数据
    from data.sources.worldcup26_source import WorldCup26Source
    try:
        source = WorldCup26Source()
        matches = await source.get_matches(group=request.group)
        
        # 球队代码映射（WorldCup26.ir 使用旧代码）
        code_mapping = {'RSA': 'ZAF', 'KSA': 'SAU', 'CHI': 'CHL'}
        
        # 找到对应比赛
        for match in matches:
            # 获取比赛双方代码（转换旧代码）
            match_home = code_mapping.get(match.home_code, match.home_code)
            match_away = code_mapping.get(match.away_code, match.away_code)
            
            # 检查是否是这场比赛
            if (match_home == request.home_code and 
                match_away == request.away_code):
                
                # 检查比赛状态
                print(f"比赛状态: {match.status} ({request.home_code} vs {request.away_code}), 比分: {match.home_score}-{match.away_score}")
                
                # 如果比赛已结束，拒绝预测
                if match.status == 'finished':
                    return {
                        "success": False,
                        "error": "该比赛已结束，无法预测"
                    }
                
                # 如果比赛正在进行中，拒绝预测
                if match.status == 'live':
                    return {
                        "success": False,
                        "error": "该比赛已开始，无法预测"
                    }
                break
    except Exception as e:
        print(f"检查比赛状态失败: {e}")
        # 如果检查失败，允许预测（降级策略）
    
    
    user_id = user["user_id"]
    
    # 构建match_id
    match_id = f"{request.group}_{request.match_idx}"
    
    # 保存预测
    result = repo.save_prediction(
        user_id=user_id,
        match_id=match_id,
        group_name=request.group,
        match_idx=request.match_idx,
        home_code=request.home_code,
        away_code=request.away_code,
        prediction=request.prediction,
        confidence=request.confidence
    )
    
    # 添加中文队名
    home_team = TEAM_LOOKUP.get(request.home_code)
    away_team = TEAM_LOOKUP.get(request.away_code)
    if home_team:
        result["home_name_cn"] = home_team["name_cn"]
    if away_team:
        result["away_name_cn"] = away_team["name_cn"]
    
    return {
        "success": True,
        "user": user,
        "prediction": result,
        "message": f"感谢参与预测，{request.nickname}！"
    }


@router.get("/prediction-stats/{group}/{match_idx}")
async def get_prediction_stats(group: str, match_idx: int) -> Dict[str, Any]:
    """获取某场比赛的预测统计"""
    repo = get_user_repo()
    match_id = f"{group}_{match_idx}"
    
    # 获取该比赛的所有预测
    predictions = repo.get_match_predictions(match_id)
    
    # 统计各选项数量
    home_win_count = sum(1 for p in predictions if p["prediction"] == "HOME_WIN")
    draw_count = sum(1 for p in predictions if p["prediction"] == "DRAW")
    away_win_count = sum(1 for p in predictions if p["prediction"] == "AWAY_WIN")
    total = len(predictions)
    
    # 计算百分比
    if total > 0:
        home_win_pct = round(home_win_count / total * 100, 1)
        draw_pct = round(draw_count / total * 100, 1)
        away_win_pct = round(away_win_count / total * 100, 1)
    else:
        home_win_pct = 0
        draw_pct = 0
        away_win_pct = 0
    
    return {
        "match_id": match_id,
        "group": group,
        "match_idx": match_idx,
        "total_predictions": total,
        "home_win_count": home_win_count,
        "draw_count": draw_count,
        "away_win_count": away_win_count,
        "home_win_pct": home_win_pct,
        "draw_pct": draw_pct,
        "away_win_pct": away_win_pct
    }


@router.get("/my-predictions")
async def get_my_predictions(
    user_id: Optional[str] = Cookie(None)
) -> Dict[str, Any]:
    """获取我的预测记录（含中文队名、比赛时间、验证结果）"""
    if not user_id:
        return {"error": "请先登录", "predictions": []}
    
    repo = get_user_repo()
    predictions = repo.get_user_predictions(user_id)
    
    # 球队代码映射
    code_mapping = {"RSA": "ZAF", "KSA": "SAU"}
    
    # 添加中文队名、比赛时间和验证结果
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
        
        # 优先使用数据库中已保存的验证结果
        if pred.get("verified_at"):
            # 已验证的预测，使用保存的数据
            pred["match_status"] = "finished"
            # actual_result、is_correct、points_earned 已经在 pred 中
        else:
            # 未验证的预测，设置默认值
            pred["match_status"] = "pending"
            pred["actual_result"] = None
            pred["is_correct"] = None
            pred["points_earned"] = None
    
    # 批量获取比赛状态（从数据服务）- 仅处理未验证的预测
    try:
        from services.data_service import get_data_service
        import asyncio
        
        ds = get_data_service()
        
        # 只处理未验证的预测
        unverified_preds = [p for p in predictions if not p.get("verified_at")]
        
        if unverified_preds:
            # 获取所有涉及的组的比赛数据
            groups_needed = set(pred["group_name"] for pred in unverified_preds)
            
            for group in groups_needed:
                try:
                    matches = await asyncio.wait_for(
                        ds.get_matches(group=group),
                        timeout=5.0
                    )
                    
                    # 更新该组所有预测的状态
                    for pred in unverified_preds:
                        if pred["group_name"] != group:
                            continue
                        
                        # 查找对应比赛
                        for match in matches:
                            match_home = code_mapping.get(match.get("home"), match.get("home"))
                            match_away = code_mapping.get(match.get("away"), match.get("away"))
                            
                            if match_home == pred["home_code"] and match_away == pred["away_code"]:
                                match_status = match.get("status", "scheduled")
                                pred["match_status"] = "finished" if match_status == "finished" else "live" if match_status == "live" else "pending"
                                
                                # 如果比赛结束，判断预测结果
                                if match_status == "finished":
                                    home_score = match.get("home_score")
                                    away_score = match.get("away_score")
                                    
                                    if home_score is not None and away_score is not None:
                                        if home_score > away_score:
                                            pred["actual_result"] = "HOME_WIN"
                                        elif home_score < away_score:
                                            pred["actual_result"] = "AWAY_WIN"
                                        else:
                                            pred["actual_result"] = "DRAW"
                                        
                                        # 判断预测是否正确
                                        pred["is_correct"] = (pred["prediction"] == pred["actual_result"])
                                        
                                        # 计算得分
                                        if pred["is_correct"]:
                                            confidence = pred.get("confidence", "MEDIUM")
                                            points_map = {"HIGH": 3, "MEDIUM": 2, "LOW": 5}
                                            pred["points_earned"] = points_map.get(confidence, 2)
                                        else:
                                            pred["points_earned"] = 0
                                break
                except Exception as e:
                    print(f"获取{group}组比赛数据失败: {e}")
                    continue
    except Exception as e:
        print(f"批量获取比赛状态失败: {e}")
    
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


@router.get("/logout")
async def logout(response: Response) -> Dict[str, Any]:
    """用户登出"""
    # 清除Cookie
    response.delete_cookie(key="user_id")
    return {
        "success": True,
        "message": "已退出登录"
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