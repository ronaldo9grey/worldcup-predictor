"""
生成带有真实特征的训练数据
基于现有球队数据库中的真实Elo、排名等特征
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
from typing import List, Dict, Tuple
from data.world_cup_2026 import get_team_lookup
from services.feature_engine_v2 import get_feature_engine_v2


def generate_training_data_with_real_features(n_matches: int = 1000) -> Tuple[np.ndarray, np.ndarray, List[Dict]]:
    """
    生成带有真实特征的训练数据
    
    Args:
        n_matches: 生成的比赛数量
        
    Returns:
        X: 特征矩阵
        y: 标签向量
        match_info: 比赛信息列表
    """
    print("🚀 开始生成训练数据...")
    
    # 获取球队数据
    team_lookup = get_team_lookup()
    teams = list(team_lookup.values())
    
    print(f"  球队数量: {len(teams)}")
    
    # 特征引擎
    feature_engine = get_feature_engine_v2()
    
    X = []
    y = []
    match_info = []
    
    # 基于Elo差异预测结果的概率分布
    # 这个函数模拟真实比赛中Elo差异与胜负的关系
    def simulate_match_result(home_elo: int, away_elo: int, home_rank: int, away_rank: int) -> str:
        """基于Elo和排名模拟比赛结果"""
        elo_diff = home_elo - away_elo
        rank_diff = away_rank - home_rank  # 负数表示主队排名低
        
        # 基于Elo差异计算基础概率
        # 参考：Elo评分每400分差异，高评分方胜率约90%
        expected_home = 1 / (1 + 10 ** ((away_elo - home_elo) / 400))
        
        # 添加排名因素（排名每差10位，概率偏移约5%）
        rank_factor = rank_diff * 0.005
        expected_home += rank_factor
        
        # 添加随机性和主场优势
        home_advantage = 0.05  # 主场优势约5%
        expected_home += home_advantage
        
        # 归一化概率
        if expected_home > 0.7:
            # 大热门
            probs = [0.65, 0.20, 0.15]
        elif expected_home > 0.55:
            # 热门
            probs = [0.50, 0.25, 0.25]
        elif expected_home > 0.45:
            # 势均力敌
            probs = [0.35, 0.30, 0.35]
        elif expected_home > 0.30:
            # 客队略优
            probs = [0.25, 0.25, 0.50]
        else:
            # 客队大热
            probs = [0.15, 0.20, 0.65]
        
        # 随机选择结果
        result = np.random.choice(['HOME_WIN', 'DRAW', 'AWAY_WIN'], p=probs)
        return result
    
    print(f"  生成{n_matches}场比赛...")
    
    for i in range(n_matches):
        # 随机选择两支球队
        home_idx = np.random.randint(0, len(teams))
        away_idx = np.random.randint(0, len(teams))
        
        # 确保不是同一支球队
        while away_idx == home_idx:
            away_idx = np.random.randint(0, len(teams))
        
        home = teams[home_idx]
        away = teams[away_idx]
        
        # 模拟比赛结果
        result = simulate_match_result(
            home.get('elo', 1500),
            away.get('elo', 1500),
            home.get('rank', 50),
            away.get('rank', 50)
        )
        
        # 提取特征
        features = feature_engine.compute_features(
            home=home,
            away=away,
            stage='GROUP'
        )
        
        X.append(features.to_vector())
        
        # 标签编码
        if result == 'HOME_WIN':
            y.append(0)
        elif result == 'DRAW':
            y.append(1)
        else:
            y.append(2)
        
        # 记录比赛信息
        match_info.append({
            'home': home.get('code'),
            'away': away.get('code'),
            'result': result,
            'home_elo': home.get('elo'),
            'away_elo': away.get('elo'),
            'home_rank': home.get('rank'),
            'away_rank': away.get('rank')
        })
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"  ✅ 生成完成!")
    print(f"  特征维度: {X.shape[1]}")
    print(f"  样本数量: {len(X)}")
    print(f"  标签分布: 主胜{np.sum(y==0)}, 平局{np.sum(y==1)}, 客胜{np.sum(y==2)}")
    
    # 验证特征值分布
    print(f"\n  特征值统计:")
    print(f"    均值范围: [{X.mean(axis=0).min():.3f}, {X.mean(axis=0).max():.3f}]")
    print(f"    标准差范围: [{X.std(axis=0).min():.3f}, {X.std(axis=0).max():.3f}]")
    print(f"    是否有NaN: {np.isnan(X).any()}")
    print(f"    是否有Inf: {np.isinf(X).any()}")
    
    return X, y, match_info


if __name__ == "__main__":
    # 生成训练数据
    X, y, match_info = generate_training_data_with_real_features(n_matches=2000)
    
    # 保存数据
    import pickle
    with open('data/training_data_real_features.pkl', 'wb') as f:
        pickle.dump({'X': X, 'y': y, 'match_info': match_info}, f)
    
    print("\n💾 训练数据已保存到 data/training_data_real_features.pkl")
