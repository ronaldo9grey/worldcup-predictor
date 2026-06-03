"""比赛详情API路由"""
from fastapi import APIRouter, Depends
from typing import Dict, Any

from services.prediction_engine_v3 import create_prediction_engine, PredictionEngineV3
from providers import H2HProvider, TeamValueProvider, WCHistoryProvider, FormProvider
from core.database import get_database
from data.world_cup_2026 import GROUPS

router = APIRouter(prefix="/api/groups", tags=["比赛详情"])


def get_engine_with_providers() -> PredictionEngineV3:
    """获取带所有数据提供者的预测引擎"""
    db = get_database()
    
    providers = {
        "h2h": H2HProvider(db),
        "value": TeamValueProvider(db),
        "wc_history": WCHistoryProvider(db),
        "form": FormProvider(db)
    }
    
    return create_prediction_engine(database=db, providers=providers)


@router.get("/{group_name}/match/{match_idx}")
async def get_match_detail(
    group_name: str,
    match_idx: int,
    engine: PredictionEngineV3 = Depends(get_engine_with_providers)
) -> Dict[str, Any]:
    """获取比赛详情（含所有因子）"""
    teams = GROUPS.get(group_name.upper())
    if not teams or match_idx < 0 or match_idx >= 6:
        return {"error": "无效请求"}
    
    # 小组赛对阵组合
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    i, j = pairs[match_idx]
    home, away = teams[i], teams[j]
    
    # 预测
    pred = engine.predict_match(home, away, stage="GROUP", is_neutral=True)
    
    return {
        "match": {
            "home": {
                "code": home["code"],
                "name": home["name"],
                "name_cn": home["name_cn"],
                "rank": home["rank"],
                "elo": home["elo"],
                "form": home["form"],
                "continent": home["continent"]
            },
            "away": {
                "code": away["code"],
                "name": away["name"],
                "name_cn": away["name_cn"],
                "rank": away["rank"],
                "elo": away["elo"],
                "form": away["form"],
                "continent": away["continent"]
            }
        },
        "prediction": {
            "home_win_prob": pred.home_win_prob,
            "draw_prob": pred.draw_prob,
            "away_win_prob": pred.away_win_prob,
            "result": pred.prediction,
            "confidence": pred.confidence
        },
        "factors": [
            {
                "key": f.key,
                "name": f.name,
                "icon": f.icon,
                "color": f.color,
                "desc": f.desc,
                "weight": f.weight,
                "contribution": f.contribution,
                "weighted_contribution": f.contribution * f.weight,
                "source": f.source
            }
            for f in pred.factors
        ],
        "upset": {
            "is_upset": pred.is_upset,
            "score": pred.upset_score,
            "factors": pred.upset_factors
        }
    }