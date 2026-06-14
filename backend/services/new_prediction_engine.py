"""
新预测引擎 - 基于球员评分的规则系统
不依赖sklearn，直接计算概率
"""
import json
import math

# 加载球队评分
with open('/var/www/worldcup-predictor/backend/data/team_ratings_48.json', 'r', encoding='utf-8') as f:
    TEAM_RATINGS = json.load(f)

def calculate_win_probability(home_code, away_code, stage='GROUP'):
    """
    计算比赛胜负概率
    
    核心思路：
    1. 计算球队实力差距（基于球员评分）
    2. 考虑位置重要性（前锋>中场>后卫>门将）
    3. 星级球员加成
    4. 大赛经验加成
    5. 返回概率分布
    """
    
    # 获取球队评分
    home = TEAM_RATINGS.get(home_code, {
        'avg_rating': 75.0,
        'forward_rating': 75.0,
        'midfield_rating': 75.0,
        'defense_rating': 75.0,
        'goalkeeper_rating': 75.0,
        'star_players': 0,
        'wc_experience': 5,
        'bench_depth': 70.0
    })
    
    away = TEAM_RATINGS.get(away_code, {
        'avg_rating': 75.0,
        'forward_rating': 75.0,
        'midfield_rating': 75.0,
        'defense_rating': 75.0,
        'goalkeeper_rating': 75.0,
        'star_players': 0,
        'wc_experience': 5,
        'bench_depth': 70.0
    })
    
    # =====================
    # 1. 计算实力差距
    # =====================
    
    # 位置权重（前锋最重要）
    position_weights = {
        'forward': 0.35,      # 进球能力
        'midfield': 0.25,     # 组织能力
        'defense': 0.22,      # 防守能力
        'goalkeeper': 0.18    # 最后防线
    }
    
    # 加权实力差距
    strength_diff = (
        (home['forward_rating'] - away['forward_rating']) * position_weights['forward'] +
        (home['midfield_rating'] - away['midfield_rating']) * position_weights['midfield'] +
        (home['defense_rating'] - away['defense_rating']) * position_weights['defense'] +
        (home['goalkeeper_rating'] - away['goalkeeper_rating']) * position_weights['goalkeeper']
    )
    
    # =====================
    # 2. 星级球员加成
    # =====================
    
    star_diff = home['star_players'] - away['star_players']
    star_bonus = star_diff * 2.0  # 每个星级球员+2%胜率
    
    # =====================
    # 3. 经验加成
    # =====================
    
    exp_diff = home['wc_experience'] - away['wc_experience']
    exp_bonus = exp_diff * 0.5  # 每次世界杯经验+0.5%胜率
    
    # =====================
    # 4. 替补深度
    # =====================
    
    bench_diff = home['bench_depth'] - away['bench_depth']
    bench_bonus = bench_diff * 0.3
    
    # =====================
    # 5. 综合实力差距
    # =====================
    
    total_diff = strength_diff + star_bonus + exp_bonus + bench_bonus
    
    # =====================
    # 6. 转换为概率
    # =====================
    
    # 使用sigmoid函数平滑转换
    # total_diff范围: -15 ~ +15
    
    # 基础概率（假设实力相等）
    base_home = 0.40
    base_draw = 0.28
    base_away = 0.32
    
    # 根据实力差距调整
    # 正值：主队更强 -> 主胜概率增加
    # 负值：客队更强 -> 客胜概率增加
    
    adjustment = total_diff / 100.0  # 归一化
    
    home_prob = base_home + adjustment * 0.5
    away_prob = base_away - adjustment * 0.5
    draw_prob = base_draw - abs(adjustment) * 0.2
    
    # =====================
    # 7. 特殊情况处理
    # =====================
    
    # 如果实力非常接近（差距<3分），增加平局概率
    if abs(total_diff) < 3:
        draw_prob += 0.08
        home_prob -= 0.04
        away_prob -= 0.04
    
    # 如果实力差距很大（>10分），降低平局概率
    if abs(total_diff) > 10:
        draw_prob -= 0.05
        if total_diff > 0:
            home_prob += 0.05
        else:
            away_prob += 0.05
    
    # =====================
    # 8. 归一化
    # =====================
    
    total = home_prob + draw_prob + away_prob
    home_prob /= total
    draw_prob /= total
    away_prob /= total
    
    # =====================
    # 9. 预测结果
    # =====================
    
    if home_prob > draw_prob and home_prob > away_prob:
        prediction = '主胜'
        confidence = home_prob
    elif away_prob > draw_prob:
        prediction = '客胜'
        confidence = away_prob
    else:
        prediction = '平局'
        confidence = draw_prob
    
    return {
        'home_win_prob': home_prob,
        'draw_prob': draw_prob,
        'away_win_prob': away_prob,
        'prediction': prediction,
        'confidence': confidence,
        'strength_diff': total_diff,
        'details': {
            'home_rating': home['avg_rating'],
            'away_rating': away['avg_rating'],
            'home_stars': home['star_players'],
            'away_stars': away['star_players'],
            'home_experience': home['wc_experience'],
            'away_experience': away['wc_experience']
        }
    }

# =====================
# 测试预测
# =====================

if __name__ == "__main__":
    print("=" * 70)
    print("新预测引擎测试（基于球员评分）")
    print("=" * 70)
    
    test_matches = [
        ("ARG", "BRA", "阿根廷 vs 巴西"),
        ("FRA", "ENG", "法国 vs 英格兰"),
        ("JPN", "KOR", "日本 vs 韩国"),
        ("MAR", "SEN", "摩洛哥 vs 塞内加尔"),
        ("ARG", "SAU", "阿根廷 vs 沙特"),
        ("FRA", "NGA", "法国 vs 尼日利亚"),
        ("GER", "MEX", "德国 vs 墨西哥"),
        ("ESP", "POR", "西班牙 vs 葡萄牙"),
    ]
    
    print("\n预测结果:")
    print("-" * 70)
    
    for home, away, name in test_matches:
        result = calculate_win_probability(home, away)
        
        print(f"\n{name}:")
        print(f"  实力差距: {result['strength_diff']:+.1f}分")
        print(f"  主胜: {result['home_win_prob']:.1%} | "
              f"平局: {result['draw_prob']:.1%} | "
              f"客胜: {result['away_win_prob']:.1%}")
        print(f"  预测: {result['prediction']} (置信度: {result['confidence']:.1%})")
        print(f"  详情: 主队{result['details']['home_rating']}分 "
              f"({result['details']['home_stars']}星), "
              f"客队{result['details']['away_rating']}分 "
              f"({result['details']['away_stars']}星)")
    
    print("\n" + "=" * 70)
    print("对比旧模型（58.3%准确率，100%预测主胜）")
    print("=" * 70)
    print("\n新模型优势:")
    print("  ✓ 预测平局和客胜（旧模型0%）")
    print("  ✓ 基于真实球员能力，而非FIFA排名")
    print("  ✓ 考虑位置重要性（前锋>中场>后卫>门将）")
    print("  ✓ 星级球员加成（如梅西、姆巴佩）")
    print("  ✓ 大赛经验加成")
    print("  ✓ 实力接近时增加平局概率")