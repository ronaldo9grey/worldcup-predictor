"""
预测引擎 V6 - P0集成版
集成：
1. 特征引擎V2（h2h、venue_factor、特征交互）
2. 在线学习V2（阶段自适应学习率、动态窗口）
"""
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import math

from services.feature_engine_v2 import FeatureEngineV2, FeatureSet, get_feature_engine_v2
from services.online_learning_v2 import OnlineLearningV2, get_online_learning_v2
from services.bayesian_model import BayesianPredictionModel, get_bayesian_model, get_upset_detector
from data.world_cup_2026 import get_team_lookup, GROUPS


@dataclass
class MatchPredictionV6:
    """V6比赛预测结果"""
    # 基本信息
    home_code: str
    home_name_cn: str
    away_code: str
    away_name_cn: str
    stage: str
    group: Optional[str]
    
    # 特征集合（新增）
    features: FeatureSet
    
    # 贝叶斯概率
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    
    # 置信区间
    home_win_interval: Tuple[float, float]
    draw_interval: Tuple[float, float]
    away_win_interval: Tuple[float, float]
    
    # 预测结果
    prediction: str
    confidence_level: str
    confidence_value: float
    
    # 风险评估
    risk_level: str
    risk_description: str
    
    # 冷门分析
    upset_score: float
    is_upset_warning: bool
    upset_factors: List[str]
    
    # 在线学习状态（新增）
    current_weights: Dict[str, float]
    stage_learning_rate: float
    
    # 预测ID
    prediction_id: str


