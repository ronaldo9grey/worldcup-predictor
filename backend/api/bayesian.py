"""
贝叶斯更新过程可视化API - 展示贝叶斯推断的详细步骤
这是训练过程可视化的扩展，不影响原有预测逻辑
"""
from fastapi import APIRouter, Query
from typing import Dict, Any, Optional

from services.bayesian_visualizer import get_bayesian_visualizer
from services.prediction_engine_v6 import get_engine_v6
from data.world_cup_2026 import get_team_lookup, GROUPS

router = APIRouter(prefix="/api/bayesian", tags=["贝叶斯可视化"])


@router.get("/process")
async def get_bayesian_process(
    home_code: str = Query(..., description="主队代码，如ARG"),
    away_code: str = Query(..., description="客队代码，如FRA"),
    stage: str = Query("GROUP", description="比赛阶段：GROUP/R16/QF/SF/FI")
) -> Dict[str, Any]:
    """
    获取完整的贝叶斯更新过程
    
    展示5个步骤：
    1. 获取先验概率（历史统计）
    2. 获取模型预测（权重计算）
    3. 贝叶斯更新（加权平均）
    4. 计算置信区间（不确定性量化）
    5. 输出预测结论
    
    Args:
        home_code: 主队代码
        away_code: 客队代码
        stage: 比赛阶段
    """
    visualizer = get_bayesian_visualizer()
    team_lookup = get_team_lookup()
    
    # 获取球队信息
    home = team_lookup.get(home_code, {"code": home_code, "name_cn": home_code, "elo": 1500})
    away = team_lookup.get(away_code, {"code": away_code, "name_cn": away_code, "elo": 1500})
    
    # 获取预测引擎的基础概率
    engine = get_engine_v6()
    prediction = engine.predict_match(home_code, away_code, stage)
    
    # 获取特征数据（用于计算elo_diff）
    features = prediction.features.to_dict()
    
    # 获取贝叶斯更新过程
    steps = visualizer.get_bayesian_update_process(
        home_prob=prediction.home_win_prob,
        draw_prob=prediction.draw_prob,
        away_prob=prediction.away_win_prob,
        stage=stage,
        elo_diff=features.get("elo_diff", 0.0),
        home_name=home.get("name_cn", home_code),
        away_name=away.get("name_cn", away_code)
    )
    
    return {
        "match_info": {
            "home": {
                "code": home_code,
                "name": home.get("name_cn", home_code),
                "elo": home.get("elo", 1500),
                "rank": home.get("rank", 50)
            },
            "away": {
                "code": away_code,
                "name": away.get("name_cn", away_code),
                "elo": away.get("elo", 1500),
                "rank": away.get("rank", 50)
            },
            "stage": stage,
            "stage_cn": visualizer._get_stage_cn(stage)
        },
        "total_steps": len(steps),
        "steps": [
            {
                "step": s.step,
                "title": s.title,
                "description": s.description,
                "input": s.input_data,
                "output": s.output_data,
                "formula": s.formula,
                "visualization": s.visualization
            }
            for s in steps
        ],
        "final_result": {
            "prediction": prediction.prediction,
            "confidence_level": prediction.confidence_level,
            "confidence_value": prediction.confidence_value,
            "probabilities": {
                "home_win": round(prediction.home_win_prob, 3),
                "draw": round(prediction.draw_prob, 3),
                "away_win": round(prediction.away_win_prob, 3)
            }
        }
    }


@router.get("/config")
async def get_bayesian_config() -> Dict[str, Any]:
    """
    获取贝叶斯配置参数
    
    解释贝叶斯模型的参数含义和核心理念
    """
    visualizer = get_bayesian_visualizer()
    return visualizer.get_bayesian_config()


@router.get("/prior-source")
async def get_prior_source() -> Dict[str, Any]:
    """
    获取先验概率数据来源
    
    展示历史世界杯统计如何转化为先验概率
    """
    visualizer = get_bayesian_visualizer()
    return visualizer.get_prior_source_all()


@router.get("/prior-source/{stage}")
async def get_prior_source_by_stage(stage: str) -> Dict[str, Any]:
    """
    获取指定阶段的先验概率来源
    
    Args:
        stage: 比赛阶段（GROUP/R16/QF/SF/FI）
    """
    visualizer = get_bayesian_visualizer()
    all_source = visualizer.get_prior_source_all()
    
    stage_data = all_source["source"].get(stage)
    if not stage_data:
        return {
            "error": "未找到该阶段数据",
            "available_stages": list(all_source["source"].keys())
        }
    
    return {
        "stage": stage,
        "stage_cn": visualizer._get_stage_cn(stage),
        "data": stage_data
    }


