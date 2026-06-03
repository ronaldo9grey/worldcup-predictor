"""
比分预测器 - 基于泊松回归模型
"""
import numpy as np
from scipy.stats import poisson
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ScorePrediction:
    """比分预测结果"""
    score: str
    probability: float
    result: str  # 主胜/平局/客胜


@dataclass
class OverUnderPrediction:
    """大小球预测结果"""
    line: float
    over_prob: float
    under_prob: float
    recommendation: str
    confidence: float
    reasoning: str


class ScorePredictor:
    """
    比分预测器
    
    基于泊松分布计算比分概率
    - 足球进球数近似服从泊松分布
    - 计算每个比分组合的概率
    - 输出最可能的比分
    """
    
    def __init__(self):
        # 历史平均进球数（世界杯数据）
        self.avg_home_goals = 1.5
        self.avg_away_goals = 1.2
        
        # 因子权重
        self.factor_weights = {
            "elo_diff": 0.30,
            "rank_diff": 0.25,
            "home_advantage": 0.20,
            "attack_strength": 0.15,
            "defense_weakness": 0.10
        }
    
    def predict(
        self,
        home_team: Dict,
        away_team: Dict,
        match_context: Optional[Dict] = None
    ) -> Dict:
        """
        预测比分
        
        参数：
        - home_team: 主队信息 {elo, rank, attack_rating, defense_rating, form_score}
        - away_team: 客队信息
        - match_context: 比赛上下文 {is_knockout, weather, importance}
        
        返回：
        - expected_goals: 期望进球数
        - score_predictions: 最可能的3个比分
        - over_under: 大小球预测
        """
        
        # 1. 计算期望进球数
        lambda_home = self._calculate_expected_goals(
            home_team, away_team, is_home=True, match_context=match_context
        )
        
        lambda_away = self._calculate_expected_goals(
            away_team, home_team, is_home=False, match_context=match_context
        )
        
        # 2. 生成比分概率矩阵
        score_probs = self._generate_score_matrix(lambda_home, lambda_away)
        
        # 3. 获取最可能的3个比分
        top_scores = self._get_top_scores(score_probs, n=3)
        
        # 4. 计算大小球
        over_under = self._calculate_over_under(
            lambda_home, lambda_away,
            match_context=match_context
        )
        
        return {
            "expected_goals": {
                "home": round(lambda_home, 2),
                "away": round(lambda_away, 2),
                "total": round(lambda_home + lambda_away, 2)
            },
            "score_predictions": [
                {
                    "score": pred.score,
                    "probability": f"{pred.probability * 100:.1f}%",
                    "result": pred.result
                }
                for pred in top_scores
            ],
            "over_under": {
                "line": over_under.line,
                "over_probability": f"{over_under.over_prob:.1f}%",
                "under_probability": f"{over_under.under_prob:.1f}%",
                "recommendation": over_under.recommendation,
                "confidence": f"{over_under.confidence:.0f}%",
                "reasoning": over_under.reasoning
            },
            "score_matrix": score_probs  # 完整概率矩阵
        }
    
    def _calculate_expected_goals(
        self,
        team: Dict,
        opponent: Dict,
        is_home: bool,
        match_context: Optional[Dict] = None
    ) -> float:
        """
        计算期望进球数
        
        基于多个因子调整基础进球数
        """
        
        # 基础进球数
        base_goals = self.avg_home_goals if is_home else self.avg_away_goals
        
        # 计算各因子的影响
        factors = {}
        
        # 1. Elo差异
        elo_diff = (team.get("elo", 1800) - opponent.get("elo", 1800)) / 100
        factors["elo_diff"] = elo_diff * self.factor_weights["elo_diff"]
        
        # 2. 排名差异（排名越低越好，所以用对手排名减己方排名）
        rank_diff = (opponent.get("rank", 50) - team.get("rank", 50)) / 20
        factors["rank_diff"] = rank_diff * self.factor_weights["rank_diff"]
        
        # 3. 主场优势
        home_advantage = 0.3 if is_home else -0.1
        factors["home_advantage"] = home_advantage * self.factor_weights["home_advantage"]
        
        # 4. 进攻强度
        attack_rating = team.get("attack_rating", 1.0)
        factors["attack_strength"] = (attack_rating - 1.0) * self.factor_weights["attack_strength"]
        
        # 5. 防守弱点（对手防守越弱，进球越多）
        defense_rating = opponent.get("defense_rating", 1.0)
        defense_weakness = 1.0 / defense_rating - 1.0
        factors["defense_weakness"] = defense_weakness * self.factor_weights["defense_weakness"]
        
        # 6. 近期状态
        form_score = team.get("form_score", 0)  # -1 到 1
        factors["form"] = form_score * 0.1
        
        # 7. 比赛上下文调整
        if match_context:
            # 淘汰赛进球更少
            if match_context.get("is_knockout"):
                factors["knockout"] = -0.15
            
            # 重要比赛更谨慎
            if match_context.get("importance") == "high":
                factors["importance"] = -0.1
        
        # 加权求和
        total_adjustment = sum(factors.values())
        
        # 计算期望进球数
        expected_goals = base_goals * (1 + total_adjustment)
        
        # 限制范围 [0.3, 3.5]
        return float(np.clip(expected_goals, 0.3, 3.5))
    
    def _generate_score_matrix(
        self,
        lambda_home: float,
        lambda_away: float,
        max_goals: int = 6
    ) -> Dict[str, float]:
        """
        生成比分概率矩阵
        
        基于泊松分布计算每个比分组合的概率
        P(比分k-j) = P(主队进k球) × P(客队进j球)
        """
        
        score_matrix = {}
        
        for home_goals in range(max_goals):
            for away_goals in range(max_goals):
                # 泊松概率
                prob_home = poisson.pmf(home_goals, lambda_home)
                prob_away = poisson.pmf(away_goals, lambda_away)
                
                # 联合概率（假设独立）
                prob = prob_home * prob_away
                
                score_matrix[f"{home_goals}-{away_goals}"] = round(prob, 6)
        
        return score_matrix
    
    def _get_top_scores(
        self,
        score_probs: Dict[str, float],
        n: int = 3
    ) -> List[ScorePrediction]:
        """
        获取最可能的N个比分
        """
        
        # 按概率排序
        sorted_scores = sorted(
            score_probs.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # 返回前N个
        predictions = []
        for score, prob in sorted_scores[:n]:
            result = self._get_result_from_score(score)
            predictions.append(ScorePrediction(
                score=score,
                probability=prob,
                result=result
            ))
        
        return predictions
    
    def _get_result_from_score(self, score: str) -> str:
        """从比分判断结果"""
        home, away = map(int, score.split('-'))
        
        if home > away:
            return "主胜"
        elif home < away:
            return "客胜"
        else:
            return "平局"
    
    def _calculate_over_under(
        self,
        lambda_home: float,
        lambda_away: float,
        line: float = 2.5,
        match_context: Optional[Dict] = None
    ) -> OverUnderPrediction:
        """
        计算大小球概率
        
        总进球数 = 主队进球 + 客队进球
        总进球数也近似服从泊松分布，参数为 λ_home + λ_away
        """
        
        # 总期望进球数
        total_lambda = lambda_home + lambda_away
        
        # 计算总进球数概率分布
        total_probs = {}
        for total in range(10):
            total_probs[total] = poisson.pmf(total, total_lambda)
        
        # 计算大球和小球概率
        over_prob = sum(total_probs[k] for k in total_probs if k > line) * 100
        under_prob = sum(total_probs[k] for k in total_probs if k <= line) * 100
        
        # 推荐结果
        if over_prob > 55:
            recommendation = f"大{line}"
            confidence = over_prob
        elif under_prob > 55:
            recommendation = f"小{line}"
            confidence = under_prob
        else:
            recommendation = "观望"
            confidence = max(over_prob, under_prob)
        
        # 生成分析理由
        reasoning = self._generate_over_under_reasoning(
            lambda_home, lambda_away, recommendation, match_context
        )
        
        return OverUnderPrediction(
            line=line,
            over_prob=round(over_prob, 1),
            under_prob=round(under_prob, 1),
            recommendation=recommendation,
            confidence=round(confidence, 0),
            reasoning=reasoning
        )
    
    def _generate_over_under_reasoning(
        self,
        lambda_home: float,
        lambda_away: float,
        recommendation: str,
        match_context: Optional[Dict] = None
    ) -> str:
        """生成大小球分析理由"""
        
        total_expected = lambda_home + lambda_away
        
        reasons = []
        
        # 期望进球数
        if total_expected < 2.0:
            reasons.append(f"预期总进球数仅{total_expected:.1f}球")
        elif total_expected > 3.5:
            reasons.append(f"预期总进球数高达{total_expected:.1f}球")
        else:
            reasons.append(f"预期总进球数{total_expected:.1f}球")
        
        # 比赛类型
        if match_context:
            if match_context.get("is_knockout"):
                reasons.append("淘汰赛阶段球队更谨慎")
            
            if match_context.get("importance") == "high":
                reasons.append("重要比赛防守优先")
        
        # 推荐
        if recommendation.startswith("小"):
            reasons.append("看好小球")
        elif recommendation.startswith("大"):
            reasons.append("看好大球")
        else:
            reasons.append("概率接近，建议观望")
        
        return "，".join(reasons)


# 测试代码
if __name__ == "__main__":
    # 测试用例
    predictor = ScorePredictor()
    
    # 墨西哥 vs 南非
    home_team = {
        "elo": 1850,
        "rank": 15,
        "attack_rating": 1.2,
        "defense_rating": 1.1,
        "form_score": 0.3
    }
    
    away_team = {
        "elo": 1650,
        "rank": 60,
        "attack_rating": 0.8,
        "defense_rating": 0.9,
        "form_score": -0.2
    }
    
    match_context = {
        "is_knockout": False,
        "importance": "high"  # 揭幕战
    }
    
    result = predictor.predict(home_team, away_team, match_context)
    
    print("=" * 50)
    print("比分预测结果")
    print("=" * 50)
    print(f"期望进球: 主队 {result['expected_goals']['home']} vs 客队 {result['expected_goals']['away']}")
    print(f"最可能比分:")
    for pred in result['score_predictions']:
        print(f"  {pred['score']} - {pred['probability']} ({pred['result']})")
    print(f"\n大小球: {result['over_under']['recommendation']}")
    print(f"理由: {result['over_under']['reasoning']}")
    print("=" * 50)
