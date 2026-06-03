"""
API路由 - 模型训练 V2
功能：
1. 启动训练
2. 获取训练进度（实时）
3. 获取训练历史
4. 加载已训练模型
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
import sys

sys.path.append('/var/www/worldcup-predictor/backend')

from services.model_trainer_v2 import get_trainer_v2

router = APIRouter(prefix="/api/training", tags=["training"])


# ========== 请求模型 ==========

class StartTrainingRequest(BaseModel):
    """开始训练请求"""
    nn_epochs: int = 100
    rf_estimators: int = 100
    train_all: bool = True


class LoadModelsRequest(BaseModel):
    """加载模型请求"""
    models: List[str] = ["neural_network", "random_forest"]


# ========== 响应模型 ==========

class TrainingProgressResponse(BaseModel):
    """训练进度响应"""
    model_name: str
    current_epoch: int
    total_epochs: int
    current_loss: float
    best_loss: float
    accuracy: float
    status: str
    message: str
    elapsed_seconds: float


class TrainingResultResponse(BaseModel):
    """训练结果响应"""
    model_name: str
    training_time: str
    epochs: int
    final_loss: float
    final_accuracy: float
    validation_accuracy: float
    status: str
    message: str
    model_path: str


class TrainingSummaryResponse(BaseModel):
    """训练摘要响应"""
    has_trained: bool
    message: str = ""
    models: Optional[Dict] = None
    best_model: Optional[str] = None
    best_accuracy: Optional[float] = None


# ========== API端点 ==========

@router.post("/start", response_model=Dict)
async def start_training(request: StartTrainingRequest, background_tasks: BackgroundTasks):
    """
    启动模型训练（后台运行）
    
    返回训练任务ID，可通过 /progress 接口查询进度
    """
    trainer = get_trainer_v2()
    
    # 检查是否正在训练
    progress = trainer.get_training_progress()
    for model_name, prog in progress.items():
        if prog and prog.get('status') == 'training':
            return {
                'status': 'already_training',
                'message': f'{model_name} 正在训练中',
                'progress': prog
            }
    
    # 后台启动训练
    if request.train_all:
        background_tasks.add_task(
            trainer.train_all_models,
            nn_epochs=request.nn_epochs,
            rf_estimators=request.rf_estimators
        )
    else:
        # 可以单独训练某个模型
        pass
    
    return {
        'status': 'started',
        'message': '训练任务已启动',
        'config': {
            'nn_epochs': request.nn_epochs,
            'rf_estimators': request.rf_estimators
        }
    }


@router.get("/progress", response_model=Dict)
async def get_progress(model_name: Optional[str] = None):
    """
    获取训练进度（实时）
    
    - 不指定 model_name 返回所有模型进度
    - 指定 model_name 返回特定模型进度
    """
    trainer = get_trainer_v2()
    progress = trainer.get_training_progress(model_name)
    
    if model_name and not progress:
        raise HTTPException(status_code=404, detail=f"模型 {model_name} 无训练进度")
    
    return {
        'progress': progress,
        'timestamp': trainer.training_results.get('last_updated', '') if hasattr(trainer, 'training_results') else ''
    }


@router.get("/results", response_model=Dict)
async def get_results(model_name: Optional[str] = None):
    """
    获取训练结果（历史）
    
    - 不指定 model_name 返回所有模型结果
    - 指定 model_name 返回特定模型结果
    """
    trainer = get_trainer_v2()
    results = trainer.get_training_results(model_name)
    
    if model_name and not results:
        raise HTTPException(status_code=404, detail=f"模型 {model_name} 无训练结果")
    
    return {
        'results': results,
        'total_models': len(results) if isinstance(results, dict) else 1
    }


@router.get("/summary", response_model=TrainingSummaryResponse)
async def get_summary():
    """
    获取上次训练摘要
    
    返回：
    - 是否有训练记录
    - 各模型准确率
    - 最佳模型
    """
    trainer = get_trainer_v2()
    summary = trainer.get_last_training_summary()
    
    return TrainingSummaryResponse(**summary)


@router.post("/load", response_model=Dict)
async def load_models(request: LoadModelsRequest):
    """
    加载已训练的模型
    
    从磁盘加载上次训练的模型
    """
    trainer = get_trainer_v2()
    loaded = trainer.load_trained_models()
    
    return {
        'loaded': loaded,
        'message': f"成功加载 {sum(loaded.values())} 个模型"
    }


@router.get("/status", response_model=Dict)
async def get_status():
    """
    获取训练系统状态
    
    返回：
    - 是否有训练记录
    - 模型是否已加载
    - 当前训练状态
    """
    trainer = get_trainer_v2()
    
    summary = trainer.get_last_training_summary()
    progress = trainer.get_training_progress()
    
    # 检查模型是否加载
    models_loaded = {
        'neural_network': trainer.nn_model is not None,
        'random_forest': trainer.rf_model is not None
    }
    
    # 检查是否正在训练
    is_training = any(
        p.get('status') == 'training' 
        for p in progress.values() if p
    )
    
    return {
        'has_trained': summary.get('has_trained', False),
        'models_loaded': models_loaded,
        'is_training': is_training,
        'current_progress': progress,
        'last_training': summary.get('models', {})
    }


@router.delete("/reset", response_model=Dict)
async def reset_training():
    """
    重置训练状态
    
    清除训练进度和结果（不清除已保存的模型）
    """
    trainer = get_trainer_v2()
    
    # 清除进度
    trainer.current_progress = {}
    trainer._save_progress()
    
    return {
        'status': 'reset',
        'message': '训练状态已重置'
    }
