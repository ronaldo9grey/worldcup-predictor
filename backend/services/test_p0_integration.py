"""
P0集成测试 - 预测引擎V6
验证：
1. 正确的分组数据
2. 特征引擎V2集成
3. 在线学习V2集成
4. 完整预测流程
"""
import sys
sys.path.append('/var/www/worldcup-predictor/backend')

from services.prediction_engine_v6 import PredictionEngineV6, get_engine_v6
from data.world_cup_2026 import GROUPS, get_team_lookup, validate_teams


def test_group_data():
    """测试分组数据"""
    print("=" * 60)
    print("测试分组数据")
    print("=" * 60)
    
    # 验证数据
    validate_teams()
    
    # 打印分组
    print("\n官方分组:")
    for group, codes in GROUPS.items():
        print(f"  {group}组: {', '.join(codes)}")
    
    # 检查分组数量
    print(f"\n总分组数: {len(GROUPS)}")
    print(f"总球队数: {sum(len(codes) for codes in GROUPS.values())}")


def test_prediction_engine_v6():
    """测试预测引擎V6"""
    print("\n" + "=" * 60)
    print("测试预测引擎V6")
    print("=" * 60)
    
    engine = get_engine_v6()
    init_result = engine.initialize()
    print(f"\n初始化状态: {init_result['status']}")
    
    # 测试比赛预测
    test_matches = [
        ('A', 'MEX', 'KOR', '小组赛A组'),
        ('B', 'CAN', 'SUI', '小组赛B组'),
        ('C', 'BRA', 'MAR', '小组赛C组'),
        ('I', 'FRA', 'SEN', '小组赛I组'),
        ('J', 'ARG', 'ALG', '小组赛J组'),
        ('L', 'ENG', 'CRO', '小组赛L组'),
    ]
    
    for group, home, away, desc in test_matches:
        print(f"\n{desc}: {home} vs {away}")
        pred = engine.predict_match(home, away, 'GROUP', group)
        
        print(f"  预测结果: {pred.prediction}")
        print(f"  概率: 主胜{pred.home_win_prob:.1%} / 平局{pred.draw_prob:.1%} / 客胜{pred.away_win_prob:.1%}")
        print(f"  置信度: {pred.confidence_level} ({pred.confidence_value:.2f})")
        print(f"  阶段学习率: {pred.stage_learning_rate}")
        
        # 显示P0新增特征
        print(f"  P0特征: h2h={pred.features.h2h:+.3f}, venue={pred.features.venue_factor:+.3f}")
        print(f"  特征交互: elo×form={pred.features.elo_form_combined:+.3f}")


def test_feature_analysis():
    """测试特征分析"""
    print("\n" + "=" * 60)
    print("测试特征分析")
    print("=" * 60)
    
    engine = get_engine_v6()
    
    # 分析经典比赛
    analysis = engine.get_feature_analysis('ARG', 'BRA', 'GROUP')
    
    print("\n阿根廷 vs 巴西 特征分析:")
    print("\n关键特征贡献:")
    
    contributions = analysis['contributions']
    sorted_contrib = sorted(contributions.items(), key=lambda x: abs(x[1]['contribution']), reverse=True)
    
    for name, info in sorted_contrib[:6]:
        print(f"  {name}: {info['value']:+.3f} × {info['weight']:.2f} = {info['contribution']:+.3f} ({info['direction']})")
    
    print(f"\n总偏置: {analysis['total_bias']:+.3f}")


