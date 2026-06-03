"""
API路由 - 预测接口 V6
支持P0优化后的预测引擎
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
import sys

sys.path.append('/var/www/worldcup-predictor/backend')

from services.prediction_engine_v6 import get_engine_v6
from data.world_cup_2026 import GROUPS, get_team_lookup, get_group_teams

router = APIRouter(prefix="/api/v6", tags=["prediction-v6"])


# ========== 请求模型 ==========

class PredictMatchRequest(BaseModel):
    """预测比赛请求"""
    home_code: str
    away_code: str
    stage: str = "GROUP"
    group: Optional[str] = None


class PredictGroupRequest(BaseModel):
    """预测小组请求"""
    group: str


# ========== 响应模型 ==========

class PredictionResponse(BaseModel):
    """预测响应"""
    home_code: str
    home_name: str
    away_code: str
    away_name: str
    prediction: str
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    confidence_level: str
    confidence_value: float
    
    # P0新增特征
    features: Dict[str, float]
    upset_score: float
    is_upset_warning: bool
    upset_factors: List[str]
    stage_learning_rate: float
    
    # 特征分析
    feature_analysis: Optional[Dict] = None


class GroupPredictionResponse(BaseModel):
    """小组预测响应"""
    group: str
    teams: List[str]
    predictions: List[PredictionResponse]


# ========== API端点 ==========

@router.get("/groups")
async def get_groups():
    """获取所有分组"""
    return {
        "groups": GROUPS,
        "total_groups": len(GROUPS),
        "teams_per_group": 4
    }


@router.get("/groups/{group}")
async def get_group_info(group: str):
    """获取指定小组信息"""
    group = group.upper()
    if group not in GROUPS:
        raise HTTPException(status_code=404, detail=f"分组 {group} 不存在")
    
    teams = get_group_teams(group)
    return {
        "group": group,
        "teams": [
            {
                "code": t.get("code", ""),
                "name": t.get("name", ""),
                "name_cn": t.get("name_cn", ""),
                "rank": t.get("rank", 0),
                "elo": t.get("elo", 1500)
            }
            for t in teams
        ]
    }


@router.post("/predict", response_model=PredictionResponse)
async def predict_match(request: PredictMatchRequest):
    """预测比赛结果（P0优化版）"""
    engine = get_engine_v6()
    
    # 预测
    pred = engine.predict_match(
        home_code=request.home_code,
        away_code=request.away_code,
        stage=request.stage,
        group=request.group
    )
    
    # 特征分析
    analysis = engine.get_feature_analysis(
        request.home_code,
        request.away_code,
        request.stage
    )
    
    return PredictionResponse(
        home_code=pred.home_code,
        home_name=pred.home_name_cn,
        away_code=pred.away_code,
        away_name=pred.away_name_cn,
        prediction=pred.prediction,
        home_win_prob=pred.home_win_prob,
        draw_prob=pred.draw_prob,
        away_win_prob=pred.away_win_prob,
        confidence_level=pred.confidence_level,
        confidence_value=pred.confidence_value,
        features=pred.features.to_dict(),
        upset_score=pred.upset_score,
        is_upset_warning=pred.is_upset_warning,
        upset_factors=pred.upset_factors,
        stage_learning_rate=pred.stage_learning_rate,
        feature_analysis={
            "total_bias": analysis["total_bias"],
            "top_factors": sorted(
                [(k, v) for k, v in analysis["contributions"].items()],
                key=lambda x: abs(x[1]["contribution"]),
                reverse=True
            )[:5]
        }
    )


@router.post("/predict/group", response_model=GroupPredictionResponse)
async def predict_group(request: PredictGroupRequest):
    """预测整个小组"""
    group = request.group.upper()
    if group not in GROUPS:
        raise HTTPException(status_code=404, detail=f"分组 {group} 不存在")
    
    engine = get_engine_v6()
    predictions = engine.predict_group(group)
    
    return GroupPredictionResponse(
        group=group,
        teams=GROUPS[group],
        predictions=[
            PredictionResponse(
                home_code=pred.home_code,
                home_name=pred.home_name_cn,
                away_code=pred.away_code,
                away_name=pred.away_name_cn,
                prediction=pred.prediction,
                home_win_prob=pred.home_win_prob,
                draw_prob=pred.draw_prob,
                away_win_prob=pred.away_win_prob,
                confidence_level=pred.confidence_level,
                confidence_value=pred.confidence_value,
                features=pred.features.to_dict(),
                upset_score=pred.upset_score,
                is_upset_warning=pred.is_upset_warning,
                upset_factors=pred.upset_factors,
                stage_learning_rate=pred.stage_learning_rate
            )
            for pred in predictions
        ]
    )


@router.get("/features/importance")
async def get_feature_importance():
    """获取特征重要性"""
    from services.feature_engine_v2 import get_feature_engine_v2
    
    engine = get_feature_engine_v2()
    importance = engine.get_feature_importance()
    
    return {
        "feature_importance": importance,
        "total_features": len(importance),
        "p0_new_features": ["h2h", "venue_factor", "elo_form_combined", "rank_stage_combined"]
    }


@router.get("/learning/stats")
async def get_learning_stats():
    """获取在线学习统计"""
    from services.online_learning_v2 import get_online_learning_v2
    
    learner = get_online_learning_v2()
    stats = learner.get_learning_stats()
    
    return {
        "total_events": stats["total_events"],
        "recent_accuracy": stats["recent_accuracy"],
        "accuracy_trend": stats["accuracy_trend"],
        "window_size": stats["window_size"],
        "stage_learning_rates": stats["stage_learning_rates"],
        "stage_performance": stats["stage_performance"]
    }


@router.get("/teams")
async def get_all_teams():
    """获取所有球队"""
    from data.world_cup_2026 import ALL_TEAMS
    
    return {
        "teams": [
            {
                "code": t["code"],
                "name": t["name"],
                "name_cn": t["name_cn"],
                "rank": t["rank"],
                "elo": t["elo"],
                "continent": t["continent"],
                "form": t["form"]
            }
            for t in ALL_TEAMS
        ],
        "total": len(ALL_TEAMS)
    }


@router.get("/health")
async def health_check():
    """健康检查"""
    engine = get_engine_v6()
    
    return {
        "status": "healthy",
        "version": "6.0",
        "features": {
            "p0_optimized": True,
            "feature_engine": "V2",
            "online_learning": "V2",
            "feature_dim": 13,
            "stage_adaptive_lr": True,
            "dynamic_window": True
        }
    }
