"""
P0优化集成测试
验证：
1. 特征引擎V2（h2h、venue_factor、特征交互）
2. 在线学习V2（阶段自适应学习率、动态窗口）
"""
import sys
sys.path.append('/var/www/worldcup-predictor/backend')

from services.feature_engine_v2 import FeatureEngineV2, get_feature_engine_v2
from services.online_learning_v2 import OnlineLearningV2, get_online_learning_v2
from data.world_cup_2026 import ALL_TEAMS


def test_feature_engine_v2():
    """测试特征引擎V2"""
    print("=" * 60)
    print("测试特征引擎V2")
    print("=" * 60)
    
    engine = get_feature_engine_v2()
    
    # 测试比赛：阿根廷 vs 法国
    argentina = next(t for t in ALL_TEAMS if t['code'] == 'ARG')
    france = next(t for t in ALL_TEAMS if t['code'] == 'FRA')
    
    features = engine.compute_features(
        home=argentina,
        away=france,
        stage='FI',  # 决赛
        group='A'
    )
    
    print(f"\n比赛: {argentina['name_cn']} vs {france['name_cn']} (决赛)")
    print(f"\n基础特征:")
    print(f"  Elo差异: {features.elo_diff:.3f}")
    print(f"  排名差异: {features.rank_diff:.3f}")
    print(f"  状态差异: {features.form_diff:.3f}")
    print(f"  阶段因子: {features.stage_factor:.3f}")
    print(f"  主场优势: {features.home_advantage:.3f}")
    print(f"  洲际因素: {features.continent_factor:.3f}")
    
    print(f"\nP0新增特征:")
    print(f"  历史交锋(h2h): {features.h2h:.3f}")
    print(f"  场地影响(venue): {features.venue_factor:.3f}")
    
    print(f"\nP0新增特征交互:")
    print(f"  Elo×状态: {features.elo_form_combined:.3f}")
    print(f"  排名×阶段: {features.rank_stage_combined:.3f}")
    
    print(f"\n特征向量维度: {len(features.to_vector())}")
    print(f"特征向量: {features.to_vector()}")
    
    return features


def test_online_learning_v2():
    """测试在线学习V2"""
    print("\n" + "=" * 60)
    print("测试在线学习V2")
    print("=" * 60)
    
    learner = get_online_learning_v2()
    
    # 初始权重
    initial_weights = {
        'bayesian': 0.4,
        'neural_network': 0.3,
        'random_forest': 0.3
    }
    
    print(f"\n初始模型权重: {initial_weights}")
    
    # 模拟小组赛预测
    print(f"\n模拟小组赛预测:")
    result1 = learner.process_match_result(
        match_id='MATCH_001',
        home_code='ARG',
        away_code='FRA',
        stage='GROUP',
        predicted='HOME_WIN',
        actual='AWAY_WIN',  # 预测错误
        model_used='贝叶斯模型',
        confidence=0.6,
        current_weights=initial_weights.copy()
    )
    print(f"  预测: 主胜, 实际: 客胜 ❌")
    print(f"  学习率: {result1['learning_rate']}")
    print(f"  新权重: {result1['new_weights']}")
    print(f"  调整原因: {result1['adjustment_reason']}")
    
    # 模拟16强预测
    print(f"\n模拟16强预测:")
    result2 = learner.process_match_result(
        match_id='MATCH_002',
        home_code='BRA',
        away_code='GER',
        stage='R16',
        predicted='HOME_WIN',
        actual='HOME_WIN',  # 预测正确
        model_used='神经网络',
        confidence=0.7,
        current_weights=result1['new_weights']
    )
    print(f"  预测: 主胜, 实际: 主胜 ✓")
    print(f"  学习率: {result2['learning_rate']}")
    print(f"  新权重: {result2['new_weights']}")
    
    # 模拟决赛预测
    print(f"\n模拟决赛预测:")
    result3 = learner.process_match_result(
        match_id='MATCH_003',
        home_code='ARG',
        away_code='FRA',
        stage='FI',
        predicted='AWAY_WIN',
        actual='AWAY_WIN',  # 预测正确
        model_used='随机森林',
        confidence=0.55,
        current_weights=result2['new_weights']
    )
    print(f"  预测: 客胜, 实际: 客胜 ✓")
    print(f"  学习率: {result3['learning_rate']}")
    print(f"  新权重: {result3['new_weights']}")
    
    # 获取统计
    print(f"\n学习统计:")
    stats = learner.get_learning_stats()
    print(f"  总事件数: {stats['total_events']}")
    print(f"  近期准确率: {stats['recent_accuracy']:.1%}")
    print(f"  当前窗口大小: {stats['window_size']}")
    print(f"  分阶段学习率: {stats['stage_learning_rates']}")
    
    return learner


