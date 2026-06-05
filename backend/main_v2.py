"""世界杯预测系统 v2.2 - 完整对阵图"""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict
import os

from services.prediction_engine_v2 import PredictionEngineV2
from services.strict_simulation import StrictSimulationEngine
from services.prediction_engine_v4 import create_v4_engine
from services.ensemble_instance import get_ensemble
from data.world_cup_2026 import GROUPS, get_all_teams, get_team_lookup, get_groups as get_groups_dict
from api.user import router as user_router
from api.accuracy import router as accuracy_router
from api.group_simulation import router as group_simulation_router
from api.groups import router as groups_router
from api.auto_verify import router as auto_verify_router
from api.training import router as training_router
from api.calculation import router as calculation_router
from api.history import router as history_router
from api.models import router as models_router
from api.learning import router as learning_router
from api.data_extension import router as data_extension_router
from api.leaderboard import router as leaderboard_router
from api.share import router as share_router
from api.bayesian import router as bayesian_router
from api.model_versions import router as model_versions_router
from api.data_service_api import router as data_service_router

# 使用完整的队伍信息（包含所有字段）
GROUPS_FULL = get_groups_dict()

app = FastAPI(title="世界杯预测系统 v2.3", version="2.3.0")

# 挂载API路由
app.include_router(user_router)
app.include_router(accuracy_router)
app.include_router(group_simulation_router)
app.include_router(groups_router)  # 小组赛详情
app.include_router(auto_verify_router)
app.include_router(training_router)
app.include_router(calculation_router)
app.include_router(history_router)
app.include_router(models_router)
app.include_router(learning_router)
app.include_router(data_extension_router)
app.include_router(leaderboard_router)
app.include_router(share_router)
app.include_router(bayesian_router)  # 贝叶斯可视化扩展
app.include_router(model_versions_router)  # 模型版本管理
app.include_router(data_service_router)  # 数据服务API

# 静态文件服务（前端）
frontend_dist = "/var/www/worldcup-predictor/frontend/dist"
if os.path.exists(frontend_dist):
    app.mount("/worldcup", StaticFiles(directory=frontend_dist, html=True), name="static")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

engine = PredictionEngineV2()


@app.get("/")
async def root():
    return {
    "name": "世界杯预测系统",
    "version": "2.3.0",
    "features": ["小组赛", "对阵图", "严谨模拟", "算法揭秘", "神经网络", "随机森林", "模型集成", "在线学习", "伤病追踪", "赔率校准", "情感分析"]
}


# 删除旧的路由定义，使用 groups.py 的路由


# 删除旧的 get_group_detail，由 groups.py 提供


# 删除旧的 get_match_detail，由 groups.py 提供
    bayesian = pred.bayesian_pred
# get_match_detail 函数已删除，由 groups.py 提供


@app.get("/api/simulate")
async def simulate_tournament(mode: str = Query("strict", description="strict或prob")):
    """一键模拟"""
    groups_dict = get_groups_dict()  # 获取字典格式的分组数据
    sim_engine = StrictSimulationEngine(groups_dict, get_team_lookup())
    return sim_engine.simulate_tournament(deterministic=(mode == "strict"))


@app.get("/api/algorithm")
async def get_algorithm():
    return {
        "name": "世界杯预测引擎 v2.4",
        "simulation_modes": {"strict": "严谨模式-选概率最高", "prob": "概率模式-采样模拟"},
        "factors": [
            {"key": "elo_diff", "name": "Elo实力差", "weight": 0.258, "icon": "📊", "description": "两队Elo积分差异，反映历史实力", "how_it_works": "Elo差值÷300，归一化到[-1,1]"},
            {"key": "form_diff", "name": "状态差异", "weight": 0.165, "icon": "📈", "description": "近期比赛状态对比", "how_it_works": "最近10场比赛胜率差值"},
            {"key": "stage_factor", "name": "赛事阶段", "weight": 0.138, "icon": "🏆", "description": "小组赛/淘汰赛影响", "how_it_works": "淘汰赛强队更有动力"},
            {"key": "rank_gap", "name": "排名差距", "weight": 0.092, "icon": "🏅", "description": "FIFA世界排名差异", "how_it_works": "排名差÷50，归一化到[-1,1]"},
            {"key": "squad_strength", "name": "球员阵容", "weight": 0.110, "icon": "👥", "description": "球队阵容实力评估", "how_it_works": "核心球员能力值+明星效应"},
            {"key": "home_advantage", "name": "主场优势", "weight": 0.074, "icon": "🏟️", "description": "主场作战优势", "how_it_works": "东道主+0.2，其他+0.05"},
            {"key": "coach_rating", "name": "教练能力", "weight": 0.074, "icon": "👨‍🏫", "description": "教练执教水平", "how_it_works": "胜率+大赛经验+战术能力"},
            {"key": "h2h_record", "name": "历史交锋", "weight": 0.064, "icon": "📜", "description": "历史对战记录", "how_it_works": "过去10场交锋胜率"},
            {"key": "wc_experience", "name": "世界杯经验", "weight": 0.064, "icon": "🌍", "description": "世界杯参赛经验", "how_it_works": "参赛次数+最佳成绩"},
            {"key": "venue_factor", "name": "场地影响", "weight": 0.046, "icon": "🏟️", "description": "比赛场地条件", "how_it_works": "海拔+温度+湿度影响"},
            {"key": "continent_factor", "name": "洲际因素", "weight": 0.046, "icon": "🌎", "description": "洲际比赛适应性", "how_it_works": "同洲+0.1，跨洲-0.05"},
            {"key": "injury_impact", "name": "伤病影响", "weight": 0.060, "icon": "🏥", "description": "核心球员伤病", "how_it_works": "伤病严重度×核心球员系数"},
            {"key": "sentiment", "name": "社交情感", "weight": 0.040, "icon": "💬", "description": "球迷情绪分析", "how_it_works": "社交媒体信心指数"},
            {"key": "odds_calibration", "name": "赔率校准", "weight": 0.030, "icon": "💰", "description": "市场赔率参考", "how_it_works": "博彩公司共识概率校准"},
        ],
        "formula": "预测概率 = Σ(因子值 × 因子权重)",
        "probability": "P(主胜), P(平), P(客胜) = Softmax(预测概率)",
        "cold_warm": [
            "❄️ Elo差距<50但排名差>20（强队低估）",
            "❄️ 亚洲/非洲球队对阵欧洲强队（历史爆冷多）",
            "❄️ 卫冕冠军小组赛首战（慢热传统）",
            "❄️ 淘汰赛0-0平局后点球大战（门神对决）",
            "❄️ 主场球迷90%以上支持（压力过大）",
            "🔥 卫冕冠军对阵东道主（历史不友好）",
            "🔥 小组赛末轮已出线球队轮换（战意不足）",
            "🔥 核心球员赛前确认伤缺（实力打折）",
        ]
    }


@app.get("/health")
async def health():
    return {"status": "ok", "version": "2.2.0"}


# 用户数据库初始化
from core.database import get_database

@app.on_event("startup")
async def startup_event():
    db = get_database()
    # 确保数据库表已创建
    from repositories.user_repo import UserRepository
    UserRepository(db.db_path)
    
    # 预计算小组出线概率（后台异步执行，不阻塞启动）
    from api.group_simulation import precompute_all_qualifications
    import asyncio
    asyncio.create_task(precompute_all_qualifications())
    
    # 自动训练模型（后台异步执行）
    asyncio.create_task(train_models_async())


async def train_models_async():
    """后台自动训练模型"""
    import time
    import asyncio
    
    await asyncio.sleep(5)  # 等待服务启动完成
    
    try:
        ensemble = get_ensemble()
        print(f"🤖 检查模型状态: nn_trained={ensemble.nn_trained}, rf_trained={ensemble.rf_trained}")
        
        # 始终调用初始化（会从缓存加载或重新训练）
        print("🤖 开始初始化模型...")
        start_time = time.time()
        status = ensemble.initialize_models(force_retrain=False)
        elapsed = time.time() - start_time
        print(f"✨ 模型初始化完成，耗时 {elapsed:.2f} 秒")
        print(f"   神经网络: {status.get('neural_network', 'unknown')}")
        print(f"   随机森林: {status.get('random_forest', 'unknown')}")
        print(f"   最终状态: nn_trained={ensemble.nn_trained}, rf_trained={ensemble.rf_trained}")
    except Exception as e:
        import traceback
        print(f"❌ 模型初始化失败: {e}")
        traceback.print_exc()