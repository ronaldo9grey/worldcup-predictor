"""
模型集成框架 - 支持持久化和版本管理
融合多种机器学习模型（贝叶斯、神经网络、随机森林）进行比赛预测
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import json
import os
import pickle
from datetime import datetime
import uuid

from services.bayesian_model import get_bayesian_model
from services.neural_network import create_nn_model
from services.random_forest import create_random_forest
from services.model_trainer import get_default_trainer
from data.historical_world_cups import get_all_world_cup_matches
from data.world_cup_2026 import get_team_lookup


# 模型存储路径
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'models')
VERSION_FILE = os.path.join(MODEL_DIR, 'model_versions.json')


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
    model_agreement: float
    disagreement_details: str
    
    # 权重信息
    model_weights: Dict[str, float]


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


class ModelEnsemble:
    """
    模型集成器 - 支持持久化和版本管理
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
        
        # 当前模型版本
        self.current_version = None
        
        # 模型权重
        self.model_weights = {
            'bayesian': 0.4,
            'neural_network': 0.3,
            'random_forest': 0.3
        }
        
        # 性能追踪
        self.learning_history = []
        self.performance_metrics = {
            'bayesian': {'correct': 0, 'total': 0},
            'neural_network': {'correct': 0, 'total': 0},
            'random_forest': {'correct': 0, 'total': 0}
        }
    
    def load_model_version(self, version_id: str) -> bool:
        """
        加载指定版本的模型
        
        Args:
            version_id: 版本ID（如 'v1', 'v2'）
        
        Returns:
            是否加载成功
        """
        nn_file = os.path.join(MODEL_DIR, f'nn_model_{version_id}.pkl')
        rf_file = os.path.join(MODEL_DIR, f'rf_model_{version_id}.pkl')
        
        success = False
        
        # 加载神经网络
        if os.path.exists(nn_file):
            try:
                with open(nn_file, 'rb') as f:
                    saved_data = pickle.load(f)
                
                input_size = saved_data.get('input_size', 11)
                self.nn_model = create_nn_model(input_size=input_size)
                
                # 恢复权重（numpy版本）
                if hasattr(self.nn_model, 'weights') and 'weights' in saved_data:
                    self.nn_model.weights = saved_data['weights']
                
                self.nn_model.is_trained = True
                self.nn_trained = True
                print(f"✅ 神经网络 {version_id} 加载成功")
                success = True
            except Exception as e:
                print(f"❌ 神经网络 {version_id} 加载失败: {e}")
        
        # 加载随机森林
        if os.path.exists(rf_file):
            try:
                with open(rf_file, 'rb') as f:
                    self.rf_model = pickle.load(f)
                self.rf_trained = True
                print(f"✅ 随机森林 {version_id} 加载成功")
                success = True
            except Exception as e:
                print(f"❌ 随机森林 {version_id} 加载失败: {e}")
        
        if success:
            self.current_version = version_id
            
            # 更新版本信息
            version_info = load_version_info()
            version_info['current_version'] = version_id
            save_version_info(version_info)
        
        return success
    
    def save_model_version(self, version_id: str, metrics: Dict) -> bool:
        """
        保存模型到指定版本
        
        Args:
            version_id: 版本ID
            metrics: 训练指标（准确率等）
        
        Returns:
            是否保存成功
        """
        os.makedirs(MODEL_DIR, exist_ok=True)
        
        nn_file = os.path.join(MODEL_DIR, f'nn_model_{version_id}.pkl')
        rf_file = os.path.join(MODEL_DIR, f'rf_model_{version_id}.pkl')
        
        # 保存神经网络
        try:
            saved_data = {
                'input_size': 11,  # 默认特征数
                'weights': getattr(self.nn_model, 'weights', {}),
                'model_state': getattr(self.nn_model, 'model', None)
            }
            with open(nn_file, 'wb') as f:
                pickle.dump(saved_data, f)
        except Exception as e:
            print(f"⚠️ 神经网络保存失败: {e}")
        
        # 保存随机森林
        try:
            with open(rf_file, 'wb') as f:
                pickle.dump(self.rf_model, f)
        except Exception as e:
            print(f"⚠️ 随机森林保存失败: {e}")
        
        # 更新版本信息
        version_info = load_version_info()
        
        version_data = {
            "id": version_id,
            "created_at": datetime.now().isoformat(),
            "nn_accuracy": metrics.get('nn_accuracy', 0),
            "rf_accuracy": metrics.get('rf_accuracy', 0),
            "data_source": metrics.get('data_source', '历史数据'),
            "is_active": True
        }
        
        # 将其他版本设为非活跃
        for v in version_info['versions']:
            v['is_active'] = False
        
        version_info['versions'].append(version_data)
        version_info['training_count'] += 1
        version_info['current_version'] = version_id
        
        save_version_info(version_info)
        
        self.current_version = version_id
        print(f"✅ 模型版本 {version_id} 已保存")
        
        return True
    
    def initialize_models(self, force_retrain: bool = False) -> Dict:
        """
        初始化所有模型（支持持久化）
        """
        status = {
            'bayesian': 'ready',
            'neural_network': 'not_trained',
            'random_forest': 'not_trained'
        }
        
        # 如果已有模型实例且不强制重新训练，直接返回
        if self.nn_trained and self.rf_trained and self.nn_model and self.rf_model and not force_retrain:
            status['neural_network'] = 'already_trained'
            status['random_forest'] = 'already_trained'
            return status
        
        # 如果只是标志位为True但模型实例不存在，重置标志位
        if not self.nn_model:
            self.nn_trained = False
        if not self.rf_model:
            self.rf_trained = False
        
        # 尝试加载最新版本
        if not force_retrain:
            version_info = load_version_info()
            current_ver = version_info.get('current_version')
            
            if current_ver:
                if self.load_model_version(current_ver):
                    status['neural_network'] = f'loaded ({current_ver})'
                    status['random_forest'] = f'loaded ({current_ver})'
                    return status
        
        # 没有可用模型，需要训练
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
        rf_accuracy = 0
        try:
            self.rf_model = create_random_forest(n_estimators=100)
            train_result = self.rf_model.train(X, y)
            self.rf_trained = True
            rf_accuracy = train_result.get('accuracy', 0)
            status['random_forest'] = f'trained (accuracy: {rf_accuracy:.1%})'
            status['rf_feature_importance'] = train_result.get('feature_importance', {})
        except Exception as e:
            status['random_forest'] = f'error: {str(e)}'
            import traceback
            traceback.print_exc()
        
        # 保存新版本
        if self.nn_trained and self.rf_trained:
            version_info = load_version_info()
            new_version = f"v{version_info['training_count'] + 1}"
            
            self.save_model_version(new_version, {
                'nn_accuracy': getattr(self.nn_model, 'validation_accuracy', 0.7),
                'rf_accuracy': rf_accuracy,
                'data_source': '2018+2022世界杯'
            })
            
            status['version'] = new_version
        
        return status
    
    def _prepare_training_data(self, matches: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """准备训练数据"""
        X = []
        y = []
        
        for match in matches:
            features = self._extract_match_features(match)
            X.append(list(features.values()))
            
            result = match.get('result', '')
            if result == 'HOME_WIN' or '主胜' in result:
                y.append(0)
            elif result == 'DRAW' or '平局' in result:
                y.append(1)
            else:
                y.append(2)
        
        return np.array(X), np.array(y)
    
    def _extract_match_features(self, match: Dict) -> Dict[str, float]:
        """提取比赛特征（固定11维）"""
        feature_names = [
            'elo_diff', 'rank_diff', 'form_diff', 'stage_factor',
            'home_advantage', 'continent_factor', 'h2h', 'wc_experience',
            'squad_strength', 'coach_rating', 'venue_factor'
        ]
        
        features = {}
        for name in feature_names:
            features[name] = match.get(name, 0.0)
        
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
        """集成预测"""
        features = self._compute_features(home, away, stage)
        
        # 1. 贝叶斯预测
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
        ensemble_probs = self._ensemble_predictions(bayesian_result, nn_result, rf_result)
        
        # 5. 计算一致性
        agreement, disagreement = self._compute_agreement(bayesian_result, nn_result, rf_result)
        
        # 6. 最终预测
        final_pred = self._probs_to_prediction(ensemble_probs)
        final_confidence = max(ensemble_probs.values()) - min(ensemble_probs.values())
        
        return EnsemblePrediction(
            home_code=home.get('code', ''),
            home_name_cn=home.get('name_cn', ''),
            away_code=away.get('code', ''),
            away_name_cn=away.get('name_cn', ''),
            
            bayesian_pred=bayesian_result,
            nn_pred=nn_result,
            rf_pred=rf_result,
            
            ensemble_home_prob=ensemble_probs['home_win'],
            ensemble_draw_prob=ensemble_probs['draw'],
            ensemble_away_prob=ensemble_probs['away_win'],
            ensemble_prediction=final_pred,
            ensemble_confidence=final_confidence,
            
            model_agreement=agreement,
            disagreement_details=disagreement,
            
            model_weights=self.model_weights.copy()
        )
    
    def _compute_features(self, home: Dict, away: Dict, stage: str) -> Dict[str, float]:
        """计算比赛特征"""
        elo_diff = (home.get('elo', 1500) - away.get('elo', 1500)) / 300
        rank_diff = (away.get('rank', 50) - home.get('rank', 50)) / 50
        
        home_form = self._parse_form(home.get('form', 'WDWDW'))
        away_form = self._parse_form(away.get('form', 'WDWDW'))
        form_diff = (home_form - away_form) / 5
        
        stage_factor = {'GROUP': 0.0, 'R16': 0.2, 'QF': 0.4, 'SF': 0.6, 'F': 0.8}.get(stage, 0.0)
        home_advantage = 0.15 if not home.get('neutral', True) else 0.0
        continent_factor = self._compute_continent_factor(home, away)
        
        h2h = 0.0
        wc_experience = (home.get('wc_participations', 5) - away.get('wc_participations', 5)) / 10
        squad_strength = (home.get('squad_rating', 75) - away.get('squad_rating', 75)) / 20
        coach_rating = (home.get('coach_rating', 70) - away.get('coach_rating', 70)) / 20
        venue_factor = 0.0
        
        return {
            'elo_diff': elo_diff, 'rank_diff': rank_diff, 'form_diff': form_diff,
            'stage_factor': stage_factor, 'home_advantage': home_advantage,
            'continent_factor': continent_factor, 'h2h': h2h, 'wc_experience': wc_experience,
            'squad_strength': squad_strength, 'coach_rating': coach_rating, 'venue_factor': venue_factor
        }
    
    def _parse_form(self, form: str) -> float:
        """解析近期状态"""
        score = 0
        for c in form[:5]:
            if c == 'W': score += 3
            elif c == 'D': score += 1
        return score
    
    def _compute_continent_factor(self, home: Dict, away: Dict) -> float:
        """计算洲际因素"""
        home_continent = home.get('continent', '')
        away_continent = away.get('continent', '')
        if home_continent == '欧洲' and away_continent != '欧洲': return 0.1
        elif away_continent == '欧洲' and home_continent != '欧洲': return -0.1
        return 0.0
    
    def _predict_bayesian(self, home: Dict, away: Dict, stage: str) -> ModelPrediction:
        """贝叶斯预测"""
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
        """融合预测"""
        total_weight = 0.0
        weighted_home = 0.0
        weighted_draw = 0.0
        weighted_away = 0.0
        
        w = self.model_weights['bayesian']
        weighted_home += w * bayesian.home_win_prob
        weighted_draw += w * bayesian.draw_prob
        weighted_away += w * bayesian.away_win_prob
        total_weight += w
        
        if nn and self.nn_trained:
            w = self.model_weights['neural_network']
            weighted_home += w * nn.home_win_prob
            weighted_draw += w * nn.draw_prob
            weighted_away += w * nn.away_win_prob
            total_weight += w
        
        if rf and self.rf_trained:
            w = self.model_weights['random_forest']
            weighted_home += w * rf.home_win_prob
            weighted_draw += w * rf.draw_prob
            weighted_away += w * rf.away_win_prob
            total_weight += w
        
        if total_weight > 0:
            weighted_home /= total_weight
            weighted_draw /= total_weight
            weighted_away /= total_weight
        
        return {'home_win': weighted_home, 'draw': weighted_draw, 'away_win': weighted_away}
    
    def _compute_agreement(
        self,
        bayesian: ModelPrediction,
        nn: Optional[ModelPrediction],
        rf: Optional[ModelPrediction]
    ) -> Tuple[float, str]:
        """计算模型一致性"""
        predictions = []
        for pred in [bayesian, nn, rf]:
            if pred:
                max_prob = max(pred.home_win_prob, pred.draw_prob, pred.away_win_prob)
                if pred.home_win_prob == max_prob:
                    predictions.append('主胜')
                elif pred.draw_prob == max_prob:
                    predictions.append('平局')
                else:
                    predictions.append('客胜')
        
        if len(predictions) == 0:
            return 0.0, "无有效预测"
        
        from collections import Counter
        counts = Counter(predictions)
        most_common = counts.most_common(1)[0]
        agreement = most_common[1] / len(predictions)
        
        if agreement == 1.0:
            disagreement = f"三模型一致预测: {most_common[0]}"
        else:
            disagreement = f"预测分歧: {dict(counts)}"
        
        return agreement, disagreement
    
    def _probs_to_prediction(self, probs: Dict[str, float]) -> str:
        """概率转预测结果"""
        if probs['home_win'] >= probs['draw'] and probs['home_win'] >= probs['away_win']:
            return '主胜'
        elif probs['draw'] >= probs['away_win']:
            return '平局'
        else:
            return '客胜'
