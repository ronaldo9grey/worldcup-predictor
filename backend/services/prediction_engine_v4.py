"""
预测引擎 V4 - 贝叶斯模型 + 权重优化 + 准确率追踪
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

from services.bayesian_model import BayesianPredictionModel, UpsetDetector, get_bayesian_model, get_upset_detector
from services.model_trainer import WeightOptimizer, get_default_trainer
from services.accuracy_tracker import AccuracyTracker, get_accuracy_tracker
from data.world_cup_2026 import get_team_lookup


@dataclass
class MatchPredictionV4:
    """V4比赛预测结果 - 更丰富的信息"""
    # 基本信息
    home_code: str
    home_name: str
    home_name_cn: str
    away_code: str
    away_name: str
    away_name_cn: str
    
    # 贝叶斯概率
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    
    # 置信区间
    home_win_interval: Dict  # {lower, upper}
    draw_interval: Dict
    away_win_interval: Dict
    
    # 预测结果
    prediction: str
    confidence_level: str  # HIGH / MEDIUM / LOW
    confidence_value: float
    
    # 风险评估
    risk_level: str
    risk_description: str
    
    # 冷门分析
    upset_score: float
    is_upset_warning: bool
    upset_factors: List[str]
    upset_recommendation: str
    
    # 优化权重使用
    weights_used: Dict
    
    # 追踪ID
    prediction_id: Optional[str] = None


class PredictionEngineV4:
    """
    预测引擎 V4
    
    新特性：
    1. 贝叶斯概率模型 - 置信区间
    2. 权重优化 - 基于历史数据训练
    3. 冷门检测增强
    4. 准确率追踪
    """
    
    def __init__(self):
        self.team_lookup = get_team_lookup()
        self.bayesian_model = get_bayesian_model()
        self.upset_detector = get_upset_detector()
        self.trainer = get_default_trainer()
        self.accuracy_tracker = get_accuracy_tracker()
        
        # 优化权重
        self.optimized_weights = self.trainer.get_optimized_weights()
    
    def predict_match(
        self,
        home: Dict,
        away: Dict,
        stage: str = "GROUP",
        is_neutral: bool = True
    ) -> MatchPredictionV4:
        """
        V4预测方法
        
        返回更丰富的预测信息
        """
        # 基础因子计算
        elo_diff = (home.get("elo", 1500) - away.get("elo", 1500)) / 300
        rank_diff = (away.get("rank", 50) - home.get("rank", 50)) / 50
        
        # 使用优化权重计算基础概率
        base_home, base_draw, base_away = self._calculate_base_probs(
            home, away, elo_diff, rank_diff, stage
        )
        
        # 贝叶斯更新
        bayesian_result = self.bayesian_model.predict_with_uncertainty(
            base_home, base_draw, base_away, stage, elo_diff
        )
        
        # 冷门检测
        upset_analysis = self.upset_detector.detect_upset_potential(
            home, away,
            bayesian_result["probabilities"]["home_win"],
            bayesian_result["probabilities"]["away_win"],
            stage
        )
        
        # 记录预测（用于后续准确率追踪）
        match_id = f"{home.get('code', '')}_{away.get('code', '')}"
        
        prediction_id = self.accuracy_tracker.record_prediction(
            match_id=match_id,
            home_code=home.get("code", ""),
            away_code=away.get("code", ""),
            stage=stage,
            predicted=bayesian_result["prediction"],
            home_prob=bayesian_result["probabilities"]["home_win"],
            draw_prob=bayesian_result["probabilities"]["draw"],
            away_prob=bayesian_result["probabilities"]["away_win"],
            confidence_level=bayesian_result["confidence_level"],
            confidence_value=bayesian_result["confidence_value"],
            upset_detected=bayesian_result["is_upset_possible"]
        )
        
        return MatchPredictionV4(
            home_code=home.get("code", ""),
            home_name=home.get("name", ""),
            home_name_cn=home.get("name_cn", ""),
            away_code=away.get("code", ""),
            away_name=away.get("name", ""),
            away_name_cn=away.get("name_cn", ""),
            
            # 贝叶斯概率
            home_win_prob=bayesian_result["probabilities"]["home_win"],
            draw_prob=bayesian_result["probabilities"]["draw"],
            away_win_prob=bayesian_result["probabilities"]["away_win"],
            
            # 置信区间
            home_win_interval=bayesian_result["confidence_intervals"]["home_win"],
            draw_interval=bayesian_result["confidence_intervals"]["draw"],
            away_win_interval=bayesian_result["confidence_intervals"]["away_win"],
            
            # 预测结果
            prediction=bayesian_result["prediction"],
            confidence_level=bayesian_result["confidence_level"],
            confidence_value=bayesian_result["confidence_value"],
            
            # 风险评估
            risk_level=bayesian_result["risk_assessment"]["level"],
            risk_description=bayesian_result["risk_assessment"]["description"],
            
            # 冷门分析
            upset_score=upset_analysis["upset_score"],
            is_upset_warning=upset_analysis["is_upset_warning"],
            upset_factors=upset_analysis["upset_factors"],
            upset_recommendation=upset_analysis["recommendation"],
            
            # 权重信息
            weights_used=self.optimized_weights,
            
            # 追踪ID
            prediction_id=prediction_id
        )
    
    def _calculate_base_probs(
        self,
        home: Dict,
        away: Dict,
        elo_diff: float,
        rank_diff: float,
        stage: str
    ) -> tuple:
        """计算基础概率"""
        w = self.optimized_weights
        
        # Elo影响
        elo_effect = elo_diff * w.get("elo_diff", 0.28) * 0.8
        
        # 排名影响
        rank_effect = rank_diff * w.get("rank_gap", 0.10) * 0.5
        
        # 状态影响（简化）
        home_form_score = self._parse_form(home.get("form", "WDWDW"))
        away_form_score = self._parse_form(away.get("form", "WDWDW"))
        form_diff = (home_form_score - away_form_score) / 5
        form_effect = form_diff * w.get("form_diff", 0.18) * 0.5
        
        # 计算基础概率
        base_home = 0.35 + elo_effect + rank_effect + form_effect
        base_draw = 0.30 - abs(elo_diff) * 0.1
        base_away = 0.35 - elo_effect - rank_effect - form_effect
        
        # 阶段影响（淘汰赛平局率下降）
        if stage not in ["GROUP", "R16"]:
            base_draw *= 0.5
            extra = base_draw * 0.5
            base_home += extra * 0.6
            base_away += extra * 0.4
        
        # 归一化
        total = base_home + base_draw + base_away
        if total > 0:
            base_home /= total
            base_draw /= total
            base_away /= total
        
        return (
            max(0.05, min(0.90, base_home)),
            max(0.05, min(0.40, base_draw)),
            max(0.05, min(0.90, base_away))
        )
    
    def _parse_form(self, form: str) -> float:
        """解析近期状态"""
        score = 0
        for c in form[:5]:
            if c == "W":
                score += 3
            elif c == "D":
                score += 1
        return score
    
    def get_accuracy_report(self) -> Dict:
        """获取准确率报告"""
        return self.accuracy_tracker.get_accuracy_report()
    
    def verify_match(self, match_id: str, actual_result: str) -> Dict:
        """验证比赛结果"""
        return self.accuracy_tracker.verify_prediction(match_id, actual_result)


def create_v4_engine():
    """创建V4引擎"""
    return PredictionEngineV4()