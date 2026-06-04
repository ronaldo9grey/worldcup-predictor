"""
模型集成框架
融合多种机器学习模型（贝叶斯、神经网络、随机森林）进行比赛预测
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json

from services.bayesian_model import get_bayesian_model
from services.neural_network import create_nn_model
from services.random_forest import create_random_forest
from services.model_trainer import get_default_trainer
from data.historical_world_cups import get_all_world_cup_matches
from data.world_cup_2026 import get_team_lookup


@dataclass
class ModelPrediction:
    """单个模型的预测结果"""
    model_name: str
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    confidence: float
    features_used: List[str]


@dataclass
class EnsemblePrediction:
    """集成预测结果"""
    # 基本信息
    home_code: str
    home_name_cn: str
    away_code: str
    away_name_cn: str
    
    # 各模型预测
    bayesian_pred: ModelPrediction
    nn_pred: Optional[ModelPrediction]
    rf_pred: Optional[ModelPrediction]
    
    # 集成结果
    ensemble_home_prob: float
    ensemble_draw_prob: float
    ensemble_away_prob: float
    ensemble_prediction: str
    ensemble_confidence: float
    
    # 模型一致性
    model_agreement: float  # 模型一致性程度 (0-1)
    disagreement_details: str
    
    # 权重信息
    model_weights: Dict[str, float]


class ModelEnsemble:
    """
    模型集成器
    
    融合贝叶斯、神经网络、随机森林三种模型
    """
    
    def __init__(self):
        self.team_lookup = get_team_lookup()
        self.bayesian = get_bayesian_model()
        self.trainer = get_default_trainer()
        
        # 模型实例
        self.nn_model = None
        self.rf_model = None
        self.nn_trained = False
        self.rf_trained = False
        
        # 模型权重（可动态调整）
        self.model_weights = {
            'bayesian': 0.4,
            'neural_network': 0.3,
            'random_forest': 0.3
        }
        
        # 在线学习状态
        self.learning_history = []
        self.performance_metrics = {
            'bayesian': {'correct': 0, 'total': 0},
            'neural_network': {'correct': 0, 'total': 0},
            'random_forest': {'correct': 0, 'total': 0}
        }
    
    def initialize_models(self, force_retrain: bool = False) -> Dict:
        """
        初始化所有模型（简化版，不持久化）
        
        Returns:
            初始化状态
        """
        status = {
            'bayesian': 'ready',
            'neural_network': 'not_trained',
            'random_forest': 'not_trained'
        }
        
        # 如果已经训练过且模型实例存在且不强制重新训练，直接返回
        if self.nn_trained and self.rf_trained and self.nn_model and self.rf_model and not force_retrain:
            status['neural_network'] = 'already_trained'
            status['random_forest'] = 'already_trained'
            return status
        
        # 如果只是标志位为True但模型实例不存在，重置标志位
        if not self.nn_model:
            self.nn_trained = False
        if not self.rf_model:
            self.rf_trained = False
        
        historical_matches = get_all_world_cup_matches()
        if len(historical_matches) == 0:
            return {'error': '无历史数据'}
        
        X, y = self._prepare_training_data(historical_matches)
        input_size = X.shape[1]
        
        # 训练神经网络
        try:
            self.nn_model = create_nn_model(input_size=input_size)
            self.nn_model.train(X, y, epochs=100, batch_size=16, validation_split=0.2)
            self.nn_trained = True
            status['neural_network'] = 'trained'
        except Exception as e:
            status['neural_network'] = f'error: {str(e)}'
            import traceback
            traceback.print_exc()
        
        # 训练随机森林
        try:
            self.rf_model = create_random_forest(n_estimators=100)
            train_result = self.rf_model.train(X, y)
            self.rf_trained = True
            status['random_forest'] = f'trained (accuracy: {train_result["accuracy"]:.1%})'
            status['rf_feature_importance'] = train_result.get('feature_importance', {})
        except Exception as e:
            status['random_forest'] = f'error: {str(e)}'
            import traceback
            traceback.print_exc()
        
        return status
    
    def _prepare_training_data(self, matches: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """
        准备训练数据
        
        Args:
            matches: 历史比赛列表
        
        Returns:
            X: 特征矩阵
            y: 标签向量
        """
        X = []
        y = []
        
        for match in matches:
            features = self._extract_match_features(match)
            X.append(list(features.values()))
            
            # 标签: 0=主胜, 1=平局, 2=客胜
            result = match.get('result', '')
            if result == 'HOME_WIN' or '主胜' in result:
                y.append(0)
            elif result == 'DRAW' or '平局' in result:
                y.append(1)
            else:
                y.append(2)
        
        return np.array(X), np.array(y)
    
    def _extract_match_features(self, match: Dict) -> Dict[str, float]:
        """提取比赛特征"""
        # 固定特征顺序
        feature_names = [
            'elo_diff', 'rank_diff', 'form_diff', 'stage_factor',
            'home_advantage', 'continent_factor', 'h2h', 'wc_experience',
            'squad_strength', 'coach_rating', 'venue_factor'
        ]
        
        features = {}
        for name in feature_names:
            features[name] = match.get(name, 0.0)
        
        # 如果原始数据有Elo，计算差值
        if 'home_elo' in match and 'away_elo' in match:
            features['elo_diff'] = (match['home_elo'] - match['away_elo']) / 300
        
        if 'home_rank' in match and 'away_rank' in match:
            features['rank_diff'] = (match['away_rank'] - match['home_rank']) / 50
        
        return features
    
    def predict_match(
        self,
        home: Dict,
        away: Dict,
        stage: str = "GROUP"
    ) -> EnsemblePrediction:
        """
        集成预测
        
        融合多模型预测结果
        """
        # 提取特征
        features = self._compute_features(home, away, stage)
        
        # 1. 贝叶斯模型预测
        bayesian_result = self._predict_bayesian(home, away, stage)
        
        # 2. 神经网络预测
        nn_result = None
        if self.nn_trained and self.nn_model:
            try:
                nn_result = self._predict_nn(features)
            except Exception as e:
                print(f"⚠️ 神经网络预测失败: {e}")
        else:
            print(f"⚠️ 神经网络未就绪: trained={self.nn_trained}, model={self.nn_model is not None}")
        
        # 3. 随机森林预测
        rf_result = None
        if self.rf_trained and self.rf_model:
            try:
                rf_result = self._predict_rf(features)
            except Exception as e:
                print(f"⚠️ 随机森林预测失败: {e}")
        else:
            print(f"⚠️ 随机森林未就绪: trained={self.rf_trained}, model={self.rf_model is not None}")
        
        # 4. 集成融合
        ensemble_probs = self._ensemble_predictions(
            bayesian_result, nn_result, rf_result
        )
        
        # 5. 计算模型一致性
        agreement, disagreement = self._compute_agreement(
            bayesian_result, nn_result, rf_result
        )
        
        # 6. 确定最终预测
        final_probs = ensemble_probs
        final_pred = self._probs_to_prediction(final_probs)
        final_confidence = max(final_probs.values()) - min(final_probs.values())
        
        return EnsemblePrediction(
            home_code=home.get('code', ''),
            home_name_cn=home.get('name_cn', ''),
            away_code=away.get('code', ''),
            away_name_cn=away.get('name_cn', ''),
            
            bayesian_pred=bayesian_result,
            nn_pred=nn_result,
            rf_pred=rf_result,
            
            ensemble_home_prob=final_probs['home_win'],
            ensemble_draw_prob=final_probs['draw'],
            ensemble_away_prob=final_probs['away_win'],
            ensemble_prediction=final_pred,
            ensemble_confidence=final_confidence,
            
            model_agreement=agreement,
            disagreement_details=disagreement,
            
            model_weights=self.model_weights.copy()
        )
    
    def _compute_features(self, home: Dict, away: Dict, stage: str) -> Dict[str, float]:
        """计算比赛特征"""
        # Elo差异
        elo_diff = (home.get('elo', 1500) - away.get('elo', 1500)) / 300
        
        # 排名差异
        rank_diff = (away.get('rank', 50) - home.get('rank', 50)) / 50
        
        # 状态差异（简化）
        home_form = self._parse_form(home.get('form', 'WDWDW'))
        away_form = self._parse_form(away.get('form', 'WDWDW'))
        form_diff = (home_form - away_form) / 5
        
        # 阶段因子
        stage_factor = {
            'GROUP': 0.0, 'R16': 0.2, 'QF': 0.4, 'SF': 0.6, 'F': 0.8
        }.get(stage, 0.0)
        
        # 主场优势
        home_advantage = 0.15 if not home.get('neutral', True) else 0.0
        
        # 洲际因素
        continent_factor = self._compute_continent_factor(home, away)
        
        # 其他特征（简化）
        h2h = 0.0
        wc_experience = (home.get('wc_participations', 5) - away.get('wc_participations', 5)) / 10
        squad_strength = (home.get('squad_rating', 75) - away.get('squad_rating', 75)) / 20
        coach_rating = (home.get('coach_rating', 70) - away.get('coach_rating', 70)) / 20
        venue_factor = 0.0
        
        return {
            'elo_diff': elo_diff,
            'rank_diff': rank_diff,
            'form_diff': form_diff,
            'stage_factor': stage_factor,
            'home_advantage': home_advantage,
            'continent_factor': continent_factor,
            'h2h': h2h,
            'wc_experience': wc_experience,
            'squad_strength': squad_strength,
            'coach_rating': coach_rating,
            'venue_factor': venue_factor
        }
    
    def _parse_form(self, form: str) -> float:
        """解析近期状态"""
        score = 0
        for c in form[:5]:
            if c == 'W':
                score += 3
            elif c == 'D':
                score += 1
        return score
    
    def _compute_continent_factor(self, home: Dict, away: Dict) -> float:
        """计算洲际因素"""
        home_continent = home.get('continent', '')
        away_continent = away.get('continent', '')
        
        # 欧洲对其他洲有优势
        if home_continent == '欧洲' and away_continent != '欧洲':
            return 0.1
        elif away_continent == '欧洲' and home_continent != '欧洲':
            return -0.1
        return 0.0
    
    def _predict_bayesian(self, home: Dict, away: Dict, stage: str) -> ModelPrediction:
        """贝叶斯模型预测"""
        from services.prediction_engine_v4 import PredictionEngineV4
        
        engine = PredictionEngineV4()
        v4_result = engine.predict_match(home, away, stage)
        
        return ModelPrediction(
            model_name='贝叶斯模型',
            home_win_prob=v4_result.home_win_prob,
            draw_prob=v4_result.draw_prob,
            away_win_prob=v4_result.away_win_prob,
            confidence=v4_result.confidence_value,
            features_used=['elo_diff', 'rank_diff', 'form_diff', 'stage_factor']
        )
    
    def _predict_nn(self, features: Dict[str, float]) -> ModelPrediction:
        """神经网络预测"""
        probs = self.nn_model.predict(features)
        
        return ModelPrediction(
            model_name='神经网络',
            home_win_prob=probs['home_win'],
            draw_prob=probs['draw'],
            away_win_prob=probs['away_win'],
            confidence=max(probs.values()) - min(probs.values()),
            features_used=list(features.keys())
        )
    
    def _predict_rf(self, features: Dict[str, float]) -> ModelPrediction:
        """随机森林预测"""
        probs = self.rf_model.predict(features)
        
        return ModelPrediction(
            model_name='随机森林',
            home_win_prob=probs['home_win'],
            draw_prob=probs['draw'],
            away_win_prob=probs['away_win'],
            confidence=max(probs.values()) - min(probs.values()),
            features_used=list(features.keys())
        )
    
    def _ensemble_predictions(
        self,
        bayesian: ModelPrediction,
        nn: Optional[ModelPrediction],
        rf: Optional[ModelPrediction]
    ) -> Dict[str, float]:
        """
        融合多模型预测
        
        加权平均法
        """
        total_weight = 0.0
        weighted_home = 0.0
        weighted_draw = 0.0
        weighted_away = 0.0
        
        # 贝叶斯
        w = self.model_weights['bayesian']
        weighted_home += w * bayesian.home_win_prob
        weighted_draw += w * bayesian.draw_prob
        weighted_away += w * bayesian.away_win_prob
        total_weight += w
        
        # 神经网络
        if nn and self.nn_trained:
            w = self.model_weights['neural_network']
            weighted_home += w * nn.home_win_prob
            weighted_draw += w * nn.draw_prob
            weighted_away += w * nn.away_win_prob
            total_weight += w
        
        # 随机森林
        if rf and self.rf_trained:
            w = self.model_weights['random_forest']
            weighted_home += w * rf.home_win_prob
            weighted_draw += w * rf.draw_prob
            weighted_away += w * rf.away_win_prob
            total_weight += w
        
        # 归一化
        if total_weight > 0:
            weighted_home /= total_weight
            weighted_draw /= total_weight
            weighted_away /= total_weight
        
        return {
            'home_win': weighted_home,
            'draw': weighted_draw,
            'away_win': weighted_away
        }
    
    def _compute_agreement(
        self,
        bayesian: ModelPrediction,
        nn: Optional[ModelPrediction],
        rf: Optional[ModelPrediction]
    ) -> Tuple[float, str]:
        """
        计算模型一致性
        
        Returns:
            (一致性分数, 差异描述)
        """
        predictions = []
        
        # 收集各模型的预测结果
        for pred in [bayesian, nn, rf]:
            if pred:
                max_prob = max(pred.home_win_prob, pred.draw_prob, pred.away_win_prob)
                if pred.home_win_prob == max_prob:
                    predictions.append('主胜')
                elif pred.draw_prob == max_prob:
                    predictions.append('平局')
                else:
                    predictions.append('客胜')
        
        # 计算一致性
        if len(predictions) == 0:
            return 0.0, '无模型预测'
        
        # 统计预测分布
        from collections import Counter
        counter = Counter(predictions)
        most_common = counter.most_common(1)[0]
        agreement = most_common[1] / len(predictions)
        
        # 差异描述
        if agreement == 1.0:
            details = f'所有模型一致预测: {most_common[0]}'
        elif agreement >= 0.66:
            details = f'多数模型预测: {most_common[0]} (有分歧)'
        else:
            details = f'模型分歧较大: {", ".join(predictions)}'
        
        return agreement, details
    
    def _probs_to_prediction(self, probs: Dict[str, float]) -> str:
        """概率转预测结果"""
        if probs['home_win'] > probs['draw'] and probs['home_win'] > probs['away_win']:
            return '主胜'
        elif probs['away_win'] > probs['draw']:
            return '客胜'
        else:
            return '平局'
    
    def update_weights(self, new_weights: Dict[str, float]) -> Dict:
        """
        更新模型权重（在线学习）
        
        Args:
            new_weights: 新权重 {'bayesian': 0.4, 'neural_network': 0.3, ...}
        
        Returns:
            更新后的权重
        """
        # 验证权重
        for model in self.model_weights:
            if model in new_weights:
                self.model_weights[model] = max(0.0, min(1.0, new_weights[model]))
        
        # 归一化
        total = sum(self.model_weights.values())
        if total > 0:
            for model in self.model_weights:
                self.model_weights[model] /= total
        
        return self.model_weights.copy()
    
    def record_performance(self, model_name: str, is_correct: bool):
        """
        记录模型表现（用于在线学习）
        """
        key = model_name.lower().replace(' ', '_')
        if key in self.performance_metrics:
            self.performance_metrics[key]['total'] += 1
            if is_correct:
                self.performance_metrics[key]['correct'] += 1
    
    def get_model_performance(self) -> Dict[str, float]:
        """
        获取各模型准确率
        """
        performance = {}
        for model, stats in self.performance_metrics.items():
            if stats['total'] > 0:
                performance[model] = stats['correct'] / stats['total']
            else:
                performance[model] = 0.0
        return performance
    
    def auto_adjust_weights(self) -> Dict:
        """
        自动调整权重（基于历史表现）
        """
        performance = self.get_model_performance()
        
        # 如果有足够数据，根据准确率调整权重
        total_correct = sum(
            self.performance_metrics[m]['correct'] 
            for m in performance 
            if self.performance_metrics[m]['total'] > 0
        )
        
        if total_correct > 0:
            new_weights = {}
            for model in self.model_weights:
                if model in performance and performance[model] > 0:
                    # 准确率越高，权重越大
                    new_weights[model] = performance[model]
                else:
                    new_weights[model] = self.model_weights[model]
            
            self.update_weights(new_weights)
        
        return self.model_weights.copy()


# 单例
_ensemble_instance = None

def get_ensemble() -> ModelEnsemble:
    """获取集成模型实例"""
    global _ensemble_instance
    if _ensemble_instance is None:
        _ensemble_instance = ModelEnsemble()
    return _ensemble_instance
