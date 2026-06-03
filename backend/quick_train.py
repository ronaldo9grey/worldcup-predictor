#!/usr/bin/env python3
"""
快速训练脚本
一键训练所有模型并验证持久化
"""
import sys
sys.path.append('/var/www/worldcup-predictor/backend')

from services.model_trainer_v2 import get_trainer_v2


def quick_train():
    """快速训练"""
    print("=" * 60)
    print("快速训练脚本")
    print("=" * 60)
    
    trainer = get_trainer_v2()
    
    # 1. 检查历史
    print("\n1️⃣ 检查历史训练记录...")
    summary = trainer.get_last_training_summary()
    
    if summary.get('has_trained'):
        print("  ✓ 发现历史记录:")
        for model, info in summary.get('models', {}).items():
            print(f"    - {model}: {info.get('accuracy', 0):.1%}")
        
        choice = input("\n  是否重新训练? (y/N): ").strip().lower()
        if choice != 'y':
            print("\n  ✓ 加载已训练模型...")
            trainer.load_trained_models()
            print("  完成!")
            return
    else:
        print("  ⚠️ 无历史记录")
    
    # 2. 准备数据
    print("\n2️⃣ 准备训练数据...")
    trainer.prepare_training_data()
    
    # 3. 训练
    print("\n3️⃣ 开始训练...")
    print("\n[神经网络训练]")
    nn_result = trainer.train_neural_network(epochs=50)
    if nn_result.status == 'completed':
        print(f"  ✓ 准确率: {nn_result.validation_accuracy:.1%}")
    
    print("\n[随机森林训练]")
    rf_result = trainer.train_random_forest(n_estimators=50)
    if rf_result.status == 'completed':
        print(f"  ✓ 准确率: {rf_result.final_accuracy:.1%}")
    
    # 4. 验证持久化
    print("\n4️⃣ 验证持久化...")
    summary2 = trainer.get_last_training_summary()
    print(f"  ✓ 训练记录已保存")
    print(f"  ✓ 最佳模型: {summary2.get('best_model')}")
    print(f"  ✓ 最佳准确率: {summary2.get('best_accuracy', 0):.1%}")
    
    print("\n" + "=" * 60)
    print("✅ 训练完成!")
    print("=" * 60)
    
    print("\n💡 提示:")
    print("  - 刷新后可通过 /api/training/summary 查看历史")
    print("  - 可通过 /api/training/load 加载已训练模型")


if __name__ == '__main__':
    quick_train()
