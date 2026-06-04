"""模型版本管理API"""
from fastapi import APIRouter, HTTPException
from typing import Dict, List
import os
import json
from datetime import datetime

router = APIRouter(prefix="/api/model-versions", tags=["模型版本"])

MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'models')
VERSION_FILE = os.path.join(MODEL_DIR, 'model_versions.json')


def load_version_info() -> Dict:
    """加载版本信息"""
    if not os.path.exists(VERSION_FILE):
        return {"versions": [], "training_count": 0, "current_version": None}
    
    try:
        with open(VERSION_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"versions": [], "training_count": 0, "current_version": None}


def save_version_info(info: Dict):
    """保存版本信息"""
    os.makedirs(MODEL_DIR, exist_ok=True)
    with open(VERSION_FILE, 'w', encoding='utf-8') as f:
        json.dump(info, f, ensure_ascii=False, indent=2)


@router.get("/list")
async def list_model_versions():
    """
    获取所有模型版本列表
    """
    version_info = load_version_info()
    
    # 检查模型文件是否存在
    versions = []
    for v in version_info.get('versions', []):
        version_id = v.get('id')
        nn_file = os.path.join(MODEL_DIR, f'nn_model_{version_id}.pkl')
        rf_file = os.path.join(MODEL_DIR, f'rf_model_{version_id}.pkl')
        
        v['nn_file_exists'] = os.path.exists(nn_file)
        v['rf_file_exists'] = os.path.exists(rf_file)
        v['is_current'] = version_id == version_info.get('current_version')
        versions.append(v)
    
    return {
        "versions": versions,
        "training_count": version_info.get('training_count', 0),
        "current_version": version_info.get('current_version')
    }


@router.post("/load/{version_id}")
async def load_model_version(version_id: str):
    """
    加载指定版本的模型
    
    Args:
        version_id: 版本ID（如 'v1', 'v2'）
    """
    from services.ensemble_instance import get_ensemble
    
    ensemble = get_ensemble()
    
    # 检查版本是否存在
    version_info = load_version_info()
    version_ids = [v.get('id') for v in version_info.get('versions', [])]
    
    if version_id not in version_ids:
        raise HTTPException(status_code=404, detail=f"版本 {version_id} 不存在")
    
    # 加载模型
    success = ensemble.load_model_version(version_id)
    
    if not success:
        raise HTTPException(status_code=500, detail=f"版本 {version_id} 加载失败")
    
    # 更新当前版本
    version_info['current_version'] = version_id
    save_version_info(version_info)
    
    return {
        "success": True,
        "message": f"已加载模型版本 {version_id}",
        "current_version": version_id
    }


@router.delete("/delete/{version_id}")
async def delete_model_version(version_id: str):
    """
    删除指定版本的模型
    
    Args:
        version_id: 版本ID
    """
    version_info = load_version_info()
    
    # 不能删除当前版本
    if version_id == version_info.get('current_version'):
        raise HTTPException(status_code=400, detail="不能删除当前使用的版本")
    
    # 检查版本是否存在
    version_ids = [v.get('id') for v in version_info.get('versions', [])]
    if version_id not in version_ids:
        raise HTTPException(status_code=404, detail=f"版本 {version_id} 不存在")
    
    # 删除模型文件
    nn_file = os.path.join(MODEL_DIR, f'nn_model_{version_id}.pkl')
    rf_file = os.path.join(MODEL_DIR, f'rf_model_{version_id}.pkl')
    
    deleted_files = []
    if os.path.exists(nn_file):
        os.remove(nn_file)
        deleted_files.append(f'nn_model_{version_id}.pkl')
    if os.path.exists(rf_file):
        os.remove(rf_file)
        deleted_files.append(f'rf_model_{version_id}.pkl')
    
    # 更新版本信息
    version_info['versions'] = [v for v in version_info['versions'] if v.get('id') != version_id]
    save_version_info(version_info)
    
    return {
        "success": True,
        "message": f"已删除版本 {version_id}",
        "deleted_files": deleted_files
    }


@router.get("/compare/{version1}/{version2}")
async def compare_model_versions(version1: str, version2: str):
    """
    对比两个版本的模型
    
    Args:
        version1: 版本1 ID
        version2: 版本2 ID
    """
    version_info = load_version_info()
    versions = {v.get('id'): v for v in version_info.get('versions', [])}
    
    if version1 not in versions:
        raise HTTPException(status_code=404, detail=f"版本 {version1} 不存在")
    if version2 not in versions:
        raise HTTPException(status_code=404, detail=f"版本 {version2} 不存在")
    
    v1 = versions[version1]
    v2 = versions[version2]
    
    return {
        "version1": {
            "id": version1,
            "nn_accuracy": v1.get('nn_accuracy', 0),
            "rf_accuracy": v1.get('rf_accuracy', 0),
            "created_at": v1.get('created_at'),
            "data_source": v1.get('data_source')
        },
        "version2": {
            "id": version2,
            "nn_accuracy": v2.get('nn_accuracy', 0),
            "rf_accuracy": v2.get('rf_accuracy', 0),
            "created_at": v2.get('created_at'),
            "data_source": v2.get('data_source')
        },
        "comparison": {
            "nn_accuracy_diff": v1.get('nn_accuracy', 0) - v2.get('nn_accuracy', 0),
            "rf_accuracy_diff": v1.get('rf_accuracy', 0) - v2.get('rf_accuracy', 0),
            "better_version": version1 if v1.get('nn_accuracy', 0) >= v2.get('nn_accuracy', 0) else version2
        }
    }


@router.get("/stats")
async def get_model_stats():
    """
    获取模型训练统计信息
    """
    version_info = load_version_info()
    versions = version_info.get('versions', [])
    
    if len(versions) == 0:
        return {
            "training_count": 0,
            "current_version": None,
            "best_version": None,
            "avg_nn_accuracy": 0,
            "avg_rf_accuracy": 0
        }
    
    nn_accuracies = [v.get('nn_accuracy', 0) for v in versions]
    rf_accuracies = [v.get('rf_accuracy', 0) for v in versions]
    
    best_version = max(versions, key=lambda v: v.get('nn_accuracy', 0))
    
    return {
        "training_count": version_info.get('training_count', len(versions)),
        "current_version": version_info.get('current_version'),
        "best_version": best_version.get('id'),
        "best_nn_accuracy": best_version.get('nn_accuracy', 0),
        "best_rf_accuracy": best_version.get('rf_accuracy', 0),
        "avg_nn_accuracy": sum(nn_accuracies) / len(nn_accuracies) if nn_accuracies else 0,
        "avg_rf_accuracy": sum(rf_accuracies) / len(rf_accuracies) if rf_accuracies else 0,
        "first_trained": versions[0].get('created_at') if versions else None,
        "last_trained": versions[-1].get('created_at') if versions else None
    }
