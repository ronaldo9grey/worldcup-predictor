"""
预测引擎 V5 - 数据扩展版
整合伤病、赔率、社交媒体情感等新数据因子
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
import sys

sys.path.append('/var/www/worldcup-predictor/backend')

from services.prediction_engine_v4 import PredictionEngineV4, MatchPredictionV4
from data.injuries import get_injury_impact, compare_injuries
from data.odds import get_consensus_odds, compare_model_vs_market
from data.social_sentiment import get_sentiment_impact, compare_sentiments
from data.players import get_squad_strength
from data.coaches import get_coach_rating
from data.venue_weather import get_venue_impact


@dataclass
class MatchPredictionV5(MatchPredictionV4):
    """V5比赛预测结果 - 新增数据扩展"""
    
    # 伤病影响
    home_injury_impact: float = 0.0
    away_injury_impact: float = 0.0
    injury_advantage: float = 0.0
    
    # 社交情感
    home_sentiment_impact: float = 0.0
    away_sentiment_impact: float = 0.0
    sentiment_advantage: float = 0.0
    
    # 市场赔率（如果有）
    market_consensus: Optional[Dict] = None
    model_vs_market: Optional[Dict] = None
    
    # 综合调整后的概率
    adjusted_home_prob: float = 0.0
    adjusted_draw_prob: float = 0.0
    adjusted_away_prob: float = 0.0
    
    # 新增因子权重
    injury_weight: float = 0.06
    sentiment_weight: float = 0.04
    odds_calibration_weight: float = 0.03
    
    # 综合评分
    composite_score: float = 0.0
    data_quality_score: float = 0.0  # 数据完整性评分


class PredictionEngineV5(PredictionEngineV4):
    """
    预测引擎 V5
    
    新增特性：
    1. 球员伤病影响因子
    2. 社交媒体情感分析
    3. 市场赔率校准
    4. 数据质量评估
    """
    
    def __init__(self):
        super().__init__()
        
        # V5新增权重
        self.injury_weight = 0.06
        self.sentiment_weight = 0.04
        self.odds_calibration_weight = 0.03
        
        # 调整原有权重以适应新因子
        self._adjust_weights()
    
    def _adjust_weights(self):
        """调整权重配置以容纳新因子"""
        # V4权重总和为1，V5需要为新因子腾出空间
        reduction_factor = 1.0 - (self.injury_weight + self.sentiment_weight + self.odds_calibration_weight)
        
        # 按比例缩减V4权重
        for key in self.optimized_weights:
            self.optimized_weights[key] *= reduction_factor
    
    def predict_match_v5(
        self,
        home: Dict,
        away: Dict,
        stage: str = "GROUP",
        is_neutral: bool = True,
        group: Optional[str] = None,
        match_idx: Optional[int] = None,
        venue: Optional[str] = None
    ) -> MatchPredictionV5:
        """
        V5预测方法 - 整合所有数据因子
        """
        
        home_code = home.get("code", home.get("name", ""))
        away_code = away.get("code", away.get("name", ""))
        
        # 1. 基础预测（V4）
        base_prediction = self.predict_match(home, away, stage, is_neutral)
        
        # 2. 伤病影响
        home_injury_impact = get_injury_impact(home_code)
        away_injury_impact = get_injury_impact(away_code)
        injury_advantage = away_injury_impact - home_injury_impact
        
        # 3. 社交情感影响
        home_sentiment_impact = get_sentiment_impact(home_code)
        away_sentiment_impact = get_sentiment_impact(away_code)
        sentiment_advantage = home_sentiment_impact - away_sentiment_impact
        
        # 4. 市场赔率校准
        market_consensus = None
        model_vs_market = None
        odds_adjustment = 0.0
        
        if group and match_idx is not None:
            market_data = get_consensus_odds(group, match_idx)
            if market_data:
                market_consensus = market_data["consensus"]
                
                # 比较模型与市场
                model_probs = {
                    "home_win": base_prediction.home_win_prob,
                    "draw": base_prediction.draw_prob,
                    "away_win": base_prediction.away_win_prob,
                }
                model_vs_market = compare_model_vs_market(model_probs, market_consensus)
                
                # 计算赔率校准调整（向市场概率靠拢）
                if model_vs_market["agreement"]:
                    # 模型与市场一致，轻微调整
                    odds_adjustment = 0.01
                else:
                    # 存在分歧，使用折中方案
                    odds_adjustment = 0.03
        
        # 5. 综合调整概率
        adjusted_probs = self._adjust_probabilities(
            base_prediction.home_win_prob,
            base_prediction.draw_prob,
            base_prediction.away_win_prob,
            injury_advantage,
            sentiment_advantage,
            odds_adjustment,
            market_consensus
        )
        
        # 6. 计算数据质量评分
        data_quality = self._calculate_data_quality(
            home_code, away_code, group, match_idx, venue
        )
        
        # 7. 构建V5预测结果
        return MatchPredictionV5(
            # 继承V4所有字段
            home_code=base_prediction.home_code,
            home_name=base_prediction.home_name,
            home_name_cn=base_prediction.home_name_cn,
            away_code=base_prediction.away_code,
            away_name=base_prediction.away_name,
            away_name_cn=base_prediction.away_name_cn,
            
            # 原始贝叶斯概率
            home_win_prob=base_prediction.home_win_prob,
            draw_prob=base_prediction.draw_prob,
            away_win_prob=base_prediction.away_win_prob,
            
            # 置信区间
            home_win_interval=base_prediction.home_win_interval,
            draw_interval=base_prediction.draw_interval,
            away_win_interval=base_prediction.away_win_interval,
            
            # 原预测结果
            prediction=base_prediction.prediction,
            confidence_level=base_prediction.confidence_level,
            confidence_value=base_prediction.confidence_value,
            
            # 风险评估
            risk_level=base_prediction.risk_level,
            risk_description=base_prediction.risk_description,
            
            # 冷门分析
            upset_score=base_prediction.upset_score,
            is_upset_warning=base_prediction.is_upset_warning,
            upset_factors=base_prediction.upset_factors,
            upset_recommendation=base_prediction.upset_recommendation,
            
            # 权重
            weights_used=base_prediction.weights_used,
            
            # 预测ID
            prediction_id=base_prediction.prediction_id,
            
            # V5新增字段
            home_injury_impact=home_injury_impact,
            away_injury_impact=away_injury_impact,
            injury_advantage=injury_advantage,
            
            home_sentiment_impact=home_sentiment_impact,
            away_sentiment_impact=away_sentiment_impact,
            sentiment_advantage=sentiment_advantage,
            
            market_consensus=market_consensus,
            model_vs_market=model_vs_market,
            
            adjusted_home_prob=adjusted_probs["home_win"],
            adjusted_draw_prob=adjusted_probs["draw"],
            adjusted_away_prob=adjusted_probs["away_win"],
            
            injury_weight=self.injury_weight,
            sentiment_weight=self.sentiment_weight,
            odds_calibration_weight=self.odds_calibration_weight,
            
            composite_score=self._calculate_composite_score(
                injury_advantage, sentiment_advantage, odds_adjustment
            ),
            data_quality_score=data_quality,
        )
    
    def _adjust_probabilities(
        self,
        base_home: float,
        base_draw: float,
        base_away: float,
        injury_adv: float,
        sentiment_adv: float,
        odds_adj: float,
        market: Optional[Dict]
    ) -> Dict[str, float]:
        """
        综合调整概率
        """
        # 计算调整量
        injury_adjustment = injury_adv * self.injury_weight
        sentiment_adjustment = sentiment_adv * self.sentiment_weight
        
        # 总调整
        total_adjustment = injury_adjustment + sentiment_adjustment
        
        # 应用调整
        adjusted_home = base_home + total_adjustment
        adjusted_away = base_away - total_adjustment
        adjusted_draw = base_draw
        
        # 如果有市场赔率，进行校准
        if market and odds_adj > 0:
            # 向市场概率折中
            adjusted_home = adjusted_home * (1 - odds_adj) + market["home_win"] * odds_adj
            adjusted_away = adjusted_away * (1 - odds_adj) + market["away_win"] * odds_adj
            adjusted_draw = adjusted_draw * (1 - odds_adj) + market["draw"] * odds_adj
        
        # 归一化
        total = adjusted_home + adjusted_draw + adjusted_away
        if total > 0:
            adjusted_home /= total
            adjusted_draw /= total
            adjusted_away /= total
        
        return {
            "home_win": max(0.01, min(0.98, adjusted_home)),
            "draw": max(0.01, min(0.98, adjusted_draw)),
            "away_win": max(0.01, min(0.98, adjusted_away)),
        }
    
    def _calculate_data_quality(
        self,
        home_code: str,
        away_code: str,
        group: Optional[str],
        match_idx: Optional[int],
        venue: Optional[str]
    ) -> float:
        """
        计算数据质量评分
        0-1范围，1表示数据最完整
        """
        score = 0.0
        
        # 基础球队数据（权重0.4）
        if home_code and away_code:
            score += 0.4
        
        # 伤病数据（权重0.2）
        injury_data_home = get_injury_impact(home_code) != 0
        injury_data_away = get_injury_impact(away_code) != 0
        score += 0.2 * ((injury_data_home + injury_data_away) / 2)
        
        # 情感数据（权重0.15）
        sentiment_data_home = abs(get_sentiment_impact(home_code)) > 0.01
        sentiment_data_away = abs(get_sentiment_impact(away_code)) > 0.01
        score += 0.15 * ((sentiment_data_home + sentiment_data_away) / 2)
        
        # 赔率数据（权重0.15）
        if group and match_idx is not None:
            odds_data = get_consensus_odds(group, match_idx)
            if odds_data:
                score += 0.15
        
        # 场地数据（权重0.1）
        if venue:
            score += 0.1
        
        return min(1.0, score)
    
    def _calculate_composite_score(
        self,
        injury_adv: float,
        sentiment_adv: float,
        odds_adj: float
    ) -> float:
        """
        计算综合评分（主队优势程度）
        -1到1范围
        """
        score = (
            injury_adv * 0.4 +
            sentiment_adv * 0.35 +
            (1 if odds_adj > 0.02 else 0 if odds_adj < 0.02 else -1) * 0.25
        )
        
        return max(-1, min(1, score))
    
    def predict_match(
        self,
        home: Dict,
        away: Dict,
        stage: str = "GROUP",
        is_neutral: bool = True
    ) -> MatchPredictionV4:
        """重写V4方法以支持V5调用"""
        return super().predict_match(home, away, stage, is_neutral)


# 单例模式
_engine_v5_instance = None


def get_engine_v5() -> PredictionEngineV5:
    """获取V5引擎单例"""
    global _engine_v5_instance
    if _engine_v5_instance is None:
        _engine_v5_instance = PredictionEngineV5()
    return _engine_v5_instance
