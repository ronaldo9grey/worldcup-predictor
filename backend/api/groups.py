"""
小组赛API路由 - 优化版
核心原则：预测数据立即返回，实时数据异步加载
"""
from fastapi import APIRouter, BackgroundTasks
from typing import Dict, Any, List
import asyncio
import logging
from datetime import datetime, timedelta

from services.data_service import get_data_service
from services.ensemble_instance import get_ensemble
from data.world_cup_2026 import get_groups as get_groups_dict, get_team_lookup, generate_match_schedule

logger = logging.getLogger(__name__)

GROUPS = get_groups_dict()

# 预测结果缓存
_prediction_cache: Dict[str, Dict] = {}
_cache_timestamp: Dict[str, datetime] = {}
CACHE_TTL = timedelta(hours=1)

# 实时数据缓存（单独管理）
_realtime_cache: Dict[str, Dict] = {}
_realtime_timestamp: Dict[str, datetime] = {}
REALTIME_CACHE_TTL = timedelta(minutes=5)  # 实时数据缓存5分钟

router = APIRouter(prefix="/api/groups", tags=["小组赛"])


@router.get("/static")
async def get_groups_static() -> Dict[str, Any]:
    """
    获取小组静态信息（队伍列表）
    不包含预测数据，用于快速显示小组卡片预览
    """
    from data.world_cup_2026 import GROUPS, get_team_lookup
    
    team_lookup = get_team_lookup()
    
    groups_data = {}
    for group_name, codes in GROUPS.items():
        teams = []
        for code in codes:
            team = team_lookup.get(code, {})
            teams.append({
                "code": code,
                "name_cn": team.get("name_cn", code),
                "rank": team.get("rank", 50),
                "flag": f"https://flagcdn.com/w40/{code.lower()}.png"
            })
        groups_data[group_name] = teams
    
    return {
        "groups": groups_data
    }


@router.get("")
async def get_groups() -> Dict[str, Any]:
    """获取所有小组信息"""
    ds = get_data_service()
    
    # 从数据服务获取球队信息
    all_teams = await ds.get_all_teams()
    groups_data = await ds.get_groups()
    
    return {
        "groups": [
            {
                "group": gname,
                "teams": [
                    {
                        "code": t.get("code"),
                        "name": t.get("name"),
                        "name_cn": t.get("name_cn"),
                        "rank": t.get("rank"),
                        "elo": t.get("elo"),
                        "flag": f"https://flagcdn.com/w40/{t.get('code', '').lower()}.png"
                    }
                    for code in codes
                    for t in all_teams
                    if t.get("code") == code
                ]
            }
            for gname, codes in groups_data.items()
        ]
    }


