# 世界杯预测系统增强功能开发计划

## 任务目标

基于对标结果，实现三项核心功能：
1. 预测状态机制（待揭晓/已命中/未命中）
2. 比分预测（泊松回归模型）
3. 大小球预测

---

## 阶段1：预测状态机制

### 1.1 数据库模型设计

```python
# models/prediction.py
class PredictionStatus(Enum):
    PENDING = "待揭晓"
    CORRECT = "已命中"
    INCORRECT = "未命中"

class MatchPrediction(Base):
    __tablename__ = "predictions"
    
    id: int
    match_id: str
    group_name: str
    match_index: int
    
    # 预测结果
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    final_prediction: str  # HOME_WIN, DRAW, AWAY_WIN
    
    # 比分预测
    score_prediction: str  # "2-1"
    expected_home_goals: float
    expected_away_goals: float
    
    # 大小球
    over_under_line: float  # 2.5
    over_prob: float
    under_prob: float
    over_under_recommendation: str  # "大2.5" or "小2.5"
    
    # 状态
    status: PredictionStatus = PredictionStatus.PENDING
    actual_result: Optional[str]  # 实际结果
    actual_score: Optional[str]   # 实际比分
    
    # 时间戳
    created_at: datetime
    verified_at: Optional[datetime]
```

### 1.2 预测验证逻辑

```python
# services/prediction_verifier.py
async def verify_prediction(match_id: str, actual_result: dict):
    """
    验证预测结果
    
    actual_result = {
        "home_score": 2,
        "away_score": 1,
        "result": "HOME_WIN"
    }
    """
    prediction = await get_prediction(match_id)
    
    # 验证胜平负
    if prediction.final_prediction == actual_result["result"]:
        prediction.status = PredictionStatus.CORRECT
    else:
        prediction.status = PredictionStatus.INCORRECT
    
    # 验证比分
    prediction.actual_score = f"{actual_result['home_score']}-{actual_result['away_score']}"
    prediction.verified_at = datetime.now()
    
    await save_prediction(prediction)
```

---

## 阶段2：比分预测（泊松回归）

### 2.1 核心算法

```python
# services/score_predictor.py
import numpy as np
from scipy.stats import poisson

class ScorePredictor:
    def predict(self, match_data: dict) -> dict:
        # 1. 计算期望进球数
        lambda_home = self._calculate_expected_goals(
            match_data["home_team"],
            match_data["away_team"],
            is_home=True
        )
        
        lambda_away = self._calculate_expected_goals(
            match_data["away_team"],
            match_data["home_team"],
            is_home=False
        )
        
        # 2. 生成比分概率矩阵
        score_probs = self._generate_score_matrix(lambda_home, lambda_away)
        
        # 3. 获取最可能的3个比分
        top_scores = self._get_top_scores(score_probs, n=3)
        
        # 4. 计算大小球
        over_under = self._calculate_over_under(lambda_home, lambda_away)
        
        return {
            "expected_goals": {
                "home": round(lambda_home, 2),
                "away": round(lambda_away, 2)
            },
            "score_predictions": top_scores,
            "over_under": over_under
        }
    
    def _calculate_expected_goals(self, team, opponent, is_home):
        """基于多个因子计算期望进球数"""
        # 基础进球数
        base_goals = 1.5 if is_home else 1.2
        
        # 因子调整
        elo_diff = (team["elo"] - opponent["elo"]) / 100
        rank_diff = (opponent["rank"] - team["rank"]) / 20
        home_advantage = 0.3 if is_home else -0.1
        
        # 加权计算
        adjustment = (elo_diff * 0.3 + rank_diff * 0.2 + home_advantage) * 0.2
        expected_goals = base_goals * (1 + adjustment)
        
        return np.clip(expected_goals, 0.3, 3.5)
```

### 2.2 比分概率矩阵

```python
def _generate_score_matrix(self, lambda_home, lambda_away, max_goals=6):
    """生成比分概率矩阵"""
    score_matrix = {}
    
    for home_goals in range(max_goals):
        for away_goals in range(max_goals):
            # 泊松概率
            prob_home = poisson.pmf(home_goals, lambda_home)
            prob_away = poisson.pmf(away_goals, lambda_away)
            
            # 联合概率
            prob = prob_home * prob_away
            score_matrix[f"{home_goals}-{away_goals}"] = prob
    
    return score_matrix
```

---

## 阶段3：大小球预测

### 3.1 计算逻辑

```python
def _calculate_over_under(self, lambda_home, lambda_away, line=2.5):
    """计算大小球概率"""
    total_expected = lambda_home + lambda_away
    
    # 计算总进球数概率分布
    total_probs = {}
    for total in range(10):
        # 总进球数服从泊松分布
        total_probs[total] = poisson.pmf(total, total_expected)
    
    # 计算大球和小球概率
    over_prob = sum(total_probs[k] for k in total_probs if k > line)
    under_prob = sum(total_probs[k] for k in total_probs if k <= line)
    
    # 推荐结果
    if over_prob > 0.55:
        recommendation = f"大{line}"
    elif under_prob > 0.55:
        recommendation = f"小{line}"
    else:
        recommendation = "观望"  # 概率接近，不建议投注
    
    return {
        "line": line,
        "over_prob": round(over_prob * 100, 1),
        "under_prob": round(under_prob * 100, 1),
        "recommendation": recommendation,
        "confidence": round(max(over_prob, under_prob) * 100, 1)
    }
```

---

## 实施步骤

### 步骤1：创建新模型和服务
- [ ] 创建 `models/prediction.py`
- [ ] 创建 `services/score_predictor.py`
- [ ] 创建 `services/prediction_verifier.py`

### 步骤2：修改现有 API
- [ ] 扩展 `/api/calculation/match/{group}/{idx}` 返回比分和大小球
- [ ] 新增 `/api/predictions/{match_id}/status` 查询预测状态
- [ ] 新增 `/api/predictions/{match_id}/verify` 验证预测结果

### 步骤3：前端展示
- [ ] 修改 MatchCalculation.vue 显示比分预测
- [ ] 修改 MatchCalculation.vue 显示大小球预测
- [ ] 添加预测状态徽章（待揭晓/已命中/未命中）

### 步骤4：测试验证
- [ ] 单元测试：泊松分布计算
- [ ] 单元测试：比分概率矩阵
- [ ] 集成测试：完整预测流程
- [ ] 手动测试：前端展示

---

## 预期效果

### API 响应示例

```json
{
  "match": "墨西哥 vs 南非",
  "prediction": {
    "win_draw_lose": {
      "home_win": 0.592,
      "draw": 0.237,
      "away_win": 0.171,
      "final": "主胜"
    },
    "score": {
      "expected_home_goals": 1.85,
      "expected_away_goals": 0.72,
      "top_predictions": [
        {"score": "2-0", "probability": "18.5%", "result": "主胜"},
        {"score": "1-0", "probability": "15.2%", "result": "主胜"},
        {"score": "2-1", "probability": "12.8%", "result": "主胜"}
      ]
    },
    "over_under": {
      "line": 2.5,
      "over_prob": 32.0,
      "under_prob": 68.0,
      "recommendation": "小2.5",
      "confidence": 68,
      "reasoning": "揭幕战节奏偏慢，墨西哥务实风格"
    }
  },
  "status": "待揭晓",
  "analysis": "墨西哥作为东道主占据多重优势..."
}
```

---

## 开发时间估算

- 阶段1（预测状态）：2-3小时
- 阶段2（比分预测）：3-4小时
- 阶段3（大小球）：2小时
- 前端展示：2-3小时
- 测试验证：1-2小时

**总计：10-14小时**
