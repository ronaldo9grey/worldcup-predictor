"""
使用随机森林 + 新特征训练模型
"""
import numpy as np
import json
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import sys
sys.path.insert(0, '/var/www/worldcup-predictor/backend')

# =====================
# 1. 加载球队评分数据
# =====================

with open('/var/www/worldcup-predictor/backend/data/team_ratings_48.json', 'r', encoding='utf-8') as f:
    TEAM_RATINGS = json.load(f)

print("=" * 70)
print("新特征体系 - 随机森林模型")
print("=" * 70)

# =====================
# 2. 生成训练数据
# =====================

def generate_training_data():
    """生成训练数据"""
    
    # 加载历史数据
    from data.historical_world_cups import get_all_world_cup_matches
    
    matches = get_all_world_cup_matches()
    print(f"\n历史比赛数: {len(matches)}")
    
    X = []
    y = []
    
    for match in matches:
        home_code = match.get('home_code')
        away_code = match.get('away_code')
        result = match.get('result')
        
        if not home_code or not away_code or not result:
            continue
        
        # 获取球队评分
        home_rating = TEAM_RATINGS.get(home_code, {
            'avg_rating': 75.0,
            'forward_rating': 75.0,
            'midfield_rating': 75.0,
            'defense_rating': 75.0,
            'goalkeeper_rating': 75.0,
            'star_players': 0,
            'wc_experience': 5,
            'bench_depth': 70.0
        })
        
        away_rating = TEAM_RATINGS.get(away_code, {
            'avg_rating': 75.0,
            'forward_rating': 75.0,
            'midfield_rating': 75.0,
            'defense_rating': 75.0,
            'goalkeeper_rating': 75.0,
            'star_players': 0,
            'wc_experience': 5,
            'bench_depth': 70.0
        })
        
        # 计算特征（核心特征）
        features = [
            # 1. 球员实力差（最重要）
            home_rating['avg_rating'] - away_rating['avg_rating'],
            home_rating['forward_rating'] - away_rating['forward_rating'],
            home_rating['midfield_rating'] - away_rating['midfield_rating'],
            home_rating['defense_rating'] - away_rating['defense_rating'],
            home_rating['goalkeeper_rating'] - away_rating['goalkeeper_rating'],
            
            # 2. 星级球员差距
            home_rating['star_players'] - away_rating['star_players'],
            
            # 3. 经验差距
            home_rating['wc_experience'] - away_rating['wc_experience'],
            
            # 4. 替补深度
            home_rating['bench_depth'] - away_rating['bench_depth'],
            
            # 5. 比赛阶段
            0 if match.get('stage') == 'GROUP' else 1
        ]
        
        X.append(features)
        
        # 结果编码: HOME_WIN=0, DRAW=1, AWAY_WIN=2
        if result == 'HOME_WIN':
            y.append(0)
        elif result == 'DRAW':
            y.append(1)
        else:
            y.append(2)
    
    return np.array(X), np.array(y), [
        'avg_rating_diff', 'forward_diff', 'midfield_diff',
        'defense_diff', 'goalkeeper_diff', 'star_players_diff',
        'wc_experience_diff', 'bench_depth_diff', 'stage'
    ]

# 生成数据
X, y, feature_names = generate_training_data()

print(f"训练数据: {len(X)} 场比赛")
print(f"特征数: {len(feature_names)}")
print(f"类别分布: 主胜={sum(y==0)}, 平局={sum(y==1)}, 客胜={sum(y==2)}")

# =====================
# 3. 训练模型
# =====================

print(f"\n分割数据集...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"训练集: {len(X_train)}, 测试集: {len(X_test)}")

print(f"\n训练随机森林...")
model = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    min_samples_leaf=5,
    class_weight='balanced',
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# =====================
# 4. 评估模型
# =====================

y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n模型评估:")
print(f"  准确率: {accuracy:.1%}")

print(f"\n分类报告:")
print(classification_report(y_test, y_pred, target_names=['主胜', '平局', '客胜']))

# 特征重要性
print(f"\n特征重要性:")
importance = dict(zip(feature_names, model.feature_importances_))
for feat, imp in sorted(importance.items(), key=lambda x: x[1], reverse=True):
    print(f"  {feat:20s}: {imp:.4f}")

# =====================
# 5. 保存模型
# =====================

model_path = '/var/www/worldcup-predictor/backend/data/models/new_rf_model.pkl'
import os
os.makedirs(os.path.dirname(model_path), exist_ok=True)

joblib.dump({
    'model': model,
    'feature_names': feature_names,
    'accuracy': accuracy,
    'team_ratings': TEAM_RATINGS
}, model_path)

print(f"\n✓ 模型已保存: {model_path}")

# =====================
# 6. 测试预测
# =====================

def predict_match(home_code, away_code):
    """预测比赛"""
    
    home_rating = TEAM_RATINGS.get(home_code, {'avg_rating': 75.0})
    away_rating = TEAM_RATINGS.get(away_code, {'avg_rating': 75.0})
    
    features = np.array([[
        home_rating['avg_rating'] - away_rating['avg_rating'],
        home_rating['forward_rating'] - away_rating['forward_rating'],
        home_rating['midfield_rating'] - away_rating['midfield_rating'],
        home_rating['defense_rating'] - away_rating['defense_rating'],
        home_rating['goalkeeper_rating'] - away_rating['goalkeeper_rating'],
        home_rating['star_players'] - away_rating['star_players'],
        home_rating['wc_experience'] - away_rating['wc_experience'],
        home_rating['bench_depth'] - away_rating['bench_depth'],
        0  # 小组赛
    ]])
    
    proba = model.predict_proba(features)[0]
    pred = model.predict(features)[0]
    
    return {
        'home_win': proba[0],
        'draw': proba[1],
        'away_win': proba[2],
        'prediction': ['主胜', '平局', '客胜'][pred],
        'confidence': max(proba)
    }

print("\n" + "=" * 70)
print("测试预测（使用新特征）")
print("=" * 70)

test_matches = [
    ("ARG", "BRA", "阿根廷 vs 巴西"),
    ("FRA", "ENG", "法国 vs 英格兰"),
    ("JPN", "KOR", "日本 vs 韩国"),
    ("MAR", "SEN", "摩洛哥 vs 塞内加尔"),
    ("ARG", "SAU", "阿根廷 vs 沙特"),
    ("FRA", "NGA", "法国 vs 尼日利亚"),
]

for home, away, name in test_matches:
    result = predict_match(home, away)
    print(f"\n{name}:")
    print(f"  主胜: {result['home_win']:.1%} | 平局: {result['draw']:.1%} | 客胜: {result['away_win']:.1%}")
    print(f"  预测: {result['prediction']} (置信度: {result['confidence']:.1%})")

print("\n" + "=" * 70)
print("对比旧模型（58.3%准确率）")
print("=" * 70)
print(f"新模型准确率: {accuracy:.1%}")
print(f"提升: {(accuracy - 0.583):.1%}")