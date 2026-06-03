"""
贝叶斯更新过程可视化 - 展示贝叶斯推断的详细步骤
这是训练过程可视化的扩展，展示贝叶斯概率模型的工作原理
"""
from typing import Dict, List, Any
from dataclasses import dataclass
import math


@dataclass
class BayesianStep:
    """贝叶斯更新过程的每一步"""
    step: int
    title: str
    description: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    formula: str  # 数学公式表示
    visualization: Dict[str, Any]  # 用于前端可视化


class BayesianVisualizer:
    """
    贝叶斯推断过程可视化
    
    展示贝叶斯模型如何将先验概率与模型预测结合，
    得出后验概率和置信区间
    
    核心公式：
    P(结果|数据) ∝ P(数据|结果) × P(结果)
    即：后验 ∝ 似然 × 先验
    """
    
    # 先验概率来源说明（历史世界杯统计）
    PRIOR_SOURCE = {
        "GROUP": {
            "data_source": "2018俄罗斯世界杯 + 2022卡塔尔世界杯小组赛统计",
            "total_matches": 96,  # 48队×2场 = 96场小组赛
            "statistics": {
                "HOME_WIN": {"count": 39, "percentage": 41.0},
                "DRAW": {"count": 25, "percentage": 26.0},
                "AWAY_WIN": {"count": 32, "percentage": 33.0}
            },
            "note": "小组赛冷门频发，主胜率低于淘汰赛"
        },
        "R16": {
            "data_source": "2018+2022世界杯16强淘汰赛统计",
            "total_matches": 32,
            "statistics": {
                "HOME_WIN": {"count": 14, "percentage": 44.0},
                "DRAW": {"count": 7, "percentage": 22.0},
                "AWAY_WIN": {"count": 11, "percentage": 34.0}
            },
            "note": "淘汰赛平局率下降，强队开始认真"
        },
        "QF": {
            "data_source": "2018+2022世界杯8强淘汰赛统计",
            "total_matches": 16,
            "statistics": {
                "HOME_WIN": {"count": 8, "percentage": 50.0},
                "DRAW": {"count": 3, "percentage": 18.0},
                "AWAY_WIN": {"count": 5, "percentage": 32.0}
            },
            "note": "8强基本是强队对决，主胜率上升"
        },
        "SF": {
            "data_source": "2018+2022世界杯半决赛统计",
            "total_matches": 8,
            "statistics": {
                "HOME_WIN": {"count": 4, "percentage": 50.0},
                "DRAW": {"count": 1, "percentage": 12.5},
                "AWAY_WIN": {"count": 3, "percentage": 37.5}
            },
            "note": "半决赛经验更重要"
        },
        "FI": {
            "data_source": "2018+2022世界杯决赛统计",
            "total_matches": 4,
            "statistics": {
                "HOME_WIN": {"count": 2, "percentage": 50.0},
                "DRAW": {"count": 1, "percentage": 25.0},
                "AWAY_WIN": {"count": 1, "percentage": 25.0}
            },
            "note": "决赛历史底蕴很重要（阿根廷2022、法国2018）"
        }
    }
    
    # 贝叶斯参数配置
    BAYESIAN_CONFIG = {
        "model_strength": 0.7,  # 模型预测权重
        "prior_strength": 0.3,  # 先验概率权重
        "confidence_level": 0.95,  # 95%置信区间
        "z_score": 1.96  # 95%置信区间Z值
    }
    
    def get_bayesian_update_process(
        self,
        home_prob: float,
        draw_prob: float,
        away_prob: float,
        stage: str = "GROUP",
        elo_diff: float = 0.0,
        home_name: str = "主队",
        away_name: str = "客队"
    ) -> List[BayesianStep]:
        """
        获取完整的贝叶斯更新过程（5步）
        
        Args:
            home_prob: 模型预测的主胜概率
            draw_prob: 模型预测的平局概率
            away_prob: 模型预测的客胜概率
            stage: 比赛阶段
            elo_diff: Elo分差（标准化后，用于计算不确定性）
            home_name: 主队名称（用于展示）
            away_name: 客队名称（用于展示）
        
        Returns:
            5个步骤的详细过程
        """
        steps = []
        
        # 获取先验数据
        prior_data = self.PRIOR_SOURCE.get(stage, self.PRIOR_SOURCE["GROUP"])
        prior_probs = prior_data["statistics"]
        
        # ========== 第1步：展示先验概率来源 ==========
        steps.append(BayesianStep(
            step=1,
            title="获取先验概率",
            description=f"从历史世界杯{stage}阶段统计中获取先验概率",
            input_data={
                "stage": stage,
                "stage_cn": self._get_stage_cn(stage),
                "data_source": prior_data["data_source"],
                "total_matches": prior_data["total_matches"]
            },
            output_data={
                "prior_probabilities": {
                    "HOME_WIN": {
                        "value": prior_probs["HOME_WIN"]["percentage"] / 100,
                        "count": prior_probs["HOME_WIN"]["count"],
                        "percentage": prior_probs["HOME_WIN"]["percentage"]
                    },
                    "DRAW": {
                        "value": prior_probs["DRAW"]["percentage"] / 100,
                        "count": prior_probs["DRAW"]["count"],
                        "percentage": prior_probs["DRAW"]["percentage"]
                    },
                    "AWAY_WIN": {
                        "value": prior_probs["AWAY_WIN"]["percentage"] / 100,
                        "count": prior_probs["AWAY_WIN"]["count"],
                        "percentage": prior_probs["AWAY_WIN"]["percentage"]
                    }
                },
                "prior_note": prior_data["note"]
            },
            formula="P(结果) = 历史该结果次数 / 历史总比赛数",
            visualization={
                "type": "prior_source",
                "chart_type": "bar",
                "data": {
                    "labels": ["主胜", "平局", "客胜"],
                    "values": [
                        prior_probs["HOME_WIN"]["percentage"],
                        prior_probs["DRAW"]["percentage"],
                        prior_probs["AWAY_WIN"]["percentage"]
                    ],
                    "counts": [
                        prior_probs["HOME_WIN"]["count"],
                        prior_probs["DRAW"]["count"],
                        prior_probs["AWAY_WIN"]["count"]
                    ]
                }
            }
        ))
        
        # ========== 第2步：获取模型预测 ==========
        steps.append(BayesianStep(
            step=2,
            title="获取模型预测",
            description=f"权重预测引擎根据{home_name}与{away_name}的实力对比计算概率",
            input_data={
                "home_team": home_name,
                "away_team": away_name,
                "elo_diff": round(elo_diff, 3),
                "elo_diff_raw": round(elo_diff * 300, 0),  # 转换为原始Elo差
                "factors_used": [
                    "Elo实力差", "状态差异", "排名差距",
                    "阶段因子", "主场优势", "历史交锋"
                ]
            },
            output_data={
                "model_probabilities": {
                    "HOME_WIN": {
                        "value": round(home_prob, 3),
                        "meaning": f"{home_name}获胜的概率"
                    },
                    "DRAW": {
                        "value": round(draw_prob, 3),
                        "meaning": "双方打平的概率"
                    },
                    "AWAY_WIN": {
                        "value": round(away_prob, 3),
                        "meaning": f"{away_name}获胜的概率"
                    }
                },
                "model_note": "基于13维特征加权计算得出"
            },
            formula="P_model(结果) = Σ(特征值 × 权重) → Softmax归一化",
            visualization={
                "type": "model_prediction",
                "chart_type": "pie",
                "data": {
                    "labels": ["主胜", "平局", "客胜"],
                    "values": [
                        round(home_prob * 100, 1),
                        round(draw_prob * 100, 1),
                        round(away_prob * 100, 1)
                    ]
                }
            }
        ))
        
        # ========== 第3步：贝叶斯更新计算 ==========
        model_strength = self.BAYESIAN_CONFIG["model_strength"]
        prior_strength = self.BAYESIAN_CONFIG["prior_strength"]
        
        # 计算后验概率（加权平均）
        post_home_raw = model_strength * home_prob + prior_strength * (prior_probs["HOME_WIN"]["percentage"] / 100)
        post_draw_raw = model_strength * draw_prob + prior_strength * (prior_probs["DRAW"]["percentage"] / 100)
        post_away_raw = model_strength * away_prob + prior_strength * (prior_probs["AWAY_WIN"]["percentage"] / 100)
        
        # 归一化
        total = post_home_raw + post_draw_raw + post_away_raw
        post_home = post_home_raw / total
        post_draw = post_draw_raw / total
        post_away = post_away_raw / total
        
        steps.append(BayesianStep(
            step=3,
            title="贝叶斯更新",
            description="将先验概率与模型预测结合，计算后验概率",
            input_data={
                "prior_probs": {
                    "HOME_WIN": prior_probs["HOME_WIN"]["percentage"] / 100,
                    "DRAW": prior_probs["DRAW"]["percentage"] / 100,
                    "AWAY_WIN": prior_probs["AWAY_WIN"]["percentage"] / 100
                },
                "model_probs": {
                    "HOME_WIN": home_prob,
                    "DRAW": draw_prob,
                    "AWAY_WIN": away_prob
                },
                "weights": {
                    "model": model_strength,
                    "prior": prior_strength
                }
            },
            output_data={
                "raw_posterior": {
                    "HOME_WIN": {
                        "calculation": f"{model_strength}×{home_prob:.3f} + {prior_strength}×{prior_probs['HOME_WIN']['percentage']/100:.2f}",
                        "value": round(post_home_raw, 4)
                    },
                    "DRAW": {
                        "calculation": f"{model_strength}×{draw_prob:.3f} + {prior_strength}×{prior_probs['DRAW']['percentage']/100:.2f}",
                        "value": round(post_draw_raw, 4)
                    },
                    "AWAY_WIN": {
                        "calculation": f"{model_strength}×{away_prob:.3f} + {prior_strength}×{prior_probs['AWAY_WIN']['percentage']/100:.2f}",
                        "value": round(post_away_raw, 4)
                    }
                },
                "normalized_posterior": {
                    "HOME_WIN": round(post_home, 3),
                    "DRAW": round(post_draw, 3),
                    "AWAY_WIN": round(post_away, 3)
                },
                "total_before_normalize": round(total, 4)
            },
            formula=f"P(结果|数据) = {model_strength}×P_model + {prior_strength}×P_prior, 然后归一化",
            visualization={
                "type": "bayesian_update",
                "chart_type": "comparison",
                "data": {
                    "labels": ["主胜", "平局", "客胜"],
                    "prior": [
                        prior_probs["HOME_WIN"]["percentage"],
                        prior_probs["DRAW"]["percentage"],
                        prior_probs["AWAY_WIN"]["percentage"]
                    ],
                    "model": [
                        round(home_prob * 100, 1),
                        round(draw_prob * 100, 1),
                        round(away_prob * 100, 1)
                    ],
                    "posterior": [
                        round(post_home * 100, 1),
                        round(post_draw * 100, 1),
                        round(post_away * 100, 1)
                    ]
                }
            }
        ))
        
        # ========== 第4步：置信区间计算 ==========
        z_score = self.BAYESIAN_CONFIG["z_score"]
        
        # 不确定性（基于Elo差）
        uncertainty = max(0.02, 0.08 - abs(elo_diff) * 0.02)
        
        # 计算标准差和置信区间
        intervals = {}
        for name, prob in [("HOME_WIN", post_home), ("DRAW", post_draw), ("AWAY_WIN", post_away)]:
            std = math.sqrt(prob * (1 - prob) + uncertainty)
            lower = max(0, prob - z_score * std)
            upper = min(1, prob + z_score * std)
            intervals[name] = {
                "median": round(prob, 3),
                "std": round(std, 4),
                "lower": round(lower, 3),
                "upper": round(upper, 3),
                "range": round(upper - lower, 3)
            }
        
        steps.append(BayesianStep(
            step=4,
            title="计算置信区间",
            description=f"计算95%置信区间，量化预测的不确定性",
            input_data={
                "posterior_probs": {
                    "HOME_WIN": round(post_home, 3),
                    "DRAW": round(post_draw, 3),
                    "AWAY_WIN": round(post_away, 3)
                },
                "elo_diff": round(elo_diff, 3),
                "uncertainty_factor": round(uncertainty, 3),
                "confidence_level": 0.95,
                "z_score": z_score
            },
            output_data={
                "confidence_intervals": intervals,
                "interpretation": {
                    "HOME_WIN": f"主胜概率在{intervals['HOME_WIN']['lower']*100:.1f}%到{intervals['HOME_WIN']['upper']*100:.1f}%之间",
                    "DRAW": f"平局概率在{intervals['DRAW']['lower']*100:.1f}%到{intervals['DRAW']['upper']*100:.1f}%之间",
                    "AWAY_WIN": f"客胜概率在{intervals['AWAY_WIN']['lower']*100:.1f}%到{intervals['AWAY_WIN']['upper']*100:.1f}%之间"
                },
                "uncertainty_note": f"Elo差距{abs(elo_diff*300):.0f}分，不确定性={uncertainty:.2f}（差距越大，越确定）"
            },
            formula=f"σ = √(p×(1-p) + u), 置信区间 = [p - {z_score}σ, p + {z_score}σ]",
            visualization={
                "type": "confidence_interval",
                "chart_type": "interval",
                "data": {
                    "labels": ["主胜", "平局", "客胜"],
                    "medians": [
                        round(post_home * 100, 1),
                        round(post_draw * 100, 1),
                        round(post_away * 100, 1)
                    ],
                    "lower": [
                        round(intervals["HOME_WIN"]["lower"] * 100, 1),
                        round(intervals["DRAW"]["lower"] * 100, 1),
                        round(intervals["AWAY_WIN"]["lower"] * 100, 1)
                    ],
                    "upper": [
                        round(intervals["HOME_WIN"]["upper"] * 100, 1),
                        round(intervals["DRAW"]["upper"] * 100, 1),
                        round(intervals["AWAY_WIN"]["upper"] * 100, 1)
                    ]
                }
            }
        ))
        
        # ========== 第5步：最终预测结论 ==========
        # 确定预测方向
        max_prob = max(post_home, post_draw, post_away)
        if max_prob == post_home:
            prediction = "HOME_WIN"
            prediction_cn = f"{home_name}获胜"
        elif max_prob == post_away:
            prediction = "AWAY_WIN"
            prediction_cn = f"{away_name}获胜"
        else:
            prediction = "DRAW"
            prediction_cn = "双方打平"
        
        # 置信度评估
        confidence_value = intervals[prediction]["median"] - intervals[prediction]["std"] * 2
        confidence_value = max(0.3, min(1.0, confidence_value))
        
        if confidence_value > 0.7:
            confidence_level = "HIGH"
            confidence_desc = "高置信度：预测较为可靠"
        elif confidence_value > 0.5:
            confidence_level = "MEDIUM"
            confidence_desc = "中等置信度：存在一定变数"
        else:
            confidence_level = "LOW"
            confidence_desc = "低置信度：结果难以预测"
        
        # 风险评估
        alternative_probs = [v["median"] for k, v in intervals.items() if k != prediction]
        risk_score = max(alternative_probs) / max_prob if max_prob > 0 else 0.5
        risk_level = "LOW" if risk_score < 0.6 else "MEDIUM" if risk_score < 0.8 else "HIGH"
        
        steps.append(BayesianStep(
            step=5,
            title="输出预测结论",
            description="综合后验概率、置信区间，给出最终预测和建议",
            input_data={
                "posterior_probs": {
                    "HOME_WIN": round(post_home, 3),
                    "DRAW": round(post_draw, 3),
                    "AWAY_WIN": round(post_away, 3)
                },
                "confidence_intervals": {
                    "HOME_WIN": f"[{intervals['HOME_WIN']['lower']:.3f}, {intervals['HOME_WIN']['upper']:.3f}]",
                    "DRAW": f"[{intervals['DRAW']['lower']:.3f}, {intervals['DRAW']['upper']:.3f}]",
                    "AWAY_WIN": f"[{intervals['AWAY_WIN']['lower']:.3f}, {intervals['AWAY_WIN']['upper']:.3f}]"
                }
            },
            output_data={
                "prediction": {
                    "result": prediction,
                    "result_cn": prediction_cn,
                    "probability": round(max_prob, 3),
                    "confidence_level": confidence_level,
                    "confidence_value": round(confidence_value, 2),
                    "confidence_desc": confidence_desc
                },
                "risk_assessment": {
                    "level": risk_level,
                    "score": round(risk_score, 2),
                    "description": self._get_risk_description(risk_level)
                },
                "summary": f"预测：{prediction_cn}（概率{max_prob*100:.1f}%），置信度：{confidence_level}"
            },
            formula="预测 = argmax(后验概率), 置信度 = median - 2×std",
            visualization={
                "type": "final_prediction",
                "chart_type": "result",
                "data": {
                    "prediction": prediction,
                    "prediction_cn": prediction_cn,
                    "probability": round(max_prob * 100, 1),
                    "confidence": round(confidence_value * 100, 1),
                    "risk_level": risk_level
                }
            }
        ))
        
        return steps
    
    def get_bayesian_config(self) -> Dict[str, Any]:
        """获取贝叶斯配置参数"""
        return {
            "config": self.BAYESIAN_CONFIG,
            "explanation": {
                "model_strength": "模型预测的权重，表示对模型预测的信任程度",
                "prior_strength": "先验概率的权重，表示对历史经验的信任程度",
                "confidence_level": "置信区间置信度，95%表示有95%的概率真实值落在区间内",
                "z_score": "Z分数，用于计算置信区间的宽度"
            },
            "philosophy": {
                "title": "贝叶斯推断的核心理念",
                "principle": "结合先验知识（历史统计）和新证据（模型预测），得出更可靠的后验概率",
                "advantage": [
                    "避免过度依赖单一模型预测",
                    "考虑历史规律作为参考",
                    "量化不确定性（置信区间）",
                    "对冷门比赛有更好的预警能力"
                ]
            }
        }
    
    def get_prior_source_all(self) -> Dict[str, Any]:
        """获取所有阶段的先验概率来源"""
        return {
            "source": self.PRIOR_SOURCE,
            "summary": {
                "title": "先验概率数据来源",
                "description": "基于2018俄罗斯世界杯和2022卡塔尔世界杯的真实比赛统计",
                "total_matches": 156,  # 96小组赛 + 32淘汰赛 + 16八强 + 8半决赛 + 4决赛
                "years": [2018, 2022],
                "champions": {
                    2018: "法国",
                    2022: "阿根廷"
                },
                "major_upsets": [
                    {"match": "沙特2-1阿根廷", "year": 2022, "stage": "GROUP"},
                    {"match": "日本2-1德国", "year": 2022, "stage": "GROUP"},
                    {"match": "韩国2-0德国", "year": 2018, "stage": "GROUP"},
                    {"match": "摩洛哥淘汰葡萄牙", "year": 2022, "stage": "QF"}
                ]
            }
        }
    
    def _get_stage_cn(self, stage: str) -> str:
        """获取阶段中文名称"""
        labels = {
            "GROUP": "小组赛",
            "R16": "16强淘汰赛",
            "QF": "8强淘汰赛",
            "SF": "半决赛",
            "FI": "决赛"
        }
        return labels.get(stage, stage)
    
    def _get_risk_description(self, level: str) -> str:
        """获取风险描述"""
        descriptions = {
            "LOW": "预测较为可靠，但足球是圆的",
            "MEDIUM": "存在一定变数，建议关注比赛走势",
            "HIGH": "比赛结果难以预测，可能出现冷门"
        }
        return descriptions.get(level, "")


def get_bayesian_visualizer() -> BayesianVisualizer:
    """获取贝叶斯可视化器实例"""
    return BayesianVisualizer()