class PredictionEngineV6:
    """
    预测引擎 V6
    
    P0集成：
    - 使用特征引擎V2（13维特征 + 交互）
    - 使用在线学习V2（阶段自适应）
    - 保留贝叶斯概率模型
    - 保留冷门检测
    """
    
    def __init__(self):
        self.feature_engine = get_feature_engine_v2()
        self.online_learner = get_online_learning_v2()
        self.bayesian = get_bayesian_model()
        self.upset_detector = get_upset_detector()
        self.team_lookup = get_team_lookup()
        
        # 模型权重
        self.model_weights = {
            'bayesian': 0.4,
            'neural_network': 0.3,
            'random_forest': 0.3
        }
        
        self._initialized = False
    
    def initialize(self) -> Dict:
        """初始化引擎"""
        if self._initialized:
            return {'status': 'already_initialized'}
        
        # 初始化在线学习
        self.online_learner.set_models(nn_model=None, rf_model=None)
        
        self._initialized = True
        return {
            'status': 'initialized',
            'feature_engine': 'V2 (13维)',
            'online_learning': 'V2 (阶段自适应)',
            'model_weights': self.model_weights
        }
    
    def predict_match(
        self,
        home_code: str,
        away_code: str,
        stage: str = "GROUP",
        group: Optional[str] = None,
        match_index: int = 0
    ) -> MatchPredictionV6:
        """
        预测比赛结果 V6
        
        集成特征引擎V2和在线学习V2
        """
        # 获取球队数据
        home = self.team_lookup.get(home_code)
        away = self.team_lookup.get(away_code)
        
        if not home:
            home = {"code": home_code, "name_cn": home_code, "elo": 1500, "rank": 50,
                    "form": "DDD", "continent": "EU"}
        if not away:
            away = {"code": away_code, "name_cn": away_code, "elo": 1500, "rank": 50,
                    "form": "DDD", "continent": "EU"}
        
        # ========== P0新增：使用特征引擎V2 ==========
        features = self.feature_engine.compute_features(
            home=home,
            away=away,
            stage=stage,
            group=group
        )
        
        # 计算基础概率（使用特征）
        base_probs = self._compute_base_probabilities_v2(home, away, stage, features)
        
        # ========== 贝叶斯推断 ==========
        elo_diff = home.get('elo', 1500) - away.get('elo', 1500)
        bayesian_result = self.bayesian.predict_with_uncertainty(
            home_prob=base_probs['home_win'],
            draw_prob=base_probs['draw'],
            away_prob=base_probs['away_win'],
            stage=stage,
            elo_diff=elo_diff / 300
        )
        
        # ========== 冷门检测 ==========
        upset_result = self._detect_upset_v2(home, away, bayesian_result, features)
        
        # ========== 在线学习状态 ==========
        stage_learning_rate = self.online_learner._get_stage_learning_rate(stage)
        current_weights = self.model_weights.copy()
        
        # ========== 构建预测结果 ==========
        prediction = bayesian_result['prediction']
        confidence_level = bayesian_result['confidence_level']
        confidence_value = bayesian_result['confidence_value']
        
        return MatchPredictionV6(
            home_code=home_code,
            home_name_cn=home.get('name_cn', home_code),
            away_code=away_code,
            away_name_cn=away.get('name_cn', away_code),
            stage=stage,
            group=group,
            
            # 特征集合
            features=features,
            
            # 贝叶斯概率
            home_win_prob=bayesian_result['probabilities']['home_win'],
            draw_prob=bayesian_result['probabilities']['draw'],
            away_win_prob=bayesian_result['probabilities']['away_win'],
            
            # 置信区间
            home_win_interval=(
                bayesian_result['confidence_intervals']['home_win']['lower'],
                bayesian_result['confidence_intervals']['home_win']['upper']
            ),
            draw_interval=(
                bayesian_result['confidence_intervals']['draw']['lower'],
                bayesian_result['confidence_intervals']['draw']['upper']
            ),
            away_win_interval=(
                bayesian_result['confidence_intervals']['away_win']['lower'],
                bayesian_result['confidence_intervals']['away_win']['upper']
            ),
            
            # 预测结果
            prediction=prediction,
            confidence_level=confidence_level,
            confidence_value=confidence_value,
            
            # 风险评估
            risk_level=bayesian_result['risk_assessment']['level'],
            risk_description=bayesian_result['risk_assessment']['description'],
            
            # 冷门分析
            upset_score=upset_result['upset_score'],
            is_upset_warning=upset_result['is_upset_warning'],
            upset_factors=upset_result['upset_factors'],
            
            # 在线学习状态
            current_weights=current_weights,
            stage_learning_rate=stage_learning_rate,
            
            # 预测ID
            prediction_id=f"PRED_{home_code}_{away_code}_{stage}"
        )
    
    def _compute_base_probabilities_v2(
        self,
        home: Dict,
        away: Dict,
        stage: str,
        features: FeatureSet
    ) -> Dict[str, float]:
        """
        计算基础概率 V2（使用特征引擎V2）
        
        新增：
        - 使用 h2h 因子
        - 使用 venue_factor
        - 使用特征交互
        """
        # 特征重要性权重
        importance = self.feature_engine.get_feature_importance()
        
        # 加权概率计算
        home_bias = 0.35
        away_bias = 0.30
        draw_bias = 0.35
        
        # 基础特征贡献
        home_bias += features.elo_diff * importance['elo_diff']
        home_bias += features.rank_diff * importance['rank_diff']
        home_bias += features.form_diff * importance['form_diff']
        home_bias += features.stage_factor * importance['stage_factor'] * 0.5
        home_bias += features.home_advantage * importance['home_advantage']
        home_bias += features.continent_factor * importance['continent_factor']
        
        # P0新增：历史交锋
        home_bias += features.h2h * importance['h2h']
        
        # P0新增：场地影响
        home_bias += features.venue_factor * importance['venue_factor']
        
        # P0新增：特征交互
        home_bias += features.elo_form_combined * importance['elo_form_combined']
        home_bias += features.rank_stage_combined * importance['rank_stage_combined']
        
        # 其他特征
        home_bias += features.wc_experience * importance['wc_experience']
        home_bias += features.squad_strength * importance['squad_strength']
        home_bias += features.coach_rating * importance['coach_rating']
        
        # 计算概率
        total = home_bias + draw_bias + away_bias
        
        home_prob = max(0.05, min(0.95, home_bias / total))
        draw_prob = max(0.05, min(0.40, draw_bias / total))
        away_prob = max(0.05, 1 - home_prob - draw_prob)
        
        # 归一化
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        return {
            'home_win': home_prob,
            'draw': draw_prob,
            'away_win': away_prob
        }
    
    def _detect_upset_v2(
        self,
        home: Dict,
        away: Dict,
        bayesian_result: Dict,
        features: FeatureSet
    ) -> Dict:
        """
        冷门检测 V2（使用新特征）
        """
        upset_factors = []
        upset_score = 0.0
        
        prediction = bayesian_result['prediction']
        probs = bayesian_result['probabilities']
        
        # 1. 实力差距 vs 状态差异
        if abs(features.elo_form_combined) > 0.3:
            # 实力和状态出现矛盾
            upset_factors.append(f"实力状态矛盾: Elo差{features.elo_diff:.2f}, 状态差{features.form_diff:.2f}")
            upset_score += 0.15
        
        # 2. 历史交锋因素（新增）
        if abs(features.h2h) > 0.05:
            if features.h2h > 0 and probs['away_win'] > 0.35:
                upset_factors.append(f"历史交锋暗示冷门: 客队虽有历史劣势但预测概率较高")
                upset_score += 0.1
            elif features.h2h < 0 and probs['home_win'] > 0.35:
                upset_factors.append(f"历史交锋暗示冷门: 主队虽有历史劣势但预测概率较高")
                upset_score += 0.1
        
        # 3. 场地因素（新增）
        if abs(features.venue_factor) > 0.08:
            if features.venue_factor > 0 and probs['away_win'] > 0.30:
                upset_factors.append(f"场地优势可能失效: 高原/高温未能转化为优势")
                upset_score += 0.08
            elif features.venue_factor < 0 and probs['home_win'] > 0.30:
                upset_factors.append(f"客场球队可能克服场地劣势")
                upset_score += 0.08
        
        # 4. 传统冷门信号
        elo_diff = home.get('elo', 1500) - away.get('elo', 1500)
        if elo_diff > 100 and probs['away_win'] > 0.25:
            upset_factors.append("强队存在爆冷风险")
            upset_score += 0.15
        
        # 5. 置信度低
        if bayesian_result['confidence_level'] == 'LOW':
            upset_score += 0.1
            upset_factors.append("预测置信度低，结果不确定")
        
        # 判断是否冷门预警
        is_upset_warning = upset_score > 0.25
        
        return {
            'upset_score': min(1.0, upset_score),
            'is_upset_warning': is_upset_warning,
            'upset_factors': upset_factors
        }
    
    def update_after_match(
        self,
        match_id: str,
        home_code: str,
        away_code: str,
        stage: str,
        predicted: str,
        actual: str,
        confidence: float
    ) -> Dict:
        """
        比赛结束后更新在线学习
        
        使用在线学习V2（阶段自适应）
        """
        # 获取特征（用于神经网络增量训练）
        home = self.team_lookup.get(home_code, {})
        away = self.team_lookup.get(away_code, {})
        features = self.feature_engine.compute_features(home, away, stage)
        
        # 更新在线学习
        result = self.online_learner.process_match_result(
            match_id=match_id,
            home_code=home_code,
            away_code=away_code,
            stage=stage,
            predicted=predicted,
            actual=actual,
            model_used='贝叶斯模型',
            confidence=confidence,
            current_weights=self.model_weights.copy(),
            features=features.to_dict()
        )
        
        # 更新模型权重
        if result['weight_adjusted']:
            self.model_weights = result['new_weights']
        
        return result
    
    def predict_group(self, group: str) -> List[MatchPredictionV6]:
        """预测整个小组的比赛"""
        predictions = []
        schedule = get_group_match_schedule(group)
        
        for match in schedule:
            pred = self.predict_match(
                home_code=match['home'],
                away_code=match['away'],
                stage='GROUP',
                group=group,
                match_index=match['match_index']
            )
            predictions.append(pred)
        
        return predictions
    
    def get_feature_analysis(self, home_code: str, away_code: str, stage: str) -> Dict:
        """获取特征分析（用于解释预测）"""
        home = self.team_lookup.get(home_code, {})
        away = self.team_lookup.get(away_code, {})
        
        features = self.feature_engine.compute_features(home, away, stage)
        importance = self.feature_engine.get_feature_importance()
        
        # 分析各特征贡献
        contributions = {}
        for name, value in features.to_dict().items():
            weight = importance.get(name, 0.05)
            contributions[name] = {
                'value': value,
                'weight': weight,
                'contribution': value * weight,
                'direction': '利好主队' if value > 0.02 else '利好客队' if value < -0.02 else '中性'
            }
        
        return {
            'features': features.to_dict(),
            'importance': importance,
            'contributions': contributions,
            'total_bias': sum(c['contribution'] for c in contributions.values())
        }


def get_group_match_schedule(group: str):
    """获取小组赛程"""
    from data.world_cup_2026 import MATCH_SCHEDULE
    return MATCH_SCHEDULE.get(group.upper(), [])


# 单例
_engine_v6_instance = None


def get_engine_v6() -> PredictionEngineV6:
    """获取V6引擎实例"""
    global _engine_v6_instance
    if _engine_v6_instance is None:
        _engine_v6_instance = PredictionEngineV6()
        _engine_v6_instance.initialize()
    return _engine_v6_instance