@router.get("/comparison")
async def get_prior_model_comparison(
    stage: str = Query("GROUP", description="比赛阶段")
) -> Dict[str, Any]:
    """
    展示先验概率与典型模型预测的对比
    
    用于理解贝叶斯更新如何平衡历史经验和模型预测
    """
    visualizer = get_bayesian_visualizer()
    prior_data = visualizer.PRIOR_SOURCE.get(stage, visualizer.PRIOR_SOURCE["GROUP"])
    
    # 典型场景对比
    scenarios = [
        {
            "name": "强队碾压",
            "description": "强队vs弱队，模型预测主胜80%",
            "model_probs": {"HOME_WIN": 0.80, "DRAW": 0.10, "AWAY_WIN": 0.10},
            "prior_probs": {
                "HOME_WIN": prior_data["statistics"]["HOME_WIN"]["percentage"] / 100,
                "DRAW": prior_data["statistics"]["DRAW"]["percentage"] / 100,
                "AWAY_WIN": prior_data["statistics"]["AWAY_WIN"]["percentage"] / 100
            }
        },
        {
            "name": "势均力敌",
            "description": "两队实力接近，模型预测均匀分布",
            "model_probs": {"HOME_WIN": 0.35, "DRAW": 0.30, "AWAY_WIN": 0.35},
            "prior_probs": {
                "HOME_WIN": prior_data["statistics"]["HOME_WIN"]["percentage"] / 100,
                "DRAW": prior_data["statistics"]["DRAW"]["percentage"] / 100,
                "AWAY_WIN": prior_data["statistics"]["AWAY_WIN"]["percentage"] / 100
            }
        },
        {
            "name": "冷门预警",
            "description": "模型预测强队胜，但先验暗示冷门可能",
            "model_probs": {"HOME_WIN": 0.55, "DRAW": 0.20, "AWAY_WIN": 0.25},
            "prior_probs": {
                "HOME_WIN": prior_data["statistics"]["HOME_WIN"]["percentage"] / 100,
                "DRAW": prior_data["statistics"]["DRAW"]["percentage"] / 100,
                "AWAY_WIN": prior_data["statistics"]["AWAY_WIN"]["percentage"] / 100
            }
        }
    ]
    
    # 计算各场景的后验概率
    model_strength = visualizer.BAYESIAN_CONFIG["model_strength"]
    prior_strength = visualizer.BAYESIAN_CONFIG["prior_strength"]
    
    results = []
    for scenario in scenarios:
        model = scenario["model_probs"]
        prior = scenario["prior_probs"]
        
        post_home = model_strength * model["HOME_WIN"] + prior_strength * prior["HOME_WIN"]
        post_draw = model_strength * model["DRAW"] + prior_strength * prior["DRAW"]
        post_away = model_strength * model["AWAY_WIN"] + prior_strength * prior["AWAY_WIN"]
        
        total = post_home + post_draw + post_away
        post_home /= total
        post_draw /= total
        post_away /= total
        
        results.append({
            "name": scenario["name"],
            "description": scenario["description"],
            "model_probs": model,
            "prior_probs": prior,
            "posterior_probs": {
                "HOME_WIN": round(post_home, 3),
                "DRAW": round(post_draw, 3),
                "AWAY_WIN": round(post_away, 3)
            },
            "change": {
                "HOME_WIN": round(post_home - model["HOME_WIN"], 3),
                "DRAW": round(post_draw - model["DRAW"], 3),
                "AWAY_WIN": round(post_away - model["AWAY_WIN"], 3)
            },
            "interpretation": _get_interpretation(scenario["name"], model, {"HOME_WIN": post_home, "DRAW": post_draw, "AWAY_WIN": post_away})
        })
    
    return {
        "stage": stage,
        "stage_cn": visualizer._get_stage_cn(stage),
        "prior_source": prior_data["data_source"],
        "weights": {
            "model": model_strength,
            "prior": prior_strength
        },
        "scenarios": results,
        "key_insight": "贝叶斯更新会'修正'极端预测，使其更接近历史经验"
    }


def _get_interpretation(name: str, model: Dict, posterior: Dict) -> str:
    """获取场景解释"""
    if name == "强队碾压":
        return "模型预测80%主胜，但历史先验拉低到约75%，防止过度自信"
    elif name == "势均力敌":
        return "模型预测均匀，贝叶斯更新保持均匀，符合历史规律"
    elif name == "冷门预警":
        return "模型预测55%主胜，先验让客胜概率有所保留，提供冷门预警"
    return ""


@router.get("/explain")
async def get_bayesian_explanation() -> Dict[str, Any]:
    """
    贝叶斯推断原理解释
    
    以通俗语言解释贝叶斯推断在足球预测中的应用
    """
    return {
        "title": "贝叶斯推断在足球预测中的应用",
        "core_formula": {
            "symbol": "P(结果|数据) ∝ P(数据|结果) × P(结果)",
            "meaning": "后验概率 ∝ 似然 × 先验概率",
            "simple": "结合历史经验（先验）和当前分析（似然），得出更可靠的判断（后验）"
        },
        "analogy": {
            "title": "通俗类比",
            "example": "假设你要预测阿根廷vs法国的比赛结果",
            "steps": [
                "先验知识：历史世界杯决赛，强队获胜概率约50%",
                "当前分析：阿根廷Elo略高，状态好，模型预测主胜55%",
                "贝叶斯更新：结合两者，得出后验概率约53%",
                "置信区间：考虑不确定性，预测区间[45%, 60%]"
            ]
        },
        "advantages": [
            {
                "point": "避免过度自信",
                "example": "模型预测强队必胜(90%)，但历史告诉我们冷门会发生，贝叶斯更新会'降温'"
            },
            {
                "point": "量化不确定性",
                "example": "不只是说'主队会赢'，而是说'主队有53%概率获胜，置信区间[45%, 60%]'"
            },
            {
                "point": "历史经验融入",
                "example": "小组赛冷门多，淘汰赛强队稳，这些历史规律会自然影响预测"
            },
            {
                "point": "持续学习",
                "example": "世界杯进行中，可以更新先验概率，让预测越来越准确"
            }
        ],
        "limitations": [
            "先验概率依赖历史数据，可能不完全适用于2026世界杯",
            "无法预测极端冷门（如沙特2-1阿根廷）",
            "置信区间是近似计算，非精确概率分布"
        ],
        "implementation": {
            "model_strength": 0.7,
            "prior_strength": 0.3,
            "rationale": "模型预测权重较高(70%)，但历史经验(30%)提供修正参考"
        }
    }