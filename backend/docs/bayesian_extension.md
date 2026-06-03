# 贝叶斯可视化扩展

## 功能说明

这是预测系统的扩展功能，用于展示贝叶斯推断的详细过程，**不影响原有预测逻辑**。

## API接口

### 1. 获取贝叶斯更新过程
```
GET /api/bayesian/process?home_code=ARG&away_code=FRA&stage=FI
```

返回5步详细过程：
1. **获取先验概率** - 历史世界杯统计
2. **获取模型预测** - 权重预测引擎输出
3. **贝叶斯更新** - 加权平均计算后验概率
4. **计算置信区间** - 95%置信区间量化不确定性
5. **输出预测结论** - 综合分析和建议

### 2. 获取贝叶斯配置
```
GET /api/bayesian/config
```

返回贝叶斯参数说明和核心理念。

### 3. 获取先验概率来源
```
GET /api/bayesian/prior-source
GET /api/bayesian/prior-source/{stage}
```

展示历史世界杯数据如何转化为先验概率。

### 4. 先验与模型对比
```
GET /api/bayesian/comparison?stage=GROUP
```

展示三种典型场景下贝叶斯更新如何修正预测：
- 强队碾压：防止过度自信
- 势均力敌：保持均匀分布
- 冷门预警：保留冷门可能性

### 5. 贝叶斯原理解释
```
GET /api/bayesian/explain
```

以通俗语言解释贝叶斯推断在足球预测中的应用。

## 技术实现

### 新增文件
- `backend/services/bayesian_visualizer.py` - 贝叶斯可视化服务（~20KB）
- `backend/api/bayesian.py` - API路由（~10KB）

### 修改文件
- `backend/main_v2.py` - 仅添加路由挂载

### 核心逻辑

```python
# 贝叶斯更新公式
P(结果|数据) = α × P_model + (1-α) × P_prior

其中：
- α = 0.7（模型权重）
- P_model = 权重预测引擎输出
- P_prior = 历史世界杯统计
```

## 使用示例

```bash
# 查看阿根廷vs法国决赛的贝叶斯更新过程
curl "http://localhost:8011/api/bayesian/process?home_code=ARG&away_code=FRA&stage=FI"

# 查看小组赛先验概率来源
curl "http://localhost:8011/api/bayesian/prior-source/GROUP"

# 查看贝叶斯参数配置
curl "http://localhost:8011/api/bayesian/config"
```

## 数据来源

### 先验概率来源
- 2018俄罗斯世界杯（64场比赛）
- 2022卡塔尔世界杯（64场比赛）
- 总计128场比赛统计

### 关键发现
- 小组赛主胜率：41%（冷门多）
- 淘汰赛主胜率：44%+
- 决赛主胜率：50%（势均力敌）

## 前端集成建议

可以在「准确率」或「模型」页面添加一个「贝叶斯详情」按钮，点击后弹窗展示：
1. 5步更新过程（带可视化）
2. 先验vs模型vs后验对比图
3. 置信区间可视化

---

**版本**: v2.4.1  
**日期**: 2026-05-31  
**状态**: ✅ 已部署