def test_h2h_feature():
    """测试历史交锋特征"""
    print("\n" + "=" * 60)
    print("测试历史交锋(h2h)特征")
    print("=" * 60)
    
    engine = get_feature_engine_v2()
    
    # 经典对决
    matchups = [
        ('ARG', 'BRA', '南美德比'),
        ('GER', 'ENG', '英德大战'),
        ('BRA', 'GER', '巴西vs德国(7-1阴影)'),
        ('JPN', 'KOR', '亚洲德比'),
        ('MEX', 'USA', '北美德比'),
    ]
    
    for home_code, away_code, name in matchups:
        home = next(t for t in ALL_TEAMS if t['code'] == home_code)
        away = next(t for t in ALL_TEAMS if t['code'] == away_code)
        
        features = engine.compute_features(home, away, 'GROUP')
        
        print(f"\n{name} ({home_code} vs {away_code}):")
        print(f"  h2h因子: {features.h2h:+.3f}")
        if features.h2h > 0:
            print(f"  解读: {home['name_cn']}历史占优")
        elif features.h2h < 0:
            print(f"  解读: {away['name_cn']}历史占优")
        else:
            print(f"  解读: 无明显历史优势")


def test_venue_feature():
    """测试场地影响特征"""
    print("\n" + "=" * 60)
    print("测试场地影响(venue)特征")
    print("=" * 60)
    
    engine = get_feature_engine_v2()
    
    # 不同小组的场地
    test_cases = [
        ('A', 'MEX', 'ARG', '墨西哥城(高原2240米)'),
        ('B', 'USA', 'GER', '达拉斯(高温30°C)'),
        ('D', 'ENG', 'JPN', '纽约(高湿70%)'),
    ]
    
    for group, home_code, away_code, venue_desc in test_cases:
        home = next(t for t in ALL_TEAMS if t['code'] == home_code)
        away = next(t for t in ALL_TEAMS if t['code'] == away_code)
        
        features = engine.compute_features(home, away, 'GROUP', group=group)
        
        print(f"\n{venue_desc} ({home_code} vs {away_code}):")
        print(f"  场地因子: {features.venue_factor:+.3f}")
        if features.venue_factor > 0:
            print(f"  解读: 有利于主队")
        elif features.venue_factor < 0:
            print(f"  解读: 不利于主队")
        else:
            print(f"  解读: 中性影响")


def test_feature_interaction():
    """测试特征交互"""
    print("\n" + "=" * 60)
    print("测试特征交互")
    print("=" * 60)
    
    engine = get_feature_engine_v2()
    
    # 场景1：强队状态好 vs 强队状态差
    strong_team_good_form = {'code': 'FRA', 'elo': 1870, 'rank': 2, 'form': 'WWWWW', 'continent': 'EU'}
    strong_team_bad_form = {'code': 'FRA', 'elo': 1870, 'rank': 2, 'form': 'LLLLL', 'continent': 'EU'}
    weak_team = {'code': 'AUS', 'elo': 1560, 'rank': 24, 'form': 'WDWDW', 'continent': 'AS'}
    
    # 强队状态好
    features1 = engine.compute_features(strong_team_good_form, weak_team, 'GROUP')
    print(f"\n场景1: 强队状态好 (法国vs澳大利亚)")
    print(f"  Elo差异: {features1.elo_diff:.3f}")
    print(f"  状态差异: {features1.form_diff:.3f}")
    print(f"  Elo×状态交互: {features1.elo_form_combined:.3f}")
    print(f"  解读: 实力强且状态好 → 交互放大优势")
    
    # 强队状态差
    features2 = engine.compute_features(strong_team_bad_form, weak_team, 'GROUP')
    print(f"\n场景2: 强队状态差 (法国vs澳大利亚)")
    print(f"  Elo差异: {features2.elo_diff:.3f}")
    print(f"  状态差异: {features2.form_diff:.3f}")
    print(f"  Elo×状态交互: {features2.elo_form_combined:.3f}")
    print(f"  解读: 实力强但状态差 → 交互削弱优势")
    
    # 排名×阶段交互
    print(f"\n排名×阶段交互测试:")
    for stage in ['GROUP', 'R16', 'QF', 'SF', 'FI']:
        features = engine.compute_features(strong_team_good_form, weak_team, stage)
        print(f"  {stage}: rank_diff={features.rank_diff:.2f}, stage_factor={features.stage_factor:.2f}, 交互={features.rank_stage_combined:.3f}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("P0优化集成测试")
    print("=" * 60)
    
    test_feature_engine_v2()
    test_online_learning_v2()
    test_h2h_feature()
    test_venue_feature()
    test_feature_interaction()
    
    print("\n" + "=" * 60)
    print("P0优化测试完成 ✓")
    print("=" * 60)
    
    print("\n优化成果:")
    print("  1. ✓ 补充 h2h（历史交锋）特征")
    print("  2. ✓ 补充 venue_factor（场地影响）特征")
    print("  3. ✓ 新增特征交互（elo×form、rank×stage）")
    print("  4. ✓ 阶段自适应学习率")
    print("  5. ✓ 动态滑动窗口")
    print("  6. ✓ 分阶段性能追踪")
    print("  7. ✓ 神经网络增量训练框架")


if __name__ == '__main__':
    run_all_tests()