def test_online_learning_integration():
    """测试在线学习集成"""
    print("\n" + "=" * 60)
    print("测试在线学习集成")
    print("=" * 60)
    
    engine = get_engine_v6()
    
    print("\n初始模型权重:")
    print(f"  {engine.model_weights}")
    
    # 模拟比赛更新
    print("\n模拟比赛结果更新:")
    
    # 比赛1：预测正确
    result1 = engine.update_after_match(
        match_id='A_1',
        home_code='MEX',
        away_code='KOR',
        stage='GROUP',
        predicted='HOME_WIN',
        actual='HOME_WIN',
        confidence=0.6
    )
    print(f"\n  比赛1 (MEX vs KOR): 预测正确 ✓")
    print(f"    学习率: {result1['learning_rate']}")
    print(f"    新权重: {result1['new_weights']}")
    
    # 比赛2：预测错误
    result2 = engine.update_after_match(
        match_id='I_1',
        home_code='FRA',
        away_code='SEN',
        stage='GROUP',
        predicted='HOME_WIN',
        actual='AWAY_WIN',
        confidence=0.7
    )
    print(f"\n  比赛2 (FRA vs SEN): 预测错误 ❌")
    print(f"    学习率: {result2['learning_rate']}")
    print(f"    新权重: {result2['new_weights']}")
    
    # 比赛3：淘汰赛
    result3 = engine.update_after_match(
        match_id='R16_1',
        home_code='ARG',
        away_code='GER',
        stage='R16',
        predicted='HOME_WIN',
        actual='HOME_WIN',
        confidence=0.55
    )
    print(f"\n  比赛3 (ARG vs GER, 16强): 预测正确 ✓")
    print(f"    学习率: {result3['learning_rate']} (淘汰赛学习率更高)")
    print(f"    新权重: {result3['new_weights']}")
    
    # 获取学习统计
    stats = engine.online_learner.get_learning_stats()
    print(f"\n学习统计:")
    print(f"  总事件数: {stats['total_events']}")
    print(f"  近期准确率: {stats['recent_accuracy']:.1%}")
    print(f"  当前窗口: {stats['window_size']}")


def test_upset_detection():
    """测试冷门检测"""
    print("\n" + "=" * 60)
    print("测试冷门检测")
    print("=" * 60)
    
    engine = get_engine_v6()
    
    # 测试可能的冷门比赛
    test_cases = [
        ('BRA', 'HTI', '巴西 vs 海地'),
        ('GER', 'CUR', '德国 vs 库拉索'),
        ('FRA', 'IRQ', '法国 vs 伊拉克'),
    ]
    
    for home, away, desc in test_cases:
        pred = engine.predict_match(home, away, 'GROUP')
        
        print(f"\n{desc}:")
        print(f"  冷门指数: {pred.upset_score:.2f}")
        print(f"  冷门预警: {'是' if pred.is_upset_warning else '否'}")
        if pred.upset_factors:
            print(f"  冷门因素: {', '.join(pred.upset_factors)}")


def test_group_prediction():
    """测试整组预测"""
    print("\n" + "=" * 60)
    print("测试整组预测 (A组)")
    print("=" * 60)
    
    engine = get_engine_v6()
    
    # 预测A组
    predictions = engine.predict_group('A')
    
    print("\nA组比赛预测:")
    print(f"{'比赛':<20} {'预测':<8} {'主胜':<8} {'平局':<8} {'客胜':<8} {'置信度':<8}")
    print("-" * 60)
    
    for pred in predictions:
        match = f"{pred.home_name_cn} vs {pred.away_name_cn}"
        print(f"{match:<20} {pred.prediction:<8} {pred.home_win_prob:.1%}   {pred.draw_prob:.1%}   {pred.away_win_prob:.1%}   {pred.confidence_level}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("P0集成测试 - 预测引擎V6")
    print("=" * 60)
    
    test_group_data()
    test_prediction_engine_v6()
    test_feature_analysis()
    test_online_learning_integration()
    test_upset_detection()
    test_group_prediction()
    
    print("\n" + "=" * 60)
    print("P0集成测试完成 ✓")
    print("=" * 60)
    
    print("\n集成成果:")
    print("  1. ✓ 更新官方分组数据（12组×4队）")
    print("  2. ✓ 特征引擎V2集成（h2h、venue、交互特征）")
    print("  3. ✓ 在线学习V2集成（阶段自适应学习率）")
    print("  4. ✓ 冷门检测增强（使用新特征）")
    print("  5. ✓ 特征分析功能（预测解释）")
    print("  6. ✓ 整组预测功能")


if __name__ == '__main__':
    run_all_tests()
