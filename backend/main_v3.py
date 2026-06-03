"""
世界杯预测系统 V3 - 主入口

架构：高内聚、松耦合
- core/      : 基础设施（数据库、缓存）
- providers/ : 数据提供者（可插拔）
- services/  : 业务逻辑（预测引擎、模拟）
- api/       : API路由（按功能拆分）
- data/      : 静态数据和初始化
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from core.database import get_database
from core.cache import get_cache
from data.init_data import init_database
from api.groups import router as groups_router
from api.matches import router as matches_router
from api.simulation import router as simulation_router
from api.history import router as history_router
from api.user import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    db = get_database()
    init_database(db)
    print("⚽ 世界杯预测系统 V3 启动完成！")
    yield
    # 关闭时清理
    print("👋 世界杯预测系统 V3 关闭")


# 创建应用
app = FastAPI(
    title="世界杯预测系统",
    description="预测比赛结果，识别潜在冷门",
    version="3.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(groups_router)
app.include_router(matches_router)
app.include_router(simulation_router)
app.include_router(history_router)
app.include_router(user_router)


# ========== 基础端点 ==========

@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "世界杯预测系统",
        "version": "3.0.0",
        "features": [
            "小组赛预测", "对阵图模拟", "冷门预警",
            "历史交锋", "球队身价", "世界杯经验",
            "蒙特卡洛模拟", "数据库持久化"
        ],
        "endpoints": {
            "groups": "/api/groups",
            "match_detail": "/api/groups/{group}/match/{idx}",
            "simulate": "/api/simulate",
            "monte_carlo": "/api/simulate/monte-carlo",
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "ok", "version": "3.0.0"}


# 兼容旧版API路由（重定向到新路由）
@app.get("/api/algorithm")
async def get_algorithm():
    """算法信息"""
    return {
        "name": "世界杯预测引擎 V3",
        "version": "3.0.0",
        "simulation_modes": {
            "strict": "严谨模式-选概率最高",
            "prob": "概率模式-采样模拟"
        },
        "factors": [
            {"key": "elo_diff", "name": "Elo实力差", "weight": 0.25, "icon": "📊"},
            {"key": "form_diff", "name": "状态差异", "weight": 0.20, "icon": "📈"},
            {"key": "stage_factor", "name": "赛事阶段", "weight": 0.12, "icon": "🏆"},
            {"key": "rank_gap", "name": "排名差距", "weight": 0.08, "icon": "🏅"},
            {"key": "home_advantage", "name": "主场优势", "weight": 0.10, "icon": "🏟️"},
            {"key": "continent_factor", "name": "洲际因素", "weight": 0.05, "icon": "🌍"},
            {"key": "h2h", "name": "历史交锋", "weight": 0.08, "icon": "⚔️"},
            {"key": "team_value", "name": "球队身价", "weight": 0.07, "icon": "💰"},
            {"key": "wc_experience", "name": "世界杯经验", "weight": 0.05, "icon": "🏆"},
        ],
        "data_sources": ["Elo Rating", "FIFA排名", "近期状态", "历史交锋", "球队身价", "世界杯底蕴"]
    }


@app.get("/api/teams")
async def get_teams():
    """获取参赛球队列表"""
    db = get_database()
    teams = db.get_all_teams()
    return {"teams": teams, "total": len(teams)}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8011)
