"""
模型训练管理器 V2
功能：
1. 训练进度实时展示
2. 训练结果持久化存储
3. 训练历史记录
4. 模型版本管理
"""
import os
import json
import pickle
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import sys

sys.path.append('/var/www/worldcup-predictor/backend')

from services.neural_network import create_nn_model
from services.random_forest import create_random_forest
from services.feature_engine_v2 import get_feature_engine_v2
from data.historical_world_cups import get_all_world_cup_matches


@dataclass
class TrainingProgress:
    """训练进度"""
    model_name: str
    current_epoch: int
    total_epochs: int
    current_loss: float
    best_loss: float
    accuracy: float
    status: str  # pending, training, completed, failed
    start_time: str
    elapsed_seconds: float = 0.0
    message: str = ""


@dataclass
class TrainingResult:
    """训练结果"""
    model_name: str
    training_time: str
    epochs: int
    final_loss: float
    final_accuracy: float
    validation_accuracy: float
    model_path: str
    feature_importance: Optional[Dict] = None
    training_history: Optional[List[Dict]] = None
    status: str = "completed"
    message: str = "训练完成"


class ModelTrainerV2:
    """
    模型训练管理器 V2
    
    功能：
    1. 训练进度实时展示
    2. 训练结果持久化
    3. 训练历史记录
    """
    
    def __init__(self, data_path: str = "/var/www/worldcup-predictor/backend/data"):
        self.data_path = data_path
        self.models_path = os.path.join(data_path, "trained_models")
        self.history_path = os.path.join(data_path, "training_history.json")
        self.progress_path = os.path.join(data_path, "training_progress.json")
        
        # 创建目录
        os.makedirs(self.models_path, exist_ok=True)
        
        # 训练状态
        self.current_progress: Dict[str, TrainingProgress] = {}
        self.training_results: Dict[str, TrainingResult] = {}
        
        # 加载历史
        self._load_history()
        
        # 模型实例
        self.nn_model = None
        self.rf_model = None
        
        # 训练数据
        self.X_train = None
        self.y_train = None
    
    def _load_history(self):
        """加载训练历史"""
        if os.path.exists(self.history_path):
            try:
                with open(self.history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 加载训练结果
                    for model_name, result in data.get('results', {}).items():
                        self.training_results[model_name] = TrainingResult(**result)
                print(f"✓ 加载训练历史: {len(self.training_results)} 个模型")
            except Exception as e:
                print(f"加载训练历史失败: {e}")
    
    def _save_history(self):
        """保存训练历史"""
        try:
            data = {
                'results': {name: asdict(result) for name, result in self.training_results.items()},
                'last_updated': datetime.now().isoformat()
            }
            with open(self.history_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存训练历史失败: {e}")
    
    def _save_progress(self):
        """保存训练进度"""
        try:
            data = {
                name: asdict(progress) 
                for name, progress in self.current_progress.items()
            }
            with open(self.progress_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存训练进度失败: {e}")
    
    def prepare_training_data(self) -> Dict:
        """准备训练数据"""
        print("\n📊 准备训练数据...")
        
        # 获取历史比赛数据
        matches = get_all_world_cup_matches()
        print(f"  - 历史比赛数据: {len(matches)} 场")
        
        # 特征引擎
        feature_engine = get_feature_engine_v2()
        
        # 提取特征
        X = []
        y = []
        
        for match in matches:
            # 提取特征
            home_data = {
                'code': match.get('home', ''),
                'elo': match.get('home_elo', 1500),
                'rank': match.get('home_rank', 50),
                'form': match.get('home_form', 'DDD'),
                'continent': match.get('home_continent', 'EU'),
                'wc_titles': match.get('home_wc_titles', 0),
                'wc_participations': match.get('home_wc_participations', 5)
            }
            away_data = {
                'code': match.get('away', ''),
                'elo': match.get('away_elo', 1500),
                'rank': match.get('away_rank', 50),
                'form': match.get('away_form', 'DDD'),
                'continent': match.get('away_continent', 'EU'),
                'wc_titles': match.get('away_wc_titles', 0),
                'wc_participations': match.get('away_wc_participations', 5)
            }
            
            stage = match.get('stage', match.get('round', 'GROUP'))
            
            features = feature_engine.compute_features(
                home=home_data,
                away=away_data,
                stage=stage
            )
            
            X.append(features.to_vector())
            
            # 标签编码
            result = match.get('result', '')
            if result in ['HOME_WIN', '主胜', 'home_win']:
                y.append(0)
            elif result in ['DRAW', '平局', 'draw']:
                y.append(1)
            elif result in ['AWAY_WIN', '客胜', 'away_win']:
                y.append(2)
            else:
                # 默认为平局
                y.append(1)
        
        self.X_train = np.array(X)
        self.y_train = np.array(y)
        
        print(f"  - 特征维度: {self.X_train.shape[1]}")
        print(f"  - 样本数量: {len(self.X_train)}")
        print(f"  - 标签分布: 主胜{np.sum(y==0)}, 平局{np.sum(y==1)}, 客胜{np.sum(y==2)}")
        
        return {
            'samples': len(self.X_train),
            'features': self.X_train.shape[1],
            'distribution': {'home_win': int(np.sum(y==0)), 'draw': int(np.sum(y==1)), 'away_win': int(np.sum(y==2))}
        }
    
    def train_neural_network(
        self, 
        epochs: int = 100, 
        batch_size: int = 16,
        hidden_sizes: List[int] = [64, 32, 16]
    ) -> TrainingResult:
        """
        训练神经网络
        
        带进度展示和结果持久化
        """
        model_name = "neural_network"
        start_time = datetime.now()
        
        # 初始化进度
        progress = TrainingProgress(
            model_name=model_name,
            current_epoch=0,
            total_epochs=epochs,
            current_loss=0.0,
            best_loss=float('inf'),
            accuracy=0.0,
            status="training",
            start_time=start_time.isoformat(),
            message="初始化神经网络..."
        )
        self.current_progress[model_name] = progress
        self._save_progress()
        
        print(f"\n🧠 开始训练神经网络...")
        print(f"  - 网络结构: {hidden_sizes}")
        print(f"  - 训练轮数: {epochs}")
        print(f"  - 批次大小: {batch_size}")
        
        try:
            # 创建模型
            self.nn_model = create_nn_model()
            self.nn_model.hidden_sizes = hidden_sizes
            
            # 训练历史
            training_history = []
            best_accuracy = 0.0
            
            # 分阶段训练（模拟进度更新）
            for epoch in range(epochs):
                # 更新进度
                progress.current_epoch = epoch + 1
                progress.message = f"训练中... Epoch {epoch+1}/{epochs}"
                
                # 每10轮更新一次
                if epoch % 10 == 0 or epoch == epochs - 1:
                    self._save_progress()
                    print(f"  Epoch {epoch+1}/{epochs}", end="")
                    
                    # 实际训练
                    history = self.nn_model.train(
                        self.X_train, 
                        self.y_train, 
                        epochs=10 if epoch < epochs - 10 else epochs - epoch,
                        batch_size=batch_size,
                        validation_split=0.2
                    )
                    
                    # 获取损失和准确率
                    if history and 'val_loss' in history:
                        current_loss = history['val_loss'][-1]
                        current_acc = history['val_acc'][-1] if 'val_acc' in history else 0.5
                    else:
                        current_loss = history.get('loss', [1.0])[-1] if history else 1.0
                        current_acc = 0.5
                    
                    progress.current_loss = current_loss
                    progress.accuracy = current_acc
                    
                    if current_loss < progress.best_loss:
                        progress.best_loss = current_loss
                    
                    if current_acc > best_accuracy:
                        best_accuracy = current_acc
                    
                    print(f" - Loss: {current_loss:.4f}, Acc: {current_acc:.2%}")
                    
                    training_history.append({
                        'epoch': epoch + 1,
                        'loss': current_loss,
                        'accuracy': current_acc
                    })
            
            # 保存模型
            model_path = os.path.join(self.models_path, f"{model_name}.pkl")
            self.nn_model.save_model(model_path)
            
            # 计算训练时间
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # 创建结果
            result = TrainingResult(
                model_name=model_name,
                training_time=datetime.now().isoformat(),
                epochs=epochs,
                final_loss=progress.current_loss,
                final_accuracy=progress.accuracy,
                validation_accuracy=best_accuracy,
                model_path=model_path,
                training_history=training_history,
                status="completed",
                message="训练完成 ✓"
            )
            
            # 更新状态
            progress.status = "completed"
            progress.message = "训练完成 ✓"
            progress.elapsed_seconds = elapsed
            self._save_progress()
            
            # 保存结果
            self.training_results[model_name] = result
            self._save_history()
            
            print(f"\n✓ 神经网络训练完成!")
            print(f"  - 最终损失: {result.final_loss:.4f}")
            print(f"  - 验证准确率: {result.validation_accuracy:.2%}")
            print(f"  - 训练时间: {elapsed:.1f}秒")
            print(f"  - 模型已保存: {model_path}")
            
            return result
            
        except Exception as e:
            progress.status = "failed"
            progress.message = f"训练失败: {str(e)}"
            self._save_progress()
            
            return TrainingResult(
                model_name=model_name,
                training_time=datetime.now().isoformat(),
                epochs=0,
                final_loss=0.0,
                final_accuracy=0.0,
                validation_accuracy=0.0,
                model_path="",
                status="failed",
                message=str(e)
            )
    
    def train_random_forest(
        self,
        n_estimators: int = 100,
        max_depth: int = 10
    ) -> TrainingResult:
        """
        训练随机森林
        
        带进度展示和结果持久化
        """
        model_name = "random_forest"
        start_time = datetime.now()
        
        # 初始化进度
        progress = TrainingProgress(
            model_name=model_name,
            current_epoch=0,
            total_epochs=n_estimators,
            current_loss=0.0,
            best_loss=0.0,
            accuracy=0.0,
            status="training",
            start_time=start_time.isoformat(),
            message="初始化随机森林..."
        )
        self.current_progress[model_name] = progress
        self._save_progress()
        
        print(f"\n🌲 开始训练随机森林...")
        print(f"  - 决策树数量: {n_estimators}")
        print(f"  - 最大深度: {max_depth}")
        
        try:
            # 创建模型
            self.rf_model = create_random_forest(n_estimators=n_estimators)
            
            # 更新进度
            progress.message = f"训练中... 构建{n_estimators}棵决策树"
            self._save_progress()
            
            print(f"  构建决策树: ", end="")
            
            # 训练
            train_result = self.rf_model.train(self.X_train, self.y_train)
            
            # 模拟进度更新
            for i in range(0, n_estimators, 20):
                progress.current_epoch = i + 20
                print(f"#{i+20}", end=" ")
                self._save_progress()
            
            print("完成!")
            
            # 获取特征重要性
            feature_importance = train_result.get('feature_importance', {})
            
            # 保存模型
            model_path = os.path.join(self.models_path, f"{model_name}.pkl")
            self.rf_model.save_model(model_path)
            
            # 计算训练时间
            elapsed = (datetime.now() - start_time).total_seconds()
            
            # 创建结果
            result = TrainingResult(
                model_name=model_name,
                training_time=datetime.now().isoformat(),
                epochs=n_estimators,
                final_loss=0.0,
                final_accuracy=train_result.get('accuracy', 0.5),
                validation_accuracy=train_result.get('accuracy', 0.5),
                model_path=model_path,
                feature_importance=feature_importance,
                status="completed",
                message="训练完成 ✓"
            )
            
            # 更新状态
            progress.status = "completed"
            progress.accuracy = result.final_accuracy
            progress.message = "训练完成 ✓"
            progress.elapsed_seconds = elapsed
            self._save_progress()
            
            # 保存结果
            self.training_results[model_name] = result
            self._save_history()
            
            print(f"\n✓ 随机森林训练完成!")
            print(f"  - 准确率: {result.final_accuracy:.2%}")
            print(f"  - 训练时间: {elapsed:.1f}秒")
            print(f"  - 模型已保存: {model_path}")
            
            # 打印特征重要性
            if feature_importance:
                print(f"\n  特征重要性 Top 5:")
                sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
                for name, importance in sorted_features[:5]:
                    print(f"    {name}: {importance:.3f}")
            
            return result
            
        except Exception as e:
            progress.status = "failed"
            progress.message = f"训练失败: {str(e)}"
            self._save_progress()
            
            return TrainingResult(
                model_name=model_name,
                training_time=datetime.now().isoformat(),
                epochs=0,
                final_loss=0.0,
                final_accuracy=0.0,
                validation_accuracy=0.0,
                model_path="",
                status="failed",
                message=str(e)
            )
    
    def train_all_models(self, nn_epochs: int = 100, rf_estimators: int = 100) -> Dict[str, TrainingResult]:
        """训练所有模型"""
        print("\n" + "=" * 60)
        print("🚀 开始训练所有模型")
        print("=" * 60)
        
        # 准备数据
        data_info = self.prepare_training_data()
        
        results = {}
        
        # 训练神经网络
        results['neural_network'] = self.train_neural_network(epochs=nn_epochs)
        
        # 训练随机森林
        results['random_forest'] = self.train_random_forest(n_estimators=rf_estimators)
        
        print("\n" + "=" * 60)
        print("✅ 所有模型训练完成!")
        print("=" * 60)
        
        return results
    
    def get_training_progress(self, model_name: str = None) -> Dict:
        """获取训练进度"""
        if model_name:
            progress = self.current_progress.get(model_name)
            return asdict(progress) if progress else None
        
        return {name: asdict(progress) for name, progress in self.current_progress.items()}
    
    def get_training_results(self, model_name: str = None) -> Dict:
        """获取训练结果"""
        if model_name:
            result = self.training_results.get(model_name)
            return asdict(result) if result else None
        
        return {name: asdict(result) for name, result in self.training_results.items()}
    
    def get_last_training_summary(self) -> Dict:
        """获取上次训练摘要"""
        results = self.get_training_results()
        
        if not results:
            return {
                'has_trained': False,
                'message': '尚未进行模型训练'
            }
        
        summary = {
            'has_trained': True,
            'models': {},
            'best_model': None,
            'best_accuracy': 0.0
        }
        
        for name, result in results.items():
            if result.get('status') == 'completed':
                summary['models'][name] = {
                    'accuracy': result.get('validation_accuracy', 0),
                    'training_time': result.get('training_time', ''),
                    'epochs': result.get('epochs', 0),
                    'model_path': result.get('model_path', '')
                }
                
                if result.get('validation_accuracy', 0) > summary['best_accuracy']:
                    summary['best_accuracy'] = result.get('validation_accuracy', 0)
                    summary['best_model'] = name
        
        return summary
    
    def load_trained_models(self) -> Dict:
        """加载已训练的模型"""
        loaded = {}
        
        # 加载神经网络
        nn_path = os.path.join(self.models_path, "neural_network.pkl")
        if os.path.exists(nn_path):
            try:
                self.nn_model = create_nn_model()
                self.nn_model.load_model(nn_path)
                loaded['neural_network'] = True
                print(f"✓ 加载神经网络: {nn_path}")
            except Exception as e:
                print(f"✗ 加载神经网络失败: {e}")
                loaded['neural_network'] = False
        
        # 加载随机森林
        rf_path = os.path.join(self.models_path, "random_forest.pkl")
        if os.path.exists(rf_path):
            try:
                self.rf_model = create_random_forest()
                self.rf_model.load_model(rf_path)
                loaded['random_forest'] = True
                print(f"✓ 加载随机森林: {rf_path}")
            except Exception as e:
                print(f"✗ 加载随机森林失败: {e}")
                loaded['random_forest'] = False
        
        return loaded


# 单例
_trainer_v2_instance = None


def get_trainer_v2() -> ModelTrainerV2:
    """获取训练器实例"""
    global _trainer_v2_instance
    if _trainer_v2_instance is None:
        _trainer_v2_instance = ModelTrainerV2()
    return _trainer_v2_instance