@router.get("/{group_name}")
async def get_group_detail(group_name: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    获取小组详情（核心API）- 增强版
    
    设计原则：
    - 预测数据立即返回（使用本地数据）
    - 实时数据异步加载（不阻塞）
    - 新增：赔率对比、伤病影响、情感分析
    
    返回：
    - 预测积分榜（基于FIFA排名、Elo评分）
    - 比赛预测（三模型对比）
    - 实时数据（如有缓存）
    - 三大数据因素（赔率/伤病/情感）
    """
    group_name = group_name.upper()
    logger.info(f"⚽ 请求小组: {group_name}")
    
    # 检查缓存
    if group_name in _prediction_cache:
        cached_time = _cache_timestamp.get(group_name)
        if cached_time and datetime.now() - cached_time < CACHE_TTL:
            logger.info(f"✅ 缓存命中: {group_name}")
            # 后台异步刷新实时数据
            background_tasks.add_task(refresh_realtime_data, group_name)
            return _prediction_cache[group_name]
    
    # 使用本地数据计算（快速，不依赖外部API）
    team_lookup = get_team_lookup()
    groups_dict = get_groups_dict()
    
    if group_name not in groups_dict:
        return {"error": f"小组不存在: {group_name}"}
    
    # groups_dict[group_name] 直接返回球队列表
    teams = groups_dict[group_name]
    
    # 获取本地赛程
    all_matches_dict = generate_match_schedule()
    matches_data = all_matches_dict.get(group_name, [])
    
    # 核心预测计算
    ensemble = get_ensemble()
    
    # 获取实际积分榜数据（优先使用缓存）
    actual_standings = []
    actual_matches = []  # 新增：实时比赛数据
    
    if group_name in _realtime_cache:
        actual_standings = _realtime_cache[group_name].get("standings", [])
        actual_matches = _realtime_cache[group_name].get("matches", [])
        logger.info(f"✅ 使用缓存的实时数据: {group_name}")
    else:
        # 尝试获取实时数据（异步，有超时保护）
        try:
            ds = get_data_service()
            actual_standings = await asyncio.wait_for(
                ds.get_standings(group_name),
                timeout=5.0  # 增加到5秒
            )
            actual_matches = await asyncio.wait_for(
                ds.get_matches(group=group_name),
                timeout=5.0
            )
            logger.info(f"✅ 获取实时数据成功: {group_name}, 积分榜{len(actual_standings)}条, 比赛{len(actual_matches)}场")
        except Exception as e:
            logger.warning(f"⚠️ 实时数据获取失败: {group_name} - {e}")
            actual_standings = []
            actual_matches = []
    
    # 构建积分榜和比赛预测
    standings = build_standings(teams, matches_data, ensemble, actual_standings)
    matches = build_matches_enhanced(teams, matches_data, ensemble, group_name, actual_matches)  # 增强版，包含三大数据和实际比分
    
    # 获取小组伤病汇总
    injury_summary = get_group_injury_summary(teams)
    
    # 获取小组情感汇总
    sentiment_summary = get_group_sentiment_summary(teams)
    
    result = {
        "group": group_name,
        "standings": standings,
        "matches": matches,
        "data_source": "local",
        "is_realtime": False,
        "realtime_available": False,
        # 新增：三大数据因素
        "injury_summary": injury_summary,
        "sentiment_summary": sentiment_summary,
    }
    
    # 缓存结果
    _prediction_cache[group_name] = result
    _cache_timestamp[group_name] = datetime.now()
    
    # 后台异步获取实时数据（不阻塞响应）
    background_tasks.add_task(refresh_realtime_data, group_name)
    
    logger.info(f"✅ 返回预测数据: {group_name}")
    return result


def build_standings(teams: List, matches: List, ensemble, actual_standings: List) -> List[Dict]:
    """构建积分榜（基于预测结果计算积分）"""
    # 初始化积分
    table = {t["code"]: {
        "team": t,
        "predicted_points": 0,  # 预测积分（按比赛规则）
        "predicted_w": 0,
        "predicted_d": 0,
        "predicted_l": 0
    } for t in teams}
    
    # 基于预测结果计算积分（胜3分、平1分、负0分）
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    for i, j in pairs:
        if i >= len(teams) or j >= len(teams):
            continue
        home, away = teams[i], teams[j]
        try:
            pred = ensemble.predict_match(home, away, "GROUP")
            
            home_code = home["code"]
            away_code = away["code"]
            
            # 根据预测结果分配积分
            prediction = pred.ensemble_prediction
            
            if prediction == "主胜":
                # 主队获胜：主队得3分，客队得0分
                table[home_code]["predicted_points"] += 3
                table[home_code]["predicted_w"] += 1
                table[away_code]["predicted_l"] += 1
            elif prediction == "平局":
                # 平局：双方各得1分
                table[home_code]["predicted_points"] += 1
                table[away_code]["predicted_points"] += 1
                table[home_code]["predicted_d"] += 1
                table[away_code]["predicted_d"] += 1
            else:  # 客胜
                # 客队获胜：主队得0分，客队得3分
                table[away_code]["predicted_points"] += 3
                table[home_code]["predicted_l"] += 1
                table[away_code]["predicted_w"] += 1
        except Exception as e:
            logger.warning(f"预测失败: {e}")
    
    # 排序
    sorted_table = sorted(table.values(), key=lambda x: x["predicted_points"], reverse=True)
    
    # 合并实际积分
    # 添加 code 映射（WorldCup26.ir 使用 RSA，本地使用 ZAF）
    code_mapping = {
        "RSA": "ZAF",  # South Africa
        "KSA": "SAU",  # Saudi Arabia
    }
    actual_map = {}
    for s in actual_standings:
        code = s.get("code") or s.get("team_id")
        # 映射到本地 code
        local_code = code_mapping.get(code, code)
        actual_map[local_code] = s
    
    result = []
    for i, s in enumerate(sorted_table):
        team = s["team"]
        code = team["code"]
        act = actual_map.get(code, {})
        
        result.append({
            "position": i + 1,
            "code": code,
            "name": team.get("name"),
            "name_cn": team.get("name_cn"),
            "rank": team.get("rank", 99),
            # 预测积分（按比赛规则计算）
            "predicted_points": s["predicted_points"],
            "predicted_w": s["predicted_w"],
            "predicted_d": s["predicted_d"],
            "predicted_l": s["predicted_l"],
            # 实际积分（未比赛显示0）
            "actual_points": act.get("points", 0) or act.get("pts", 0),
            "actual_w": act.get("w", 0),
            "actual_d": act.get("d", 0),
            "actual_l": act.get("l", 0),
            "actual_gf": act.get("gf", 0),
            "actual_ga": act.get("ga", 0),
            "actual_gd": act.get("gd", 0),
            # 差异
            "diff": round((act.get("points", 0) or act.get("pts", 0)) - s["predicted_points"], 1),
            "diff_text": "待比赛" if (act.get("points", 0) or act.get("pts", 0)) == 0 else "符合预期" if (act.get("points", 0) or act.get("pts", 0)) == s["predicted_points"] else "偏差"
        })
    
    return result


def build_matches(teams: List, matches_data: List, ensemble) -> List[Dict]:
    """构建比赛列表（包含三模型对比）"""
    result = []
    
    for m in matches_data:
        home_code = m.get("home") or m.get("home_code")
        away_code = m.get("away") or m.get("away_code")
        
        home_team = next((t for t in teams if t["code"] == home_code), None)
        away_team = next((t for t in teams if t["code"] == away_code), None)
        
        if not home_team or not away_team:
            logger.warning(f"找不到球队: {home_code} vs {away_code}")
            continue
        
        try:
            pred = ensemble.predict_match(home_team, away_team, "GROUP")
            bayesian = pred.bayesian_pred
            nn_pred = pred.nn_pred
            rf_pred = pred.rf_pred
            
            # 构建三模型对比
            models_comparison = {
                "bayesian": {
                    "home_win": round(bayesian.home_win_prob, 3) if bayesian else 0,
                    "draw": round(bayesian.draw_prob, 3) if bayesian else 0,
                    "away_win": round(bayesian.away_win_prob, 3) if bayesian else 0,
                    "result": "主胜" if bayesian and bayesian.home_win_prob > 0.5 else "平局" if bayesian and bayesian.draw_prob > 0.3 else "客胜"
                },
                "neural_network": {
                    "home_win": round(nn_pred.home_win_prob, 3) if nn_pred else 0.33,
                    "draw": round(nn_pred.draw_prob, 3) if nn_pred else 0.34,
                    "away_win": round(nn_pred.away_win_prob, 3) if nn_pred else 0.33,
                    "result": "主胜" if nn_pred and nn_pred.home_win_prob > 0.4 else "-"
                },
                "random_forest": {
                    "home_win": round(rf_pred.home_win_prob, 3) if rf_pred else 0.33,
                    "draw": round(rf_pred.draw_prob, 3) if rf_pred else 0.34,
                    "away_win": round(rf_pred.away_win_prob, 3) if rf_pred else 0.33,
                    "result": "主胜" if rf_pred and rf_pred.home_win_prob > 0.45 else "-"
                },
                "ensemble": {
                    "home_win": round(pred.ensemble_home_prob, 3),
                    "draw": round(pred.ensemble_draw_prob, 3),
                    "away_win": round(pred.ensemble_away_prob, 3),
                    "result": pred.ensemble_prediction
                }
            }
            
            # 贝叶斯因子
            bayesian_factors = {
                "elo_diff": home_team.get("elo", 1500) - away_team.get("elo", 1500),
                "rank_gap": away_team.get("rank", 99) - home_team.get("rank", 99),
                "confidence": round(bayesian.confidence, 2) if bayesian else 0
            } if bayesian else None
            
            result.append({
                "match_id": m.get("match_id"),
                "idx": m.get("match_index"),
                "home": home_code,
                "home_name_cn": home_team.get("name_cn", home_team.get("name")),
                "away": away_code,
                "away_name_cn": away_team.get("name_cn", away_team.get("name")),
                # 预测
                "home_win_prob": round(pred.ensemble_home_prob, 3),
                "draw_prob": round(pred.ensemble_draw_prob, 3),
                "away_win_prob": round(pred.ensemble_away_prob, 3),
                "prediction": pred.ensemble_prediction,
                "confidence": "高" if pred.ensemble_home_prob > 0.6 else "中" if pred.ensemble_home_prob > 0.4 else "低",
                # 实际
                "home_score": m.get("home_score"),
                "away_score": m.get("away_score"),
                "status": m.get("status"),
                "scheduled_time": m.get("scheduled_time"),
                # 三模型对比
                "models_comparison": models_comparison,
                # 贝叶斯因子
                "bayesian_factors": bayesian_factors,
                # 结果说明
                "result_text": f"预测: {pred.ensemble_prediction}"
            })
        except Exception as e:
            logger.error(f"构建比赛数据失败: {e}")
            result.append({
                "match_id": m.get("match_id"),
                "home": home_code,
                "away": away_code,
                "error": str(e)
            })
    
    logger.info(f"✅ 构建完成: {len(result)} 场比赛")
    return result


# ==================== 实时数据异步加载 ====================

async def refresh_realtime_data(group_name: str):
    """
    后台任务：异步刷新实时数据（不阻塞主请求）
    
    流程：
    1. 从 WorldCup26.ir 获取实时积分榜和比赛数据
    2. 更新缓存（供下次请求使用）
    3. 失败也不影响预测功能
    """
    logger.info(f"🔄 后台刷新实时数据: {group_name}")
    
    try:
        ds = get_data_service()
        
        # 获取实时积分榜（异步，有超时保护）
        actual_standings = await asyncio.wait_for(
            ds.get_standings(group_name),
            timeout=10.0
        )
        
        # 获取实时比赛数据
        matches = await asyncio.wait_for(
            ds.get_matches(group=group_name),
            timeout=10.0
        )
        
        # 更新实时数据缓存
        _realtime_cache[group_name] = {
            "standings": actual_standings,
            "matches": matches,
            "timestamp": datetime.now().isoformat()
        }
        _realtime_timestamp[group_name] = datetime.now()
        
        logger.info(f"✅ 实时数据更新: {group_name}, 积分榜{len(actual_standings)}条, 比赛{len(matches)}场")
        
    except asyncio.TimeoutError:
        logger.warning(f"⚠️ 实时数据超时: {group_name}")
    except Exception as e:
        logger.warning(f"⚠️ 实时数据获取失败: {group_name} - {e}")


@router.get("/{group_name}/realtime")
async def get_realtime_data(group_name: str) -> Dict[str, Any]:
    """
    获取实时数据（前端轮询接口）
    
    用于：
    - 比赛开始后，前端定时轮询获取实时比分
    - 积分榜实时更新
    
    返回：
    - 实时积分榜
    - 比赛状态
    - 最后更新时间
    """
    group_name = group_name.upper()
    
    # 检查缓存
    if group_name in _realtime_cache:
        cached_time = _realtime_timestamp.get(group_name)
        if cached_time and datetime.now() - cached_time < REALTIME_CACHE_TTL:
            return {
                "group": group_name,
                "data": _realtime_cache[group_name],
                "cached": True
            }
    
    # 缓存过期，异步刷新
    try:
        ds = get_data_service()
        actual_standings = await asyncio.wait_for(
            ds.get_standings(group_name),
            timeout=5.0
        )
        
        result = {
            "standings": actual_standings,
            "timestamp": datetime.now().isoformat()
        }
        
        # 更新缓存
        _realtime_cache[group_name] = result
        _realtime_timestamp[group_name] = datetime.now()
        
        return {
            "group": group_name,
            "data": result,
            "cached": False
        }
        
    except asyncio.TimeoutError:
        return {
            "group": group_name,
            "error": "timeout",
            "message": "实时数据请求超时"
        }
    except Exception as e:
        return {
            "group": group_name,
            "error": str(e),
            "message": "实时数据获取失败"
        }


# ==================== 三大数据因素辅助函数 ====================

def get_group_injury_summary(teams: List[Dict]) -> Dict:
    """获取小组伤病情况汇总"""
    from data.injuries import get_injury_report
    
    summary = []
    total_impact = 0
    
    for team in teams:
        code = team.get("code")
        if code:
            try:
                report = get_injury_report(code)
                summary.append({
                    "code": code,
                    "name_cn": team.get("name_cn"),
                    "injury_count": report["injury_count"],
                    "risk_level": report["risk_level"],
                    "risk_label": report["risk_label"],
                    "impact": report["impact_coefficient"]
                })
                total_impact += report["impact_coefficient"]
            except:
                pass
    
    return {
        "teams": summary,
        "group_avg_impact": round(total_impact / len(teams), 3) if teams else 0,
        "critical_teams": [t for t in summary if t["risk_level"] in ["critical", "high"]]
    }


def get_group_sentiment_summary(teams: List[Dict]) -> Dict:
    """获取小组情感情况汇总"""
    from data.social_sentiment import get_team_sentiment
    
    summary = []
    
    for team in teams:
        code = team.get("code")
        if code:
            try:
                sentiment = get_team_sentiment(code)
                summary.append({
                    "code": code,
                    "name_cn": team.get("name_cn"),
                    "overall_sentiment": sentiment["overall_sentiment"],
                    "confidence_level": sentiment["confidence_level"],
                    "buzz_score": sentiment["buzz_score"],
                    "pressure_level": sentiment["pressure_level"]
                })
            except:
                pass
    
    # 按信心排序
    summary.sort(key=lambda x: x["confidence_level"], reverse=True)
    
    return {
        "teams": summary,
        "highest_confidence": summary[0] if summary else None,
        "avg_sentiment": round(sum(t["overall_sentiment"] for t in summary) / len(summary), 3) if summary else 0.5
    }


def build_matches_enhanced(teams: List, matches_data: List, ensemble, group_name: str, actual_matches: List = None) -> List[Dict]:
    """构建比赛列表（增强版 - 包含赔率对比和三大数据）"""
    from data.odds import get_match_odds
    from data.injuries import compare_injuries
    from data.social_sentiment import compare_sentiments
    
    result = []
    
    # 球队代码映射
    code_mapping = {"RSA": "ZAF", "KSA": "SAU"}
    
    # 构建实际比赛数据映射
    actual_match_map = {}
    if actual_matches:
        for rm in actual_matches:
            rm_home = rm.get("home")
            rm_away = rm.get("away")
            rm_home_local = code_mapping.get(rm_home, rm_home)
            rm_away_local = code_mapping.get(rm_away, rm_away)
            actual_match_map[(rm_home_local, rm_away_local)] = rm
    
    for idx, m in enumerate(matches_data):
        home_code = m.get("home") or m.get("home_code")
        away_code = m.get("away") or m.get("away_code")
        
        home_team = next((t for t in teams if t["code"] == home_code), None)
        away_team = next((t for t in teams if t["code"] == away_code), None)
        
        if not home_team or not away_team:
            continue
        
        try:
            pred = ensemble.predict_match(home_team, away_team, "GROUP")
            bayesian = pred.bayesian_pred
            nn_pred = pred.nn_pred
            rf_pred = pred.rf_pred
            
            # 三模型对比
            models_comparison = {
                "bayesian": {
                    "home_win": round(bayesian.home_win_prob, 3) if bayesian else 0,
                    "draw": round(bayesian.draw_prob, 3) if bayesian else 0,
                    "away_win": round(bayesian.away_win_prob, 3) if bayesian else 0,
                    "result": "主胜" if bayesian and bayesian.home_win_prob > 0.5 else "平局" if bayesian and bayesian.draw_prob > 0.3 else "客胜"
                },
                "neural_network": {
                    "home_win": round(nn_pred.home_win_prob, 3) if nn_pred else 0.33,
                    "draw": round(nn_pred.draw_prob, 3) if nn_pred else 0.34,
                    "away_win": round(nn_pred.away_win_prob, 3) if nn_pred else 0.33,
                    "result": "主胜" if nn_pred and nn_pred.home_win_prob > 0.4 else "-"
                },
                "random_forest": {
                    "home_win": round(rf_pred.home_win_prob, 3) if rf_pred else 0.33,
                    "draw": round(rf_pred.draw_prob, 3) if rf_pred else 0.34,
                    "away_win": round(rf_pred.away_win_prob, 3) if rf_pred else 0.33,
                    "result": "主胜" if rf_pred and rf_pred.home_win_prob > 0.45 else "-"
                },
                "ensemble": {
                    "home_win": round(pred.ensemble_home_prob, 3),
                    "draw": round(pred.ensemble_draw_prob, 3),
                    "away_win": round(pred.ensemble_away_prob, 3),
                    "result": pred.ensemble_prediction
                }
            }
            
            # 赔率对比（如果可用）
            odds_comparison = None
            try:
                odds_data = get_match_odds(group_name, idx)
                if odds_data:
                    odds_comparison = {
                        "available": True,
                        "consensus": odds_data["consensus"],
                        "favorite": odds_data["favorite"],
                        "bookmakers": list(odds_data["odds"].keys()),
                        "model_vs_market": {
                            "home_win_diff": round(pred.ensemble_home_prob - odds_data["consensus"]["home_win"], 3),
                            "draw_diff": round(pred.ensemble_draw_prob - odds_data["consensus"]["draw"], 3),
                            "away_win_diff": round(pred.ensemble_away_prob - odds_data["consensus"]["away_win"], 3),
                        },
                        "moneyline": odds_data.get("moneyline", ""),
                        "asian_handicap": odds_data.get("asian_handicap"),
                        "jingcai_handicap": odds_data.get("jingcai_handicap"),
                        "total_goals": odds_data.get("total_goals"),
                        "comprehensive_advice": odds_data.get("comprehensive_advice")
                    }
            except:
                pass
            
            # 伤病对比
            injury_comparison = None
            try:
                injury_comparison = compare_injuries(home_code, away_code)
            except:
                pass
            
            # 情感对比
            sentiment_comparison = None
            try:
                sentiment_comparison = compare_sentiments(home_code, away_code)
            except:
                pass
            
            # 获取实际比分和比赛状态（从实时数据）
            match_status = "scheduled"
            home_score = None
            away_score = None
            
            # 从实际比赛数据中查找
            match_key = (home_code, away_code)
            if match_key in actual_match_map:
                rm = actual_match_map[match_key]
                match_status = rm.get("status", "scheduled")
                home_score = rm.get("home_score")
                away_score = rm.get("away_score")
            
            # 计算实际比分和预测结果
            actual_score = None
            actual_result = None
            prediction_correct = None
            
            if match_status == "finished" and home_score is not None and away_score is not None:
                actual_score = f"{home_score} - {away_score}"
                if home_score > away_score:
                    actual_result = "主胜"
                elif home_score < away_score:
                    actual_result = "客胜"
                else:
                    actual_result = "平局"
                
                # 判断预测是否正确
                predicted_result = pred.ensemble_prediction
                prediction_correct = (predicted_result == actual_result)
            
            result.append({
                "match_id": m.get("match_id"),
                "idx": idx,
                "home": home_code,
                "home_name_cn": home_team.get("name_cn", home_team.get("name")),
                "away": away_code,
                "away_name_cn": away_team.get("name_cn", away_team.get("name")),
                # 预测
                "home_win_prob": round(pred.ensemble_home_prob, 3),
                "draw_prob": round(pred.ensemble_draw_prob, 3),
                "away_win_prob": round(pred.ensemble_away_prob, 3),
                "prediction": pred.ensemble_prediction,
                "confidence": "高" if pred.ensemble_home_prob > 0.6 else "中" if pred.ensemble_home_prob > 0.4 else "低",
                # 三模型对比
                "models_comparison": models_comparison,
                # 新增：三大数据因素
                "odds_comparison": odds_comparison,
                "injury_comparison": injury_comparison,
                "sentiment_comparison": sentiment_comparison,
                # 实际比分
                "home_score": home_score,
                "away_score": away_score,
                "status": match_status,
                # 新增：实际结果和预测是否正确
                "actual_score": {
                    "result": actual_score,
                    "home_score": home_score,
                    "away_score": away_score
                } if actual_score else None,
                "actual_result": actual_result,
                "prediction_correct": prediction_correct
            })
        except Exception as e:
            logger.error(f"构建比赛数据失败: {e}")
            result.append({
                "match_id": m.get("match_id"),
                "home": home_code,
                "away": away_code,
                "error": str(e)
            })
    
    logger.info(f"✅ 构建完成: {len(result)} 场比赛（含三大数据）")
    return result