"""
在线学习系统
实时更新模型权重，追踪概念漂移，管理模型版本
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import json
import os
from dataclasses import dataclass, asdict


@dataclass
class LearningEvent:
    """学习事件"""
    timestamp: str
    match_id: str
    home_code: str
    away_code: str
    predicted: str
    actual: str
    is_correct: bool
    model_used: str
    confidence: float
    weights_before: Dict[str, float]
    weights_after: Dict[str, float]
    adjustment_reason: str


class OnlineLearningSystem:
    """
    在线学习系统
    
    功能:
    1. 实时更新模型权重
    2. 追踪模型性能变化
    3. 检测概念漂移
    4. 管理模型版本
    """
    
    def __init__(self, data_path: str = "/var/www/worldcup-predictor/backend/data"):
        self.data_path = data_path
        self.learning_log_path = os.path.join(data_path, "online_learning_log.json")
        
        # 学习历史
        self.learning_history: List[LearningEvent] = []
        
        # 性能追踪（滑动窗口）
        self.window_size = 50  # 最近50场比赛
        self.recent_predictions: List[Dict] = []
        
        # 概念漂移检测
        self.drift_threshold = 0.15  # 准确率下降超过15%触发漂移警告
        self.baseline_accuracy = 0.53  # 基线准确率（历史训练）
        self.recent_accuracy_window = []
        
        # 自适应学习率
        self.learning_rate = 0.1
        self.min_learning_rate = 0.01
        self.max_learning_rate = 0.3
        
        # 加载历史数据
        self._load_history()
    
    def _load_history(self):
        """加载历史学习记录"""
        if os.path.exists(self.learning_log_path):
            try:
                with open(self.learning_log_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learning_history = [LearningEvent(**e) for e in data.get('events', [])]
            except Exception as e:
                print(f"加载历史记录失败: {e}")
    
    def _save_history(self):
        """保存学习记录"""
        try:
            data = {
                'events': [asdict(e) for e in self.learning_history[-100:]],  # 只保留最近100条
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
        predicted: str,
        actual: str,
        model_used: str,
        confidence: float,
        current_weights: Dict[str, float]
    ) -> Dict:
        """
        处理比赛结果，在线学习
        
        Args:
            match_id: 比赛ID
            home_code: 主队代码
            away_code: 客队代码
            predicted: 预测结果
            actual: 实际结果
            model_used: 使用的模型
            confidence: 预测置信度
            current_weights: 当前模型权重
        
        Returns:
            学习结果（新权重、是否调整、漂移警告等）
        """
        is_correct = predicted == actual
        
        # 记录预测
        self.recent_predictions.append({
            'match_id': match_id,
            'predicted': predicted,
            'actual': actual,
            'is_correct': is_correct,
            'confidence': confidence,
            'model_used': model_used,
            'timestamp': datetime.now().isoformat()
        })
        
        # 保持窗口大小
        if len(self.recent_predictions) > self.window_size:
            self.recent_predictions = self.recent_predictions[-self.window_size:]
        
        # 计算近期准确率
        recent_accuracy = self._compute_recent_accuracy()
        
        # 检测概念漂移
        drift_warning, drift_details = self._detect_concept_drift(recent_accuracy)
        
        # 调整权重
        new_weights, adjustment_reason = self._adjust_weights(
            current_weights, is_correct, model_used, confidence, recent_accuracy, drift_warning
        )
        
        # 记录学习事件
        event = LearningEvent(
            timestamp=datetime.now().isoformat(),
            match_id=match_id,
            home_code=home_code,
            away_code=away_code,
            predicted=predicted,
            actual=actual,
            is_correct=is_correct,
            model_used=model_used,
            confidence=confidence,
            weights_before=current_weights.copy(),
            weights_after=new_weights.copy(),
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
            'drift_warning': drift_warning,
            'drift_details': drift_details,
            'learning_rate': self.learning_rate
        }
    
    def _compute_recent_accuracy(self) -> float:
        """计算近期准确率"""
        if len(self.recent_predictions) == 0:
            return 0.0
        
        correct = sum(1 for p in self.recent_predictions if p['is_correct'])
        return correct / len(self.recent_predictions)
    
    def _detect_concept_drift(self, recent_accuracy: float) -> Tuple[bool, str]:
        """
        检测概念漂移
        
        当准确率显著下降时，可能存在概念漂移
        """
        if len(self.recent_predictions) < 10:
            return False, "样本数不足"
        
        drift = self.baseline_accuracy - recent_accuracy
        
        if drift > self.drift_threshold:
            return True, f"警告: 准确率下降 {drift:.1%}，可能存在概念漂移"
        elif drift > self.drift_threshold * 0.5:
            return False, f"注意: 准确率略降 {drift:.1%}"
        else:
            return False, f"正常: 准确率稳定"
    
    def _adjust_weights(
        self,
        current_weights: Dict[str, float],
        is_correct: bool,
        model_used: str,
        confidence: float,
        recent_accuracy: float,
        drift_warning: bool
    ) -> Tuple[Dict[str, float], str]:
        """
        自适应调整权重
        
        根据预测结果动态调整模型权重
        """
        new_weights = current_weights.copy()
        adjustment_reason = ""
        
        # 如果存在概念漂移，增加学习率
        if drift_warning:
            self.learning_rate = min(self.max_learning_rate, self.learning_rate * 1.5)
            adjustment_reason = "概念漂移检测，增加学习率; "
        
        # 根据预测结果调整
        model_key = model_used.lower().replace(' ', '_').replace('模型', '')
        
        # 标准化模型名称
        if 'bayesian' in model_key or '贝叶斯' in model_used:
            model_key = 'bayesian'
        elif 'neural' in model_key or '神经网络' in model_used:
            model_key = 'neural_network'
        elif 'forest' in model_key or '森林' in model_used:
            model_key = 'random_forest'
        
        if model_key in new_weights:
            if is_correct:
                # 正确预测，增加权重
                adjustment = self.learning_rate * confidence * 0.1
                new_weights[model_key] = min(0.7, new_weights[model_key] + adjustment)
                adjustment_reason += f"正确预测，增加{model_key}权重"
            else:
                # 错误预测，减少权重（但保持最小值）
                adjustment = self.learning_rate * (1 - confidence) * 0.05
                new_weights[model_key] = max(0.1, new_weights[model_key] - adjustment)
                adjustment_reason += f"错误预测，减少{model_key}权重"
        
        # 归一化权重
        total = sum(new_weights.values())
        if total > 0:
            for key in new_weights:
                new_weights[key] /= total
        
        # 如果没有调整
        if not adjustment_reason:
            adjustment_reason = "权重保持不变"
        
        # 漂移后逐渐恢复学习率
        if not drift_warning and self.learning_rate > 0.1:
            self.learning_rate = max(0.1, self.learning_rate * 0.9)
        
        return new_weights, adjustment_reason
    
    def get_learning_stats(self) -> Dict:
        """获取学习统计"""
        recent_accuracy = self._compute_recent_accuracy()
        
        # 各模型表现
        model_performance = {}
        for model in ['bayesian', 'neural_network', 'random_forest']:
            model_preds = [p for p in self.recent_predictions 
                          if model.replace('_', ' ') in p.get('model_used', '').lower() or 
                             model in p.get('model_used', '').lower()]
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
            'model_performance': model_performance,
            'learning_rate': self.learning_rate,
            'window_size': self.window_size
        }
    
    def reset_learning(self):
        """重置学习状态"""
        self.learning_history = []
        self.recent_predictions = []
        self.learning_rate = 0.1
        self._save_history()
    
    def export_learning_report(self) -> Dict:
        """导出学习报告"""
        stats = self.get_learning_stats()
        
        # 最近10次调整
        recent_adjustments = []
        for event in self.learning_history[-10:]:
            recent_adjustments.append({
                'match': f"{event.home_code} vs {event.away_code}",
                'predicted': event.predicted,
                'actual': event.actual,
                'result': '✓' if event.is_correct else '✗',
                'weight_change': event.weights_after != event.weights_before,
                'reason': event.adjustment_reason
            })
        
        return {
            'stats': stats,
            'recent_adjustments': recent_adjustments,
            'drift_detection': {
                'threshold': self.drift_threshold,
                'baseline': self.baseline_accuracy,
                'current': stats['recent_accuracy'],
                'status': 'warning' if stats['accuracy_trend'] < -self.drift_threshold else 'normal'
            }
        }


# 单例
_online_learning_instance = None

def get_online_learning() -> OnlineLearningSystem:
    """获取在线学习实例"""
    global _online_learning_instance
    if _online_learning_instance is None:
        _online_learning_instance = OnlineLearningSystem()
    return _online_learning_instance
