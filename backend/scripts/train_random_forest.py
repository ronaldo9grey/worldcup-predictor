"""
重新训练随机森林模型
使用带有真实特征的训练数据
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pickle
import numpy as np
from services.random_forest import RandomForestPredictor
from datetime import datetime


def train_random_forest_with_real_data():
    """使用真实特征数据训练随机森林"""
    
    print("=" * 60)
    print("🌲 开始训练随机森林模型（真实特征）")
    print("=" * 60)
    print()
    
    # 加载训练数据
    print("📂 加载训练数据...")
    with open('data/training_data_real_features.pkl', 'rb') as f:
        data = pickle.load(f)
    
    X = data['X']
    y = data['y']
    match_info = data['match_info']
    
    print(f"  特征维度: {X.shape[1]}")
    print(f"  样本数量: {len(X)}")
    print(f"  标签分布: 主胜{np.sum(y==0)}, 平局{np.sum(y==1)}, 客胜{np.sum(y==2)}")
    print()
    
    # 创建随机森林模型
    print("🌲 创建随机森林模型...")
    print("  参数:")
    print("    - 决策树数量: 100")
    print("    - 最大深度: 10")
    print("    - 最小分割样本数: 2")
    print()
    
    rf = RandomForestPredictor(n_estimators=100)
    
    # 训练模型
    print("🚀 开始训练...")
    print()
    
    start_time = datetime.now()
    
    train_result = rf.train(X, y)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print()
    print("✅ 训练完成!")
    print(f"  训练耗时: {duration:.2f}秒")
    print(f"  训练准确率: {train_result['accuracy']*100:.2f}%")
    print()
    
    # 显示特征重要性
    print("📊 特征重要性排名:")
    importance = train_result['feature_importance']
    for feat, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  {feat}: {imp:.4f}")
    print()
    
    # 验证模型是否正常工作
    print("🧪 模型验证:")
    
    # 测试几个场景
    test_cases = [
        ("强队 vs 弱队", X[0]),
        ("弱队 vs 强队", X[-1]),
        ("势均力敌", X[len(X)//2])
    ]
    
    for desc, features in test_cases:
        proba = rf.model.predict_proba(features.reshape(1, -1))[0]
        result = "主胜" if proba[0] > 0.4 else "客胜" if proba[2] > 0.4 else "平局"
        print(f"  {desc}: 主胜{proba[0]*100:.1f}% | 平局{proba[1]*100:.1f}% | 客胜{proba[2]*100:.1f}% → {result}")
    print()
    
    # 检查是否所有树都是叶子节点
    print("🔍 检查决策树结构:")
    leaf_count = 0
    split_count = 0
    
    for i in range(min(20, len(rf.model.trees))):
        tree_dict = rf.model.trees[i]
        tree = tree_dict['tree']
        
        if tree.tree.get('leaf'):
            leaf_count += 1
        else:
            split_count += 1
            if i < 5:  # 显示前5棵树的分割信息
                print(f"  树#{i+1}: 有分割")
                print(f"    分割特征: {rf.feature_names[tree.tree['feature']]}")
                print(f"    分割阈值: {tree.tree['threshold']:.3f}")
    
    print(f"\n  统计（前20棵树）:")
    print(f"    有分割的树: {split_count}")
    print(f"    纯叶子节点: {leaf_count}")
    print()
    
    if leaf_count == 0:
        print("  ✅ 所有树都有分割，模型正常!")
    else:
        print(f"  ⚠️ 有{leaf_count}棵树是纯叶子节点")
    print()
    
    # 保存模型
    print("💾 保存模型...")
    
    # 备份旧模型
    import shutil
    old_model_path = 'data/models/rf_model_v1.pkl'
    if os.path.exists(old_model_path):
        backup_path = f'data/models/rf_model_v1_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pkl'
        shutil.copy(old_model_path, backup_path)
        print(f"  旧模型已备份: {backup_path}")
    
    # 保存新模型
    rf.save_model(old_model_path)
    print(f"  新模型已保存: {old_model_path}")
    print()
    
    print("=" * 60)
    print("🎉 训练完成！")
    print("=" * 60)
    
    return rf, train_result


if __name__ == "__main__":
    rf, result = train_random_forest_with_real_data()
