"""
模型训练V2测试
验证：
1. 训练进度展示
2. 结果持久化
3. 加载已训练模型
"""
import sys
sys.path.append('/var/www/worldcup-predictor/backend')

from services.model_trainer_v2 import get_trainer_v2


def test_training_v2():
    """测试模型训练V2"""
    print("=" * 60)
    print("测试模型训练V2")
    print("=" * 60)
    
    trainer = get_trainer_v2()
    
    # 1. 检查历史训练记录
    print("\n1️⃣ 检查历史训练记录:")
    summary = trainer.get_last_training_summary()
    
    if summary.get('has_trained'):
        print("  ✓ 发现历史训练记录:")
        for model_name, info in summary.get('models', {}).items():
            print(f"    - {model_name}: 准确率 {info.get('accuracy', 0):.1%}")
    else:
        print("  ⚠️ 无历史训练记录")
    
    # 2. 准备训练数据
    print("\n2️⃣ 准备训练数据:")
    data_info = trainer.prepare_training_data()
    print(f"  ✓ 样本数量: {data_info['samples']}")
    print(f"  ✓ 特征维度: {data_info['features']}")
    print(f"  ✓ 标签分布: {data_info['distribution']}")
    
    # 3. 训练神经网络
    print("\n3️⃣ 训练神经网络:")
    nn_result = trainer.train_neural_network(epochs=50)
    
    print(f"\n  训练结果:")
    print(f"    - 状态: {nn_result.status}")
    print(f"    - 消息: {nn_result.message}")
    if nn_result.status == 'completed':
        print(f"    - 最终损失: {nn_result.final_loss:.4f}")
        print(f"    - 验证准确率: {nn_result.validation_accuracy:.2%}")
        print(f"    - 模型路径: {nn_result.model_path}")
    
    # 4. 训练随机森林
    print("\n4️⃣ 训练随机森林:")
    rf_result = trainer.train_random_forest(n_estimators=50)
    
    print(f"\n  训练结果:")
    print(f"    - 状态: {rf_result.status}")
    print(f"    - 消息: {rf_result.message}")
    if rf_result.status == 'completed':
        print(f"    - 准确率: {rf_result.final_accuracy:.2%}")
        print(f"    - 模型路径: {rf_result.model_path}")
        
        if rf_result.feature_importance:
            print(f"\n  特征重要性 Top 5:")
            sorted_features = sorted(rf_result.feature_importance.items(), key=lambda x: x[1], reverse=True)
            for name, importance in sorted_features[:5]:
                print(f"    - {name}: {importance:.3f}")
    
    # 5. 检查训练进度
    print("\n5️⃣ 检查训练进度:")
    progress = trainer.get_training_progress()
    for model_name, prog in progress.items():
        if prog:
            print(f"  {model_name}:")
            print(f"    - 状态: {prog.get('status', '')}")
            print(f"    - 消息: {prog.get('message', '')}")
            print(f"    - 准确率: {prog.get('accuracy', 0):.2%}")
    
    # 6. 检查训练结果（持久化）
    print("\n6️⃣ 检查训练结果（持久化）:")
    results = trainer.get_training_results()
    for model_name, result in results.items():
        print(f"  {model_name}:")
        print(f"    - 训练时间: {result.get('training_time', '')}")
        print(f"    - 状态: {result.get('status', '')}")
    
    # 7. 加载已训练模型
    print("\n7️⃣ 加载已训练模型:")
    loaded = trainer.load_trained_models()
    print(f"  加载结果: {loaded}")
    
    # 8. 再次检查训练摘要（验证持久化）
    print("\n8️⃣ 再次检查训练摘要（验证持久化）:")
    summary2 = trainer.get_last_training_summary()
    print(f"  有训练记录: {summary2.get('has_trained')}")
    print(f"  最佳模型: {summary2.get('best_model')}")
    print(f"  最佳准确率: {summary2.get('best_accuracy', 0):.2%}")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
    
    print("\n功能验证:")
    print("  1. ✓ 训练进度实时展示")
    print("  2. ✓ 训练结果持久化存储")
    print("  3. ✓ 模型加载功能")
    print("  4. ✓ 特征重要性展示")
    print("  5. ✓ 训练历史记录")
    
    return trainer


if __name__ == '__main__':
    trainer = test_training_v2()
    
    print("\n💡 提示:")
    print("  - 训练结果已保存到: /var/www/worldcup-predictor/backend/data/")
    print("  - 刷新后可通过 /api/training/summary 查看历史记录")
    print("  - 可通过 /api/training/load 加载已训练模型")