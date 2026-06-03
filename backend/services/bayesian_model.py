"""
贝叶斯概率模型 - 更准确的预测置信度
使用贝叶斯推断计算预测置信区间
"""
from dataclasses import dataclass
from typing import Dict, Tuple, List
import math


@dataclass
class ConfidenceInterval:
    """置信区间"""
    lower: float  # 下限
    median: float # 中位数（预测值）
    upper: float  # 上限
    confidence: float  # 置信度 0-1


class BayesianPredictionModel:
    """
    贝叶斯预测模型
    
    特点：
    1. 基于先验概率和历史数据
    2. 输出置信区间而非单点估计
    3. 考虑不确定性
    """
    
    # 先验概率（基于历史世界杯统计）
    PRIOR_PROBABILITIES = {
        "GROUP": {
            "HOME_WIN": 0.41,  # 小组赛主胜率约41%
            "DRAW": 0.26,      # 平局率约26%
            "AWAY_WIN": 0.33   # 客胜率约33%
        },
        "R16": {
            "HOME_WIN": 0.44,
            "DRAW": 0.22,      # 淘汰赛平局率下降
            "AWAY_WIN": 0.34
        },
        "QF": {
            "HOME_WIN": 0.48,
            "DRAW": 0.18,
            "AWAY_WIN": 0.34
        },
        "SF": {
            "HOME_WIN": 0.50,
            "DRAW": 0.15,
            "AWAY_WIN": 0.35
        },
        "FI": {
            "HOME_WIN": 0.45,
            "DRAW": 0.20,
            "AWAY_WIN": 0.35
        }
    }
    
    # 冷门发生的先验概率（基于历史数据）
    UPSET_PRIOR = 0.15  # 约15%的比赛是冷门
    
    def __init__(self):
        self.historical_variance = {
            "HOME_WIN": 0.02,
            "DRAW": 0.03,
            "AWAY_WIN": 0.02
        }
    
    def compute_confidence_interval(
        self,
        home_prob: float,
        draw_prob: float,
        away_prob: float,
        stage: str = "GROUP",
        elo_diff: float = 0.0
    ) -> Dict[str, ConfidenceInterval]:
        """
        计算贝叶斯置信区间
        
        Args:
            home_prob, draw_prob, away_prob: 模型预测概率
            stage: 比赛阶段
            elo_diff: Elo分差（影响方差）
        
        Returns:
            三个结果的置信区间
        """
        # 获取先验概率
        prior = self.PRIOR_PROBABILITIES.get(stage, self.PRIOR_PROBABILITIES["GROUP"])
        
        # 贝叶斯更新：结合先验和模型预测
        # P(结果|数据) ∝ P(数据|结果) * P(结果)
        # 简化：使用加权平均
        
        # 证据强度（模型可信度）
        model_strength = 0.7  # 模型权重70%，先验30%
        
        # 后验概率
        post_home = model_strength * home_prob + (1 - model_strength) * prior["HOME_WIN"]
        post_draw = model_strength * draw_prob + (1 - model_strength) * prior["DRAW"]
        post_away = model_strength * away_prob + (1 - model_strength) * prior["AWAY_WIN"]
        
        # 归一化
        total = post_home + post_draw + post_away
        post_home /= total
        post_draw /= total
        post_away /= total
        
        # 计算方差（基于Elo差的不确定性）
        # Elo差越大，方差越小（越确定）
        uncertainty = max(0.02, 0.04 - abs(elo_diff) * 0.01)  # 降低基础不确定性（从0.08降到0.04）
        
        # 置信区间（近似正态分布）
        intervals = {}
        
        for name, prob in [("HOME_WIN", post_home), ("DRAW", post_draw), ("AWAY_WIN", post_away)]:
            std = math.sqrt(prob * (1 - prob) + uncertainty)
            intervals[name] = ConfidenceInterval(
                lower=max(0, prob - 1.96 * std),
                median=prob,
                upper=min(1, prob + 1.96 * std),
                confidence=self._compute_confidence(prob, std)
            )
        
        return intervals
    
    def _compute_confidence(self, prob: float, std: float) -> float:
        """
        计算预测置信度
        
        改进方案：基于最大概率与次大概率的比例
        - 最大概率远高于其他选项 → 高置信度
        - 最大概率接近其他选项 → 低置信度
        """
        # 简化置信度计算：直接基于概率大小
        # 概率越高，置信度越高
        # 使用非线性映射，使置信度分布更合理
        
        if prob >= 0.60:
            # 最大概率超过60%，高置信度
            confidence = 0.5 + (prob - 0.60) * 2  # 0.5-0.9
        elif prob >= 0.45:
            # 最大概率在45-60%，中等置信度
            confidence = 0.35 + (prob - 0.45) * 1.0  # 0.35-0.5
        else:
            # 最大概率低于45%，低置信度
            confidence = 0.3 + prob * 0.1  # 0.3-0.345
        
        return min(1.0, confidence)
    
    def predict_with_uncertainty(
        self,
        home_prob: float,
        draw_prob: float,
        away_prob: float,
        stage: str = "GROUP",
        elo_diff: float = 0.0
    ) -> Dict:
        """
        带不确定性的预测
        
        返回：
        - 预测结果
        - 置信度
        - 各结果概率区间
        - 风险评估
        """
        intervals = self.compute_confidence_interval(
            home_prob, draw_prob, away_prob, stage, elo_diff
        )
        
        # 确定预测方向
        medians = {
            "HOME_WIN": intervals["HOME_WIN"].median,
            "DRAW": intervals["DRAW"].median,
            "AWAY_WIN": intervals["AWAY_WIN"].median
        }
        
        predicted = max(medians.keys(), key=lambda k: medians[k])
        
        # 置信度等级
        confidence_value = intervals[predicted].confidence
        if confidence_value > 0.7:
            confidence_level = "HIGH"
        elif confidence_value > 0.5:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"
        
        # 风险评估：检查其他结果的可能性
        alternative_probs = [v.median for k, v in intervals.items() if k != predicted]
        risk_score = max(alternative_probs) / medians[predicted] if medians[predicted] > 0 else 0.5
        
        risk_level = "LOW" if risk_score < 0.6 else "MEDIUM" if risk_score < 0.8 else "HIGH"
        
        return {
            "prediction": predicted,
            "confidence_level": confidence_level,
            "confidence_value": round(confidence_value, 2),
            "probabilities": {
                "home_win": round(intervals["HOME_WIN"].median, 3),
                "draw": round(intervals["DRAW"].median, 3),
                "away_win": round(intervals["AWAY_WIN"].median, 3)
            },
            "confidence_intervals": {
                "home_win": {
                    "lower": round(intervals["HOME_WIN"].lower, 3),
                    "upper": round(intervals["HOME_WIN"].upper, 3)
                },
                "draw": {
                    "lower": round(intervals["DRAW"].lower, 3),
                    "upper": round(intervals["DRAW"].upper, 3)
                },
                "away_win": {
                    "lower": round(intervals["AWAY_WIN"].lower, 3),
                    "upper": round(intervals["AWAY_WIN"].upper, 3)
                }
            },
            "risk_assessment": {
                "level": risk_level,
                "score": round(risk_score, 2),
                "description": self._get_risk_description(risk_level, predicted)
            },
            "is_upset_possible": self._check_upset_possibility(intervals, predicted)
        }
    
    def _get_risk_description(self, level: str, predicted: str) -> str:
        """风险描述"""
        descriptions = {
            "LOW": "预测较为可靠，但有足球是圆的",
            "MEDIUM": "存在一定变数，建议关注比赛走势",
            "HIGH": "比赛结果难以预测，可能出现冷门"
        }
        return descriptions.get(level, "")
    
    def _check_upset_possibility(
        self,
        intervals: Dict[str, ConfidenceInterval],
        predicted: str
    ) -> bool:
        """
        检查是否存在冷门可能性
        
        冷门判定：弱队获胜概率超过一定阈值
        """
        # 获取所有概率
        probs = [v.median for v in intervals.values()]
        
        # 如果概率分布比较平均，则可能冷门
        max_prob = max(probs)
        min_prob = min(probs)
        
        # 如果最大概率和最小概率差距小于0.15，存在冷门可能
        return (max_prob - min_prob) < 0.15


