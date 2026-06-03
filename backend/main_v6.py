"""
世界杯预测系统 - 主应用 V6
兼容旧API路径 + 新V6功能
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 导入旧的API路由（兼容）
from api.groups import router as groups_router
from api.matches import router as matches_router
from api.simulation import router as simulation_router
from api.history import router as history_router
from api.accuracy import router as accuracy_router
from api.models import router as models_router
from api.learning import router as learning_router

# 导入新的V6 API路由
from api.prediction_v6 import router as prediction_v6_router
from api.training_v2 import router as training_v2_router

# 创建应用
app = FastAPI(
    title="世界杯预测系统 V6",
    description="P0优化版 + 兼容旧API",
    version="6.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册旧API路由（兼容前端）
app.include_router(groups_router)
app.include_router(matches_router)
app.include_router(simulation_router)
app.include_router(history_router)
app.include_router(accuracy_router)
app.include_router(models_router)
app.include_router(learning_router)

# 注册新V6 API路由
app.include_router(prediction_v6_router)
app.include_router(training_v2_router)


@app.get("/")
async def root():
    """API根路径"""
    return {
        "name": "世界杯预测系统",
        "version": "6.0.0",
        "p0_optimized": True,
        "endpoints": {
            "groups": "/api/groups",
            "matches": "/api/matches",
            "simulation": "/api/simulation",
            "history": "/api/history",
            "accuracy": "/api/accuracy",
            "v6_groups": "/api/v6/groups",
            "v6_predict": "/api/v6/predict",
            "training": "/api/training"
        }
    }


@app.on_event("startup")
async def startup():
    """启动时检查训练状态"""
    from services.model_trainer_v2 import get_trainer_v2
    
    print("\n" + "=" * 60)
    print("世界杯预测系统 V6 启动")
    print("=" * 60)
    
    trainer = get_trainer_v2()
    summary = trainer.get_last_training_summary()
    
    if summary.get('has_trained'):
        print("\n📊 发现历史训练记录:")
        for model_name, info in summary.get('models', {}).items():
            print(f"  - {model_name}: 准确率 {info.get('accuracy', 0):.1%}")
        
        # 自动加载模型
        print("\n🔄 自动加载已训练模型...")
        loaded = trainer.load_trained_models()
        print(f"✓ 加载完成: {loaded}")
    else:
        print("\n⚠️  尚未进行模型训练")
        print("💡 请访问 /api/training/start 启动训练")
    
    print("\n" + "=" * 60)
    print("系统就绪，API地址: http://localhost:8012")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    uvicorn.run(
        "main_v6:app",
        host="0.0.0.0",
        port=8012,
        reload=True
    )