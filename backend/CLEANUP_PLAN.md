# 代码清理计划

## 当前状态
- Python 文件总数: 86
- 多版本 prediction_engine: v2, v3, v4, v5, v6
- 多版本入口文件: main.py, main_v2.py, main_v3.py, main_v6.py
- 测试文件残留: test_p0_*, test_training_v2.py

## 引用分析

| 文件 | 被引用 | 使用位置 |
|------|--------|----------|
| prediction_engine_v2.py | ✅ | main_v2.py |
| prediction_engine_v3.py | ✅ | groups.py, matches.py |
| prediction_engine_v4.py | ✅ | main_v2.py, accuracy.py |
| prediction_engine_v5.py | ❌ | 未被引用 |
| prediction_engine_v6.py | ✅ | bayesian.py, prediction_v6.py |
| main.py | ❌ | 旧版本入口 |
| main_v2.py | ✅ | 当前主入口 |
| main_v3.py | ❌ | 多余入口 |
| main_v6.py | ❌ | 多余入口 |

## 清理计划

### 第一阶段：安全删除（确认无引用）
- [ ] 删除 prediction_engine_v5.py
- [ ] 删除 main.py（旧版本）
- [ ] 删除 main_v3.py
- [ ] 删除 main_v6.py
- [ ] 删除 test_p0_optimization.py
- [ ] 删除 test_p0_integration.py
- [ ] 删除 test_training_v2.py
- [ ] 清理所有 __pycache__

### 第二阶段：合并多版本（需谨慎）
- [ ] 分析 prediction_engine v2-v6 差异
- [ ] 统一为单一版本
- [ ] 更新所有引用

## 预计收益
- 减少约 50KB 代码
- 提高可维护性
- 减少混淆
