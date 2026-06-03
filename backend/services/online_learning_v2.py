"""
在线学习系统 V2 - P0优化版
新增：
1. 阶段自适应学习率
2. 模型参数微调（不仅是权重）
3. 动态滑动窗口
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import os
from dataclasses import dataclass, asdict


@dataclass
class LearningEventV2:
    """学习事件V2"""
    timestamp: str
    match_id: str
    home_code: str
    away_code: str
    stage: str
    predicted: str
    actual: str
    is_correct: bool
    model_used: str
    confidence: float
    
    # 权重变化
    weights_before: Dict[str, float]
    weights_after: Dict[str, float]
    
    # 新增：模型参数变化
    nn_loss_before: Optional[float] = None
    nn_loss_after: Optional[float] = None
    
    # 学习信息
    learning_rate: float = 0.1
    adjustment_reason: str = ""


class OnlineLearningV2:
    """
    在线学习系统 V2
    
    P0优化：
    1. 阶段自适应学习率（小组赛慢学、决赛快学）
    2. 模型参数微调（神经网络增量训练）
    3. 动态滑动窗口（根据数据密度调整）
    """
    
    def __init__(self, data_path: str = "/var/www/worldcup-predictor/backend/data"):
        self.data_path = data_path
        self.learning_log_path = os.path.join(data_path, "online_learning_v2_log.json")
        
        # 学习历史
        self.learning_history: List[LearningEventV2] = []
        
        # 性能追踪
        self.window_size_min = 20   # 最小窗口
        self.window_size_max = 100  # 最大窗口
        self.window_size = 50       # 当前窗口
        self.recent_predictions: List[Dict] = []
        
        # 分阶段性能追踪（新增）
        self.stage_performance = {
            'GROUP': {'correct': 0, 'total': 0},
            'R16': {'correct': 0, 'total': 0},
            'QF': {'correct': 0, 'total': 0},
            'SF': {'correct': 0, 'total': 0},
            'FI': {'correct': 0, 'total': 0},
        }
        
        # 阶段自适应学习率（新增）
        self.stage_learning_rates = {
            'GROUP': 0.08,      # 小组赛样本多，慢学
            'R16': 0.10,        # 16强
            'QF': 0.12,         # 8强，加快
            'SF': 0.15,         # 4强，更快
            'FI': 0.20,         # 决赛，最快响应
        }
        
        # 概念漂移检测
        self.drift_threshold = 0.15
        self.baseline_accuracy = 0.53
        self.stage_baselines = {
            'GROUP': 0.50,
            'R16': 0.55,
            'QF': 0.52,
            'SF': 0.50,
            'FI': 0.48,
        }
        
        # 当前学习率
        self.current_learning_rate = 0.1
        
        # 模型引用（用于参数微调）
        self.nn_model = None
        self.rf_model = None
        
        # 加载历史
        self._load_history()
    
    def set_models(self, nn_model=None, rf_model=None):
        """设置模型引用（用于参数微调）"""
        self.nn_model = nn_model
        self.rf_model = rf_model
    
    def _load_history(self):
        """加载历史记录"""
        if os.path.exists(self.learning_log_path):
            try:
                with open(self.learning_log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learning_history = [LearningEventV2(**e) for e in data.get('events', [])]
            except Exception as e:
                print(f"加载历史记录失败: {e}")
    
    def _save_history(self):
        """保存历史记录"""
        try:
            data = {
                'events': [asdict(e) for e in self.learning_history[-100:]],
                'last_updated': datetime.now().isoformat()
            }
            with open(self.learning_log_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存历史记录失败: {e}")
    
    def process_match_result(
        self,
        match_id: str,
        home_code: str,
        away_code: str,
        stage: str,
        predicted: str,
        actual: str,
        model_used: str,
        confidence: float,
        current_weights: Dict[str, float],
        features: Optional[Dict] = None
    ) -> Dict:
        """
        处理比赛结果，在线学习V2
        
        新增：
        1. 根据阶段调整学习率
        2. 神经网络增量训练
        3. 动态调整窗口大小
        """
        is_correct = predicted == actual
        
        # 记录预测
        prediction_record = {
            'match_id': match_id,
            'stage': stage,
            'predicted': predicted,
            'actual': actual,
            'is_correct': is_correct,
            'confidence': confidence,
            'model_used': model_used,
            'timestamp': datetime.now().isoformat()
        }
        self.recent_predictions.append(prediction_record)
        
        # 更新阶段性能
        stage_key = self._normalize_stage(stage)
        if stage_key in self.stage_performance:
            self.stage_performance[stage_key]['total'] += 1
            if is_correct:
                self.stage_performance[stage_key]['correct'] += 1
        
        # 动态调整窗口大小（新增）
        self._adjust_window_size(stage)
        
        # 保持窗口大小
        if len(self.recent_predictions) > self.window_size:
            self.recent_predictions = self.recent_predictions[-self.window_size:]
        
        # 阶段自适应学习率（新增）
        stage_learning_rate = self._get_stage_learning_rate(stage)
        
        # 计算准确率
        recent_accuracy = self._compute_recent_accuracy()
        stage_accuracy = self._compute_stage_accuracy(stage_key)
        
        # 检测概念漂移
        drift_warning, drift_details = self._detect_concept_drift(recent_accuracy, stage_accuracy, stage_key)
        
        # 调整权重
        new_weights, adjustment_reason = self._adjust_weights_v2(
            current_weights, is_correct, model_used, confidence,
            recent_accuracy, stage_accuracy, stage,
            drift_warning, stage_learning_rate
        )
        
        # 神经网络增量训练（新增）
        nn_loss_before = None
        nn_loss_after = None
        
        if self.nn_model and features and is_correct is False:
            # 错误预测时，进行增量训练
            nn_loss_before = getattr(self.nn_model, 'last_loss', None)
            self._incremental_nn_train(features, actual)
            nn_loss_after = getattr(self.nn_model, 'last_loss', None)
        
        # 记录学习事件
        event = LearningEventV2(
            timestamp=datetime.now().isoformat(),
            match_id=match_id,
            home_code=home_code,
            away_code=away_code,
            stage=stage,
            predicted=predicted,
            actual=actual,
            is_correct=is_correct,
            model_used=model_used,
            confidence=confidence,
            weights_before=current_weights.copy(),
            weights_after=new_weights.copy(),
            nn_loss_before=nn_loss_before,
            nn_loss_after=nn_loss_after,
            learning_rate=stage_learning_rate,
            adjustment_reason=adjustment_reason
        )
        self.learning_history.append(event)
        
        # 保存
        self._save_history()
        
        return {
            'is_correct': is_correct,
            'new_weights': new_weights,
            'weight_adjusted': new_weights != current_weights,
            'adjustment_reason': adjustment_reason,
            'recent_accuracy': recent_accuracy,
            'stage_accuracy': stage_accuracy,
            'current_window_size': self.window_size,
            'drift_warning': drift_warning,
            'drift_details': drift_details,
            'learning_rate': stage_learning_rate,
            'nn_incremental_train': nn_loss_after is not None,
        }
    
    def _normalize_stage(self, stage: str) -> str:
        """标准化阶段名称"""
        stage_map = {
            'GROUP': 'GROUP',
            'ROUND_OF_16': 'R16',
            'R16': 'R16',
            'QUARTER_FINAL': 'QF',
            'QF': 'QF',
            'SEMI_FINAL': 'SF',
            'SF': 'SF',
            'FINAL': 'FI',
            'FI': 'FI',
            'THIRD_PLACE': 'FI',
        }
        return stage_map.get(stage.upper(), 'GROUP')
    
    def _adjust_window_size(self, stage: str):
        """
        动态调整滑动窗口大小（新增）
        
        规则：
        - 淘汰赛阶段：减小窗口，更关注近期
        - 小组赛阶段：增大窗口，样本多
        """
        if stage in ['QF', 'SF', 'FI']:
            # 淘汰赛后期，窗口缩小
            self.window_size = max(self.window_size_min, self.window_size - 5)
        elif stage == 'GROUP':
            # 小组赛，窗口增大
            self.window_size = min(self.window_size_max, self.window_size + 2)
    
    def _get_stage_learning_rate(self, stage: str) -> float:
        """
        获取阶段自适应学习率（新增）
        
        规则：
        - 小组赛：样本多，慢学习，避免过拟合
        - 淘汰赛：样本少，快学习，快速适应
        - 决赛：最快响应
        """
        stage_key = self._normalize_stage(stage)
        return self.stage_learning_rates.get(stage_key, 0.1)
    
    def _compute_recent_accuracy(self) -> float:
        """计算近期准确率"""
        if len(self.recent_predictions) == 0:
            return 0.0
        
        correct = sum(1 for p in self.recent_predictions if p['is_correct'])
        return correct / len(self.recent_predictions)
    
    def _compute_stage_accuracy(self, stage: str) -> float:
        """计算阶段准确率"""
        if stage not in self.stage_performance:
            return 0.0
        
        stats = self.stage_performance[stage]
        if stats['total'] == 0:
            return 0.0
        
        return stats['correct'] / stats['total']
    
    def _detect_concept_drift(
        self,
        recent_accuracy: float,
        stage_accuracy: float,
        stage: str
    ) -> Tuple[bool, str]:
        """
        检测概念漂移（优化版）
        
        新增：分阶段检测
        """
        if len(self.recent_predictions) < 10:
            return False, "样本数不足"
        
        # 使用阶段基线
        baseline = self.stage_baselines.get(stage, self.baseline_accuracy)
        
        # 综合漂移
        drift = baseline - recent_accuracy
        
        if drift > self.drift_threshold:
            return True, f"警告: 准确率下降 {drift:.1%}，可能存在概念漂移"
        elif drift > self.drift_threshold * 0.5:
            return False, f"注意: 准确率略降 {drift:.1%}"
        else:
            return False, f"正常: 准确率稳定"
    
    def _adjust_weights_v2(
        self,
        current_weights: Dict[str, float],
        is_correct: bool,
        model_used: str,
        confidence: float,
        recent_accuracy: float,
        stage_accuracy: float,
        stage: str,
        drift_warning: bool,
        stage_learning_rate: float
    ) -> Tuple[Dict[str, float], str]:
        """
        自适应调整权重 V2
        
        新增：
        1. 使用阶段自适应学习率
        2. 根据阶段调整权重范围
        """
        new_weights = current_weights.copy()
        adjustment_reason = ""
        
        # 如果存在概念漂移，增加学习率
        if drift_warning:
            stage_learning_rate *= 1.5
            adjustment_reason = "概念漂移检测，增加学习率; "
        
        # 识别模型
        model_key = self._normalize_model_name(model_used)
        
        if model_key in new_weights:
            if is_correct:
                # 正确预测，增加权重
                adjustment = stage_learning_rate * confidence * 0.1
                new_weights[model_key] = min(0.6, new_weights[model_key] + adjustment)
                adjustment_reason += f"正确预测({stage})，增加{model_key}权重"
            else:
                # 错误预测，减少权重
                adjustment = stage_learning_rate * (1 - confidence) * 0.05
                new_weights[model_key] = max(0.15, new_weights[model_key] - adjustment)
                adjustment_reason += f"错误预测({stage})，减少{model_key}权重"
        
        # 归一化权重
        total = sum(new_weights.values())
        if total > 0:
            for key in new_weights:
                new_weights[key] /= total
        
        if not adjustment_reason:
            adjustment_reason = "权重保持不变"
        
        return new_weights, adjustment_reason
    
    def _normalize_model_name(self, model_name: str) -> str:
        """标准化模型名称"""
        model_name_lower = model_name.lower()
        
        if 'bayesian' in model_name_lower or '贝叶斯' in model_name:
            return 'bayesian'
        elif 'neural' in model_name_lower or '神经网络' in model_name:
            return 'neural_network'
        elif 'forest' in model_name_lower or '森林' in model_name:
            return 'random_forest'
        
        return model_name_lower.replace(' ', '_')
    
    def _incremental_nn_train(self, features: Dict, actual_result: str):
        """
        神经网络增量训练（新增）
        
        只在错误预测时进行少量训练
        """
        if not self.nn_model:
            return
        
        try:
            # 准备单样本训练数据
            X = np.array([list(features.values())])
            
            # 标签编码
            result_map = {'HOME_WIN': 0, 'DRAW': 1, 'AWAY_WIN': 2, '主胜': 0, '平局': 1, '客胜': 2}
            y = np.array([result_map.get(actual_result, 0)])
            
            # 增量训练（少量轮次）
            self.nn_model.train(X, y, epochs=5, batch_size=1, validation_split=0.0)
            
        except Exception as e:
            print(f"神经网络增量训练失败: {e}")
    
    def get_learning_stats(self) -> Dict:
        """获取学习统计"""
        recent_accuracy = self._compute_recent_accuracy()
        
        # 各模型表现
        model_performance = {}
        for model in ['bayesian', 'neural_network', 'random_forest']:
            model_preds = [p for p in self.recent_predictions 
                          if self._normalize_model_name(p.get('model_used', '')) == model]
            if model_preds:
                correct = sum(1 for p in model_preds if p['is_correct'])
                model_performance[model] = correct / len(model_preds)
            else:
                model_performance[model] = None
        
        return {
            'total_events': len(self.learning_history),
            'recent_predictions': len(self.recent_predictions),
            'recent_accuracy': recent_accuracy,
            'baseline_accuracy': self.baseline_accuracy,
            'accuracy_trend': recent_accuracy - self.baseline_accuracy if self.recent_predictions else 0,
            'stage_performance': {
                stage: {
                    'accuracy': stats['correct'] / stats['total'] if stats['total'] > 0 else 0,
                    'total': stats['total']
                }
                for stage, stats in self.stage_performance.items()
            },
            'model_performance': model_performance,
            'learning_rate': self.current_learning_rate,
            'window_size': self.window_size,
            'stage_learning_rates': self.stage_learning_rates,
        }
    
    def reset_learning(self):
        """重置学习状态"""
        self.learning_history = []
        self.recent_predictions = []
        self.current_learning_rate = 0.1
        self.window_size = 50
        self.stage_performance = {
            'GROUP': {'correct': 0, 'total': 0},
            'R16': {'correct': 0, 'total': 0},
            'QF': {'correct': 0, 'total': 0},
            'SF': {'correct': 0, 'total': 0},
            'FI': {'correct': 0, 'total': 0},
        }
        self._save_history()


# 单例
_online_learning_v2_instance = None


def get_online_learning_v2() -> OnlineLearningV2:
    """获取在线学习V2实例"""
    global _online_learning_v2_instance
    if _online_learning_v2_instance is None:
        _online_learning_v2_instance = OnlineLearningV2()
    return _online_learning_v2_instance
