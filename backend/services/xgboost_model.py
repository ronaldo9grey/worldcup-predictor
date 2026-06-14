"""
XGBoost预测模型 - 使用新特征体系
训练数据：世界杯历史比赛 + 新特征
"""
import xgboost as xgb
import numpy as np
import pandas as pd
import sqlite3
import json
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import joblib
import sys
sys.path.insert(0, '/var/www/worldcup-predictor/backend')

# =====================
# 1. 加载球队评分数据
# =====================

with open('/var/www/worldcup-predictor/backend/data/team_ratings_48.json', 'r', encoding='utf-8') as f:
    TEAM_RATINGS = json.load(f)

# =====================
# 2. 生成训练数据
# =====================

def generate_training_data():
    """生成训练数据（使用历史世界杯数据）"""
    
    # 加载历史数据
    from data.historical_world_cups import get_all_world_cup_matches
    
    matches = get_all_world_cup_matches()
    print(f"历史比赛数: {len(matches)}")
    
    # 生成特征
    X = []
    y = []
    
    for match in matches:
        home_code = match.get('home_code')
        away_code = match.get('away_code')
        result = match.get('result')  # 'HOME_WIN', 'DRAW', 'AWAY_WIN'
        
        if not home_code or not away_code or not result:
            continue
        
        # 获取球队评分（使用默认值如果球队不在列表中）
        home_rating = TEAM_RATINGS.get(home_code, {'avg_rating': 75.0})
        away_rating = TEAM_RATINGS.get(away_code, {'avg_rating': 75.0})
        
        # 计算特征
        features = {
            # 球员实力差
            'avg_rating_diff': home_rating['avg_rating'] - away_rating['avg_rating'],
            'forward_diff': home_rating['forward_rating'] - away_rating['forward_rating'],
            'midfield_diff': home_rating['midfield_rating'] - away_rating['midfield_rating'],
            'defense_diff': home_rating['defense_rating'] - away_rating['defense_rating'],
            'goalkeeper_diff': home_rating['goalkeeper_rating'] - away_rating['goalkeeper_rating'],
            'star_players_diff': home_rating['star_players'] - away_rating['star_players'],
            
            # 比赛阶段（小组赛=0, 淘汰赛=1）
            'stage': 0 if match.get('stage') == 'GROUP' else 1,
            
            # 经验差距
            'wc_experience_diff': home_rating['wc_experience'] - away_rating['wc_experience'],
            
            # 替补深度
            'bench_depth_diff': home_rating['bench_depth'] - away_rating['bench_depth']
        }
        
        X.append(list(features.values()))
        
        # 结果编码: HOME_WIN=0, DRAW=1, AWAY_WIN=2
        if result == 'HOME_WIN':
            y.append(0)
        elif result == 'DRAW':
            y.append(1)
        else:
            y.append(2)
    
    return np.array(X), np.array(y), list(features.keys())

# =====================
# 3. 训练模型
# =====================

def train_xgboost_model():
    """训练XGBoost模型"""
    
    print("=" * 70)
    print("开始训练XGBoost模型")
    print("=" * 70)
    
    # 生成训练数据
    X, y, feature_names = generate_training_data()
    
    print(f"\n训练数据:")
    print(f"  样本数: {len(X)}")
    print(f"  特征数: {len(feature_names)}")
    print(f"  类别分布: {np.bincount(y)}")
    
    # 分割训练集和测试集
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"\n训练集: {len(X_train)}, 测试集: {len(X_test)}")
    
    # 训练XGBoost
    print(f"\n训练中...")
    
    model = xgb.XGBClassifier(
        n_estimators=200,
        max_depth=6,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        objective='multi:softprob',
        num_class=3,
        eval_metric='mlogloss',
        use_label_encoder=False,
        random_state=42
    )
    
    model.fit(
        X_train, y_train,
        eval_set=[(X_test, y_test)],
        early_stopping_rounds=20,
        verbose=False
    )
    
    # 预测
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)
    
    # 评估
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n模型评估:")
    print(f"  准确率: {accuracy:.1%}")
    
    print(f"\n分类报告:")
    print(classification_report(y_test, y_pred, target_names=['主胜', '平局', '客胜']))
    
    # 特征重要性
    print(f"\n特征重要性:")
    importance = dict(zip(feature_names, model.feature_importances_))
    for feat, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
        print(f"  {feat}: {imp:.4f}")
    
    # 保存模型
    model_path = '/var/www/worldcup-predictor/backend/data/models/xgboost_model.pkl'
    import os
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    joblib.dump({
        'model': model,
        'feature_names': feature_names,
        'accuracy': accuracy,
        'team_ratings': TEAM_RATINGS
    }, model_path)
    
    print(f"\n✓ 模型已保存: {model_path}")
    
    return model, feature_names, accuracy

# =====================
# 4. 测试预测
# =====================

def predict_match(home_code, away_code, model_data=None):
    """预测比赛结果"""
    
    if model_data is None:
        model_path = '/var/www/worldcup-predictor/backend/data/models/xgboost_model.pkl'
        model_data = joblib.load(model_path)
    
    model = model_data['model']
    feature_names = model_data['feature_names']
    
    # 获取球队评分
    home_rating = TEAM_RATINGS.get(home_code, {'avg_rating': 75.0})
    away_rating = TEAM_RATINGS.get(away_code, {'avg_rating': 75.0})
    
    # 计算特征
    features = [
        home_rating['avg_rating'] - away_rating['avg_rating'],
        home_rating['forward_rating'] - away_rating['forward_rating'],
        home_rating['midfield_rating'] - away_rating['midfield_rating'],
        home_rating['defense_rating'] - away_rating['defense_rating'],
        home_rating['goalkeeper_rating'] - away_rating['goalkeeper_rating'],
        home_rating['star_players'] - away_rating['star_players'],
        0,  # 小组赛
        home_rating['wc_experience'] - away_rating['wc_experience'],
        home_rating['bench_depth'] - away_rating['bench_depth']
    ]
    
    X = np.array([features])
    
    # 预测
    proba = model.predict_proba(X)[0]
    pred_class = model.predict(X)[0]
    
    result_names = ['主胜', '平局', '客胜']
    
    return {
        'home_win_prob': proba[0],
        'draw_prob': proba[1],
        'away_win_prob': proba[2],
        'prediction': result_names[pred_class],
        'confidence': max(proba)
    }

# =====================
# 主程序
# =====================

if __name__ == "__main__":
    # 训练模型
    model, feature_names, accuracy = train_xgboost_model()
    
    # 测试几个比赛
    print("\n" + "=" * 70)
    print("测试预测")
    print("=" * 70)
    
    test_matches = [
        ("ARG", "BRA", "阿根廷 vs 巴西"),
        ("FRA", "ENG", "法国 vs 英格兰"),
        ("JPN", "KOR", "日本 vs 韩国"),
        ("MAR", "SEN", "摩洛哥 vs 塞内加尔"),
        ("ARG", "SAU", "阿根廷 vs 沙特")
    ]
    
    for home, away, name in test_matches:
        result = predict_match(home, away)
        print(f"\n{name}:")
        print(f"  主胜: {result['home_win_prob']:.1%}")
        print(f"  平局: {result['draw_prob']:.1%}")
        print(f"  客胜: {result['away_win_prob']:.1%}")
        print(f"  预测: {result['prediction']} (置信度: {result['confidence']:.1%})")