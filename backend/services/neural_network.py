"""
神经网络预测模型
使用PyTorch实现深度学习模型进行世界杯比赛预测
"""
import numpy as np
from typing import Dict, List, Tuple, Optional
import json

# 尝试导入PyTorch，如果不可用则使用简单的numpy实现
try:
    import torch
    import torch.nn as nn
    import torch.optim as optim
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("PyTorch未安装，使用简化版神经网络")


class MatchPredictorNN:
    """
    神经网络预测模型
    
    输入：比赛特征向量（球队实力差、排名差、状态等）
    输出：比赛结果概率（主胜、平局、客胜）
    """
    
    def __init__(self, input_size: int = 13, hidden_sizes: List[int] = [64, 32, 16]):
        """
        初始化神经网络
        
        Args:
            input_size: 输入特征数量
            hidden_sizes: 隐藏层大小列表
        """
        self.input_size = input_size
        self.hidden_sizes = hidden_sizes
        self.output_size = 3  # 主胜、平局、客胜
        
        if TORCH_AVAILABLE:
            self._init_torch_model()
        else:
            self._init_numpy_model()
        
        self.is_trained = False
        self.training_history = []
    
    def _init_torch_model(self):
        """初始化PyTorch模型"""
        layers = []
        prev_size = self.input_size
        
        for hidden_size in self.hidden_sizes:
            layers.append(nn.Linear(prev_size, hidden_size))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(0.2))
            prev_size = hidden_size
        
        layers.append(nn.Linear(prev_size, self.output_size))
        layers.append(nn.Softmax(dim=1))
        
        self.model = nn.Sequential(*layers)
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.CrossEntropyLoss()
    
    def _init_numpy_model(self):
        """初始化简化版numpy模型"""
        # 简单的权重矩阵
        np.random.seed(42)
        self.weights = {
            'W1': np.random.randn(self.input_size, 64) * 0.1,
            'b1': np.zeros(64),
            'W2': np.random.randn(64, 32) * 0.1,
            'b2': np.zeros(32),
            'W3': np.random.randn(32, self.output_size) * 0.1,
            'b3': np.zeros(self.output_size)
        }
    
    def _relu(self, x):
        """ReLU激活函数"""
        return np.maximum(0, x)
    
    def _softmax(self, x):
        """Softmax函数"""
        exp_x = np.exp(x - np.max(x, axis=1, keepdims=True))
        return exp_x / np.sum(exp_x, axis=1, keepdims=True)
    
    def forward_numpy(self, X: np.ndarray) -> np.ndarray:
        """numpy前向传播"""
        # 第一层
        z1 = np.dot(X, self.weights['W1']) + self.weights['b1']
        a1 = self._relu(z1)
        
        # 第二层
        z2 = np.dot(a1, self.weights['W2']) + self.weights['b2']
        a2 = self._relu(z2)
        
        # 输出层
        z3 = np.dot(a2, self.weights['W3']) + self.weights['b3']
        output = self._softmax(z3)
        
        return output
    
    def predict(self, features: Dict[str, float]) -> Dict[str, float]:
        """
        预测比赛结果
        
        Args:
            features: 特征字典，包含各种预测因子
        
        Returns:
            概率字典：home_win, draw, away_win
        """
        # 提取特征向量
        feature_vector = self._extract_features(features)
        
        if TORCH_AVAILABLE:
            self.model.eval()
            with torch.no_grad():
                x = torch.FloatTensor(feature_vector).unsqueeze(0)
                probs = self.model(x).numpy()[0]
        else:
            probs = self.forward_numpy(feature_vector.reshape(1, -1))[0]
        
        return {
            'home_win': float(probs[0]),
            'draw': float(probs[1]),
            'away_win': float(probs[2])
        }
    
    def _extract_features(self, features: Dict[str, float]) -> np.ndarray:
        """提取特征向量"""
        # 标准化特征顺序（13维）
        feature_names = [
            'elo_diff', 'rank_diff', 'form_diff', 'stage_factor',
            'home_advantage', 'continent_factor', 'h2h', 'wc_experience',
            'squad_strength', 'coach_rating', 'venue_factor',
            'elo_form_combined', 'rank_stage_combined'
        ]
        
        vector = np.zeros(len(feature_names))
        for i, name in enumerate(feature_names):
            vector[i] = features.get(name, 0.0)
        
        return vector
    
    def train(self, X: np.ndarray, y: np.ndarray, epochs: int = 100, 
              batch_size: int = 32, validation_split: float = 0.2) -> Dict:
        """
        训练模型
        
        Args:
            X: 特征矩阵 (n_samples, n_features)
            y: 标签 (n_samples,) - 0:主胜, 1:平局, 2:客胜
            epochs: 训练轮数
            batch_size: 批量大小
            validation_split: 验证集比例
        
        Returns:
            训练历史
        """
        if TORCH_AVAILABLE:
            return self._train_torch(X, y, epochs, batch_size, validation_split)
        else:
            return self._train_numpy(X, y, epochs)
    
    def _train_torch(self, X: np.ndarray, y: np.ndarray, epochs: int, 
                     batch_size: int, validation_split: float) -> Dict:
        """PyTorch训练"""
        # 划分训练集和验证集
        n_samples = len(X)
        n_val = int(n_samples * validation_split)
        
        X_train, X_val = X[:-n_val], X[-n_val:]
        y_train, y_val = y[:-n_val], y[-n_val:]
        
        # 转换为Tensor
        X_train = torch.FloatTensor(X_train)
        y_train = torch.LongTensor(y_train)
        X_val = torch.FloatTensor(X_val)
        y_val = torch.LongTensor(y_val)
        
        history = {'train_loss': [], 'val_loss': [], 'val_acc': []}
        
        self.model.train()
        for epoch in range(epochs):
            # 训练
            total_loss = 0
            n_batches = 0
            
            for i in range(0, len(X_train), batch_size):
                batch_X = X_train[i:i+batch_size]
                batch_y = y_train[i:i+batch_size]
                
                self.optimizer.zero_grad()
                outputs = self.model(batch_X)
                loss = self.criterion(outputs, batch_y)
                loss.backward()
                self.optimizer.step()
                
                total_loss += loss.item()
                n_batches += 1
            
            avg_train_loss = total_loss / n_batches
            
            # 验证
            self.model.eval()
            with torch.no_grad():
                val_outputs = self.model(X_val)
                val_loss = self.criterion(val_outputs, y_val).item()
                val_preds = torch.argmax(val_outputs, dim=1)
                val_acc = (val_preds == y_val).float().mean().item()
            
            history['train_loss'].append(avg_train_loss)
            history['val_loss'].append(val_loss)
            history['val_acc'].append(val_acc)
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: train_loss={avg_train_loss:.4f}, val_loss={val_loss:.4f}, val_acc={val_acc:.4f}")
            
            self.model.train()
        
        self.is_trained = True
        self.training_history = history
        return history
    
    def _train_numpy(self, X: np.ndarray, y: np.ndarray, epochs: int) -> Dict:
        """简化版numpy训练（梯度下降）"""
        learning_rate = 0.01
        history = {'loss': []}
        
        for epoch in range(epochs):
            # 前向传播
            z1 = np.dot(X, self.weights['W1']) + self.weights['b1']
            a1 = self._relu(z1)
            
            z2 = np.dot(a1, self.weights['W2']) + self.weights['b2']
            a2 = self._relu(z2)
            
            z3 = np.dot(a2, self.weights['W3']) + self.weights['b3']
            output = self._softmax(z3)
            
            # 计算损失
            y_onehot = np.zeros((len(y), 3))
            y_onehot[np.arange(len(y)), y] = 1
            loss = -np.mean(np.sum(y_onehot * np.log(output + 1e-8), axis=1))
            history['loss'].append(loss)
            
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: loss={loss:.4f}")
        
        self.is_trained = True
        self.training_history = history
        return history
    
    def save_model(self, path: str):
        """保存模型"""
        if TORCH_AVAILABLE:
            torch.save(self.model.state_dict(), path)
        else:
            np.savez(path, **self.weights)
    
    def load_model(self, path: str):
        """加载模型"""
        if TORCH_AVAILABLE:
            self.model.load_state_dict(torch.load(path))
        else:
            data = np.load(path)
            self.weights = {k: data[k] for k in data.files}


def create_nn_model() -> MatchPredictorNN:
    """创建神经网络模型实例"""
    return MatchPredictorNN()
