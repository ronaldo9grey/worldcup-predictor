"""
随机森林集成学习模型
使用多棵决策树进行集成预测，提高预测准确性和稳定性
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
import json
from collections import Counter


class DecisionTree:
    """
    决策树类
    
    用于随机森林的单棵树
    """
    
    def __init__(self, max_depth: int = 10, min_samples_split: int = 2):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.tree = None
    
    def fit(self, X: np.ndarray, y: np.ndarray):
        """训练决策树"""
        self.tree = self._build_tree(X, y, depth=0)
    
    def _build_tree(self, X: np.ndarray, y: np.ndarray, depth: int) -> Dict:
        """递归构建决策树"""
        n_samples = len(y)
        
        # 停止条件
        if depth >= self.max_depth or n_samples < self.min_samples_split:
            return {'leaf': True, 'class': self._most_common_class(y)}
        
        # 找最佳分割
        best_feature, best_threshold = self._find_best_split(X, y)
        
        if best_feature is None:
            return {'leaf': True, 'class': self._most_common_class(y)}
        
        # 分割数据
        left_mask = X[:, best_feature] <= best_threshold
        right_mask = ~left_mask
        
        if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:
            return {'leaf': True, 'class': self._most_common_class(y)}
        
        # 递归构建子树
        left_tree = self._build_tree(X[left_mask], y[left_mask], depth + 1)
        right_tree = self._build_tree(X[right_mask], y[right_mask], depth + 1)
        
        return {
            'leaf': False,
            'feature': best_feature,
            'threshold': best_threshold,
            'left': left_tree,
            'right': right_tree
        }
    
    def _find_best_split(self, X: np.ndarray, y: np.ndarray) -> Tuple[Optional[int], Optional[float]]:
        """找到最佳分割点"""
        best_gain = -1
        best_feature = None
        best_threshold = None
        
        n_features = X.shape[1]
        
        for feature in range(n_features):
            thresholds = np.unique(X[:, feature])
            
            for threshold in thresholds:
                left_mask = X[:, feature] <= threshold
                right_mask = ~left_mask
                
                if np.sum(left_mask) == 0 or np.sum(right_mask) == 0:
                    continue
                
                gain = self._information_gain(y, y[left_mask], y[right_mask])
                
                if gain > best_gain:
                    best_gain = gain
                    best_feature = feature
                    best_threshold = threshold
        
        return best_feature, best_threshold
    
    def _information_gain(self, parent: np.ndarray, left: np.ndarray, right: np.ndarray) -> float:
        """计算信息增益"""
        parent_entropy = self._entropy(parent)
        left_entropy = self._entropy(left)
        right_entropy = self._entropy(right)
        
        n_parent = len(parent)
        n_left = len(left)
        n_right = len(right)
        
        weighted_entropy = (n_left / n_parent) * left_entropy + (n_right / n_parent) * right_entropy
        
        return parent_entropy - weighted_entropy
    
    def _entropy(self, y: np.ndarray) -> float:
        """计算熵"""
        if len(y) == 0:
            return 0
        
        counts = np.bincount(y)
        probs = counts / len(y)
        
        return -np.sum([p * np.log2(p + 1e-8) for p in probs if p > 0])
    
    def _most_common_class(self, y: np.ndarray) -> int:
        """找到最常见的类别"""
        if len(y) == 0:
            return 0
        return int(np.bincount(y).argmax())
    
    def predict_single(self, x: np.ndarray) -> int:
        """预测单个样本"""
        return self._predict_tree(x, self.tree)
    
    def _predict_tree(self, x: np.ndarray, tree: Dict) -> int:
        """递归预测"""
        if tree['leaf']:
            return tree['class']
        
        if x[tree['feature']] <= tree['threshold']:
            return self._predict_tree(x, tree['left'])
        else:
            return self._predict_tree(x, tree['right'])


class RandomForestClassifier:
    """
    随机森林分类器
    
    集成多棵决策树，使用bagging和随机特征选择
    """
    
    def __init__(self, n_estimators: int = 100, max_depth: int = 10,
                 min_samples_split: int = 2, max_features: str = 'sqrt'):
        """
        初始化随机森林
        
        Args:
            n_estimators: 树的数量
            max_depth: 树的最大深度
            min_samples_split: 分割所需最小样本数
            max_features: 每棵树使用的最大特征数
        """
        self.n_estimators = n_estimators
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.max_features = max_features
        self.trees = []
        self.feature_importances_ = None
        self.is_trained = False
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'RandomForestClassifier':
        """
        训练随机森林
        
        Args:
            X: 特征矩阵 (n_samples, n_features)
            y: 标签向量 (n_samples,)
        
        Returns:
            self
        """
        n_samples, n_features = X.shape
        
        # 计算每棵树使用的特征数
        if self.max_features == 'sqrt':
            max_feat = int(np.sqrt(n_features))
        elif self.max_features == 'log2':
            max_feat = int(np.log2(n_features))
        else:
            max_feat = n_features
        
        self.trees = []
        feature_importance_sum = np.zeros(n_features)
        
        for i in range(self.n_estimators):
            # Bootstrap采样
            indices = np.random.choice(n_samples, n_samples, replace=True)
            X_bootstrap = X[indices]
            y_bootstrap = y[indices]
            
            # 创建并训练决策树
            tree = DecisionTree(max_depth=self.max_depth, 
                               min_samples_split=self.min_samples_split)
            
            # 随机选择特征（简化实现）
            tree_features = np.random.choice(n_features, max_feat, replace=False)
            tree.fit(X_bootstrap[:, tree_features], y_bootstrap)
            
            self.trees.append({'tree': tree, 'features': tree_features})
            
            # 累积特征重要性
            feature_importance_sum[tree_features] += 1
            
            if (i + 1) % 20 == 0:
                print(f"训练进度: {i+1}/{self.n_estimators} 棵树")
        
        # 归一化特征重要性
        self.feature_importances_ = feature_importance_sum / self.n_estimators
        self.is_trained = True
        
        return self
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """
        预测
        
        Args:
            X: 特征矩阵
        
        Returns:
            预测标签
        """
        predictions = []
        
        for i, x in enumerate(X):
            votes = []
            
            for tree_dict in self.trees:
                tree = tree_dict['tree']
                features = tree_dict['features']
                pred = tree.predict_single(x[features])
                votes.append(pred)
            
            # 多数投票
            most_common = Counter(votes).most_common(1)[0][0]
            predictions.append(most_common)
        
        return np.array(predictions)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """
        预测概率
        
        Args:
            X: 特征矩阵
        
        Returns:
            概率矩阵 (n_samples, n_classes)
        """
        n_samples = len(X)
        n_classes = 3  # 主胜、平局、客胜
        proba = np.zeros((n_samples, n_classes))
        
        for i, x in enumerate(X):
            votes = []
            
            for tree_dict in self.trees:
                tree = tree_dict['tree']
                features = tree_dict['features']
                pred = tree.predict_single(x[features])
                votes.append(pred)
            
            # 计算每个类别的投票比例
            vote_counts = Counter(votes)
            total_votes = len(votes)
            
            for cls, count in vote_counts.items():
                if cls < n_classes:
                    proba[i, cls] = count / total_votes
        
        return proba
    
    def get_feature_importance(self, feature_names: List[str] = None) -> Dict[str, float]:
        """获取特征重要性"""
        if self.feature_importances_ is None:
            return {}
        
        if feature_names is None:
            feature_names = [f'feature_{i}' for i in range(len(self.feature_importances_))]
        
        importance_dict = {}
        for name, importance in zip(feature_names, self.feature_importances_):
            importance_dict[name] = float(importance)
        
        return importance_dict


class RandomForestPredictor:
    """
    随机森林预测器
    
    封装随机森林分类器，提供预测接口
    """
    
    def __init__(self, n_estimators: int = 100):
        self.model = RandomForestClassifier(n_estimators=n_estimators)
        self.feature_names = [
            'elo_diff', 'rank_diff', 'form_diff', 'stage_factor',
            'home_advantage', 'continent_factor', 'h2h', 'wc_experience',
            'squad_strength', 'coach_rating', 'venue_factor',
            'elo_form_combined', 'rank_stage_combined'
        ]
    
    def train(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """
        训练模型
        
        Returns:
            训练信息
        """
        self.model.fit(X, y)
        
        # 获取特征重要性
        importance = self.model.get_feature_importance(self.feature_names)
        
        # 计算训练准确率
        predictions = self.model.predict(X)
        accuracy = np.mean(predictions == y)
        
        return {
            'accuracy': accuracy,
            'feature_importance': importance,
            'n_estimators': self.model.n_estimators
        }
    
    def predict(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        预测比赛结果
        """
        # 提取特征向量
        feature_vector = np.zeros(len(self.feature_names))
        for i, name in enumerate(self.feature_names):
            feature_vector[i] = features.get(name, 0.0)
        
        # 预测概率
        proba = self.model.predict_proba(feature_vector.reshape(1, -1))[0]
        
        return {
            'home_win': float(proba[0]),
            'draw': float(proba[1]),
            'away_win': float(proba[2])
        }
    
    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性"""
        return self.model.get_feature_importance(self.feature_names)
    
    def save_model(self, path: str):
        """保存模型"""
        import pickle
        with open(path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'feature_names': self.feature_names
            }, f)
    
    def load_model(self, path: str):
        """加载模型"""
        import pickle
        with open(path, 'rb') as f:
            data = pickle.load(f)
            self.model = data['model']
            self.feature_names = data['feature_names']


def create_random_forest(n_estimators: int = 100) -> RandomForestPredictor:
    """创建随机森林预测器"""
    return RandomForestPredictor(n_estimators=n_estimators)