class UpsetDetector:
    """冷门检测器"""
    
    # 历史冷门模式
    UPSET_PATTERNS = {
        "champion_struggle": {
            "description": "卫冕冠军小组赛挣扎",
            "indicators": ["GER-2018", "FRA-2002", "ITA-2010", "ESP-2014"]
        },
        "asian_power": {
            "description": "亚洲球队爆冷",
            "indicators": ["JPN-GER-2022", "KOR-GER-2018", "KSA-ARG-2022"]
        },
        "african_rise": {
            "description": "非洲球队突破",
            "indicators": ["MAR-ESP-2022", "MAR-POR-2022", "SEN-FRA-2022"]
        },
        "knockout_surprise": {
            "description": "淘汰赛黑马",
            "indicators": ["CRO-2018", "MAR-2022", "KOR-2002"]
        }
    }
    
    def detect_upset_potential(
        self,
        home_team: Dict,
        away_team: Dict,
        home_prob: float,
        away_prob: float,
        stage: str
    ) -> Dict:
        """
        检测冷门潜力
        
        返回冷门评分和预警
        """
        upset_factors = []
        upset_score = 0.0
        
        # 1. Elo差距检测
        elo_diff = home_team.get("elo", 1500) - away_team.get("elo", 1500)
        
        if elo_diff > 150 and away_prob > 0.25:
            # 强队vs弱队，但弱队有一定概率
            upset_factors.append("弱队具备爆冷实力")
            upset_score += 0.2
        
        if elo_diff < -100 and home_prob < 0.35:
            # 主场弱队
            upset_factors.append("主场劣势但非完全劣势")
            upset_score += 0.15
        
        # 2. 排名差距检测
        rank_diff = home_team.get("rank", 50) - away_team.get("rank", 50)
        
        if rank_diff < -20 and away_prob < 0.35:
            # 低排名球队有反击机会
            upset_factors.append("排名低不代表实力弱")
            upset_score += 0.15
        
        # 3. 世界杯经验检测
        home_exp = home_team.get("world_cup_experience", 5)
        away_exp = away_team.get("world_cup_experience", 5)
        
        if home_exp > 10 and away_exp < 5 and away_prob > 0.20:
            # 经验丰富vs新军，新军有潜力
            upset_factors.append("新军可能创造奇迹")
            upset_score += 0.1
        
        # 4. 阶段因素
        if stage == "GROUP":
            # 小组赛冷门率高
            upset_score *= 1.2
        elif stage in ["QF", "SF"]:
            # 淘汰赛后期，经验更重要
            if abs(elo_diff) < 50:
                upset_factors.append("势均力敌，可能爆冷")
                upset_score += 0.1
        
        # 5. 亚洲/非洲球队特殊检测
        home_continent = home_team.get("continent", "")
        away_continent = away_team.get("continent", "")
        
        if away_continent in ["AS", "AF"] and away_prob > 0.20:
            upset_factors.append("亚洲/非洲球队有爆冷传统")
            upset_score += 0.1
        
        # 归一化
        upset_score = min(1.0, upset_score)
        
        # 判断是否冷门预警
        is_upset_warning = upset_score > 0.4
        
        return {
            "upset_score": round(upset_score, 2),
            "is_upset_warning": is_upset_warning,
            "upset_factors": upset_factors,
            "recommendation": self._get_upset_recommendation(upset_score, upset_factors)
        }
    
    def _get_upset_recommendation(self, score: float, factors: List[str]) -> str:
        """冷门建议"""
        if score > 0.6:
            return "⚠️ 高冷门风险！谨慎投注"
        elif score > 0.4:
            return "⚡ 存在冷门可能，关注弱队"
        elif score > 0.2:
            return "💡 小概率冷门，正常预测"
        else:
            return "✅ 正常比赛，强队优势明显"


def get_bayesian_model():
    """获取贝叶斯模型实例"""
    return BayesianPredictionModel()


def get_upset_detector():
    """获取冷门检测器实例"""
    return UpsetDetector()