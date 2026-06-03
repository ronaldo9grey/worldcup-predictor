"""世界杯预测系统 - 主应用"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import uvicorn

from services.upset_analyzer import PredictionEngine
from services.data_fetcher import MockDataGenerator
from models.schema import (
    MatchWithPrediction, MatchListResponse, PredictionRequest,
    PredictionResponse, TeamStats, StatisticsResponse
)

# 创建应用
app = FastAPI(
    title="世界杯预测系统",
    description="预测比赛结果，识别潜在冷门",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化预测引擎
engine = PredictionEngine()

# 数据存储（生产环境应使用数据库）
matches_data = []
predictions_cache = {}


@app.on_event("startup")
async def startup():
    """启动时加载模拟数据"""
    global matches_data
    matches_data = MockDataGenerator.generate_sample_matches(24)
    print(f"✅ 已加载 {len(matches_data)} 场比赛数据")


@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "世界杯预测系统",
        "version": "1.0.0",
        "endpoints": {
            "matches": "/api/matches",
            "upsets": "/api/upsets",
            "predict": "/api/predict",
            "teams": "/api/teams",
            "stats": "/api/stats"
        }
    }


@app.get("/api/matches", response_model=MatchListResponse)
async def get_matches(
    stage: Optional[str] = Query(None, description="赛事阶段"),
    team: Optional[str] = Query(None, description="球队代码"),
    upcoming_only: bool = Query(True, description="只返回未开始的比赛")
):
    """获取比赛列表"""
    global matches_data
    
    matches = matches_data.copy()
    
    # 过滤
    if stage:
        matches = [m for m in matches if m.get("stage") == stage]
    
    if team:
        matches = [m for m in matches 
                   if m.get("home_team") == team or m.get("away_team") == team]
    
    if upcoming_only:
        matches = [m for m in matches if m.get("status") == "SCHEDULED"]
    
    # 为每场比赛生成预测
    result_matches = []
    upset_count = 0
    
    for match in matches:
        prediction = engine.predict(match)
        
        match_with_pred = MatchWithPrediction(
            match_id=match["match_id"],
            home_team=match["home_team"],
            away_team=match["away_team"],
            match_time=datetime.fromisoformat(match["match_time"]),
            venue=match.get("venue"),
            stage=match.get("stage", "GROUP"),
            status=match.get("status", "SCHEDULED"),
            
            home_team_name=match["home_team_name"],
            away_team_name=match["away_team_name"],
            home_team_rank=match["home_team_rank"],
            away_team_rank=match["away_team_rank"],
            
            home_win_prob=prediction["home_win_prob"],
            draw_prob=prediction["draw_prob"],
            away_win_prob=prediction["away_win_prob"],
            
            upset_score=prediction["upset_score"],
            upset_factors=prediction["upset_factors"],
            is_potential_upset=prediction["is_potential_upset"],
            
            prediction=prediction["prediction"],
            confidence=prediction["confidence"],
        )
        
        if prediction["is_potential_upset"]:
            upset_count += 1
        
        result_matches.append(match_with_pred)
    
    return MatchListResponse(
        matches=result_matches,
        total=len(result_matches),
        upcoming_count=len(result_matches),
        upset_matches=upset_count
    )


@app.get("/api/upsets")
async def get_upset_matches():
    """获取冷门比赛列表"""
    global matches_data
    
    upset_matches = {"high": [], "medium": []}
    
    for match in matches_data:
        prediction = engine.predict(match)
        
        if prediction["upset_score"] >= 50:
            upset_matches["high"].append({
                **match,
                **prediction
            })
        elif prediction["upset_score"] >= 35:
            upset_matches["medium"].append({
                **match,
                **prediction
            })
    
    return {
        "high_upset": sorted(upset_matches["high"], 
                            key=lambda x: x["upset_score"], reverse=True),
        "medium_upset": sorted(upset_matches["medium"], 
                              key=lambda x: x["upset_score"], reverse=True),
        "summary": {
            "high_count": len(upset_matches["high"]),
            "medium_count": len(upset_matches["medium"])
        }
    }


@app.post("/api/predict", response_model=PredictionResponse)
async def predict_match(request: PredictionRequest):
    """预测指定比赛"""
    teams = MockDataGenerator.get_team_list()
    
    home_team = next((t for t in teams if t["fifa_code"] == request.home_team), None)
    away_team = next((t for t in teams if t["fifa_code"] == request.away_team), None)
    
    if not home_team or not away_team:
        raise HTTPException(status_code=404, detail="球队不存在")
    
    match_data = {
        "home_team": request.home_team,
        "away_team": request.away_team,
        "home_team_name": home_team["name"],
        "away_team_name": away_team["name"],
        "home_team_rank": home_team["fifa_rank"],
        "away_team_rank": away_team["fifa_rank"],
        "home_elo": home_team["elo_rating"],
        "away_elo": away_team["elo_rating"],
        "home_recent_form": home_team["recent_form"],
        "away_recent_form": away_team["recent_form"],
        "is_neutral": True,
        "stage": "GROUP",
    }
    
    prediction = engine.predict(match_data)
    
    match_pred = MatchWithPrediction(
        match_id=f"CUSTOM_{request.home_team}_{request.away_team}",
        home_team=request.home_team,
        away_team=request.away_team,
        match_time=datetime.now(),
        venue=None,
        stage="CUSTOM",
        status="CUSTOM",
        
        home_team_name=home_team["name"],
        away_team_name=away_team["name"],
        home_team_rank=home_team["fifa_rank"],
        away_team_rank=away_team["fifa_rank"],
        
        home_win_prob=prediction["home_win_prob"],
        draw_prob=prediction["draw_prob"],
        away_win_prob=prediction["away_win_prob"],
        
        upset_score=prediction["upset_score"],
        upset_factors=prediction["upset_factors"],
        is_potential_upset=prediction["is_potential_upset"],
        
        prediction=prediction["prediction"],
        confidence=prediction["confidence"],
    )
    
    home_stats = TeamStats(**home_team, goals_scored_last5=0, goals_conceded_last5=0, win_rate=0.5, draw_rate=0.2, 
                          loss_rate=0.3, updated_at=datetime.now())
    away_stats = TeamStats(**away_team, goals_scored_last5=0, goals_conceded_last5=0, win_rate=0.5, draw_rate=0.2,
                          loss_rate=0.3, updated_at=datetime.now())
    
    return PredictionResponse(
        home_team=home_stats,
        away_team=away_stats,
        prediction=match_pred,
        analysis={
            "elo_diff": abs(home_team["elo_rating"] - away_team["elo_rating"]),
            "rank_diff": abs(home_team["fifa_rank"] - away_team["fifa_rank"]),
            "form_comparison": f"{home_team['recent_form']} vs {away_team['recent_form']}",
            "upset_analysis": prediction["upset_factors"],
        }
    )


@app.get("/api/teams")
async def get_teams():
    """获取参赛球队列表"""
    teams = MockDataGenerator.get_team_list()
    return {
        "teams": teams,
        "total": len(teams)
    }


@app.get("/api/team/{team_code}")
async def get_team_detail(team_code: str):
    """获取球队详情"""
    teams = MockDataGenerator.get_team_list()
    team = next((t for t in teams if t["fifa_code"] == team_code), None)
    
    if not team:
        raise HTTPException(status_code=404, detail="球队不存在")
    
    # 获取该球队的比赛
    team_matches = []
    for match in matches_data:
        if match.get("home_team") == team_code or match.get("away_team") == team_code:
            prediction = engine.predict(match)
            team_matches.append({
                **match,
                **prediction
            })
    
    return {
        "team": team,
        "matches": team_matches
    }


@app.get("/api/stats", response_model=StatisticsResponse)
async def get_statistics():
    """获取预测统计"""
    # 模拟统计（生产环境应从数据库读取）
    return StatisticsResponse(
        total_predictions=48,
        correct_predictions=32,
        accuracy_rate=0.667,
        upset_predictions=12,
        upset_correct=5,
        upset_accuracy=0.417,
        by_stage={
            "GROUP": {"total": 32, "correct": 22, "accuracy": 0.688},
            "ROUND_OF_16": {"total": 8, "correct": 6, "accuracy": 0.75},
            "QUARTER_FINAL": {"total": 4, "correct": 2, "accuracy": 0.50},
            "SEMI_FINAL": {"total": 2, "correct": 1, "accuracy": 0.50},
            "FINAL": {"total": 2, "correct": 1, "accuracy": 0.50}
        }
    )


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8011)
