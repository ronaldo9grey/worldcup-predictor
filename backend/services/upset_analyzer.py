"""冷门分析引擎"""
from typing import List, Dict, Tuple
from datetime import datetime
import math


class UpsetAnalyzer:
    """冷门分析器 - 识别潜在爆冷比赛"""
    
    def __init__(self):
        # 冷门因子权重
        self.weights = {
            "rank_gap": 0.20,        # 排名差距
            "form_diff": 0.25,       # 状态差异
            "elo_diff": 0.15,        # Elo差异
            "home_advantage": 0.10,  # 主场优势
            "odds_value": 0.15,      # 赔率价值
            "tournament_stage": 0.15, # 赛事阶段
        }
    
    def analyze(self, match_data: dict) -> Tuple[float, List[str], bool]:
        """
        分析比赛冷门潜力
        
        返回:
            upset_score: 冷门指数 0-100
            upset_factors: 冷门因子列表
            is_potential_upset: 是否潜在冷门
        """
        factors = []
        scores = {}
        
        # 1. 排名差距因子
        rank_diff = match_data.get("away_team_rank", 100) - match_data.get("home_team_rank", 100)
        if match_data.get("is_neutral", True):
            # 中立场，排名低的球队有冷门潜力
            rank_score = max(0, -rank_diff) / 50 * 100  # 排名差距越大，冷门潜力越大
        else:
            rank_score = max(0, -rank_diff) / 50 * 100
        scores["rank_gap"] = min(100, rank_score)
        if rank_score > 30:
            factors.append(f"排名差距: {abs(rank_diff)}位")
        
        # 2. 近期状态因子
        home_form = match_data.get("home_recent_form", "")
        away_form = match_data.get("away_recent_form", "")
        form_diff = self._calculate_form_score(away_form) - self._calculate_form_score(home_form)
        scores["form_diff"] = min(100, max(0, form_diff * 10))
        if form_diff > 1.5:
            factors.append("客队近期状态更佳")
        elif form_diff > 0.5:
            factors.append("客队状态略优")
        
        # 3. Elo评分差异
        home_elo = match_data.get("home_elo", 1500)
        away_elo = match_data.get("away_elo", 1500)
        elo_diff = away_elo - home_elo
        # 强队（Elo高）对弱队时，弱队爆冷的可能性
        if elo_diff < 0:  # 主队是强队
            elo_score = abs(elo_diff) / 100 * 50
        else:  # 客队是强队
            elo_score = elo_diff / 100 * 30
        scores["elo_diff"] = min(100, max(0, elo_score))
        
        # 4. 主场优势（世界杯中立场影响小）
        is_neutral = match_data.get("is_neutral", True)
        home_country = match_data.get("home_team_country")
        host_country = match_data.get("host_country")
        
        if home_country and home_country == host_country:
            scores["home_advantage"] = 0  # 东道主主场优势，不利于冷门
            factors.append("东道主主场优势")
        elif is_neutral:
            scores["home_advantage"] = 30  # 中立场略有冷门倾向
        else:
            scores["home_advantage"] = 10
        
        # 5. 赔率价值（如果有赔率数据）
        home_odds = match_data.get("home_odds")
        away_odds = match_data.get("away_odds")
        
        if home_odds and away_odds:
            # 赔率偏离度：如果赔率给出的概率与模型差距大
            odds_value = self._calculate_odds_value(
                home_odds, away_odds,
                match_data.get("model_home_prob", 0.5),
                match_data.get("model_away_prob", 0.5)
            )
            scores["odds_value"] = min(100, abs(odds_value) * 200)
            if abs(odds_value) > 0.1:
                factors.append(f"赔率偏离: {abs(odds_value)*100:.1f}%")
        else:
            scores["odds_value"] = 20  # 默认中等
        
        # 6. 赛事阶段因子
        stage = match_data.get("stage", "GROUP")
        stage_scores = {
            "GROUP": 40,           # 小组赛冷门多
            "ROUND_OF_16": 35,     # 16强
            "QUARTER_FINAL": 25,   # 8强
            "SEMI_FINAL": 15,      # 4强
            "FINAL": 10,           # 决赛冷门少
        }
        scores["tournament_stage"] = stage_scores.get(stage, 30)
        
        # 特殊冷门信号
        self._check_special_signals(match_data, factors)
        
        # 计算加权总分
        total_score = sum(scores[k] * self.weights[k] for k in scores)
        
        # 判断是否潜在冷门
        is_upset = total_score >= 45
        
        if is_upset and not factors:
            factors.append("综合指标显示冷门潜力")
        
        return round(total_score, 1), factors, is_upset
    
    def _calculate_form_score(self, form: str) -> float:
        """计算近期状态得分 W=3, D=1, L=0"""
        if not form:
            return 1.5
        score = 0
        for char in form.upper()[:5]:  # 只看最近5场
            if char == 'W':
                score += 3
            elif char == 'D':
                score += 1
        return score / 5  # 归一化
    
    def _calculate_odds_value(self, home_odds: float, away_odds: float,
                               model_home: float, model_away: float) -> float:
        """计算赔率价值（模型概率 vs 赔率隐含概率）"""
        # 赔率隐含概率
        implied_home = 1 / home_odds if home_odds > 0 else 0.5
        implied_away = 1 / away_odds if away_odds > 0 else 0.5
        
        # 偏离度
        return model_away - implied_away
    
    def _check_special_signals(self, match_data: dict, factors: List[str]):
        """检查特殊冷门信号"""
        
        # 信号1: 强队轮换（小组赛末轮已出线）
        if match_data.get("home_team_qualified") or match_data.get("away_team_qualified"):
            factors.append("⚠️ 已出线球队可能轮换")
        
        # 信号2: 强队近期低迷
        strong_team_form = match_data.get("strong_team_form", "")
        if len(strong_team_form) >= 3 and strong_team_form[:3].count('L') >= 2:
            factors.append("⚠️ 强队近期连败")
        
        # 信号3: 弱队状态火热
        weak_team_form = match_data.get("weak_team_form", "")
        if len(weak_team_form) >= 5 and weak_team_form.count('W') >= 4:
            factors.append("🔥 弱队状态火热")
        
        # 信号4: 战术克制
        if match_data.get("tactical_counter"):
            factors.append("⚔️ 战术克制")


class PredictionEngine:
    """比赛预测引擎"""
    
    def __init__(self):
        self.upset_analyzer = UpsetAnalyzer()
        
        # 预测参数
        self.params = {
            "elo_weight": 0.35,
            "form_weight": 0.25,
            "h2h_weight": 0.15,
            "home_weight": 0.10,
            "stage_weight": 0.15,
        }
    
    def predict(self, match_data: dict) -> dict:
        """
        预测比赛结果
        
        返回:
            home_win_prob: 主胜概率
            draw_prob: 平局概率
            away_win_prob: 客胜概率
            prediction: 预测结果 (HOME_WIN/DRAW/AWAY_WIN)
            confidence: 信心等级
            upset_score: 冷门指数
            upset_factors: 冷门因子
            is_upset: 是否潜在冷门
        """
        # 基础概率计算
        base_probs = self._calculate_base_probabilities(match_data)
        
        # 冷门分析
        upset_score, upset_factors, is_upset = self.upset_analyzer.analyze(match_data)
        
        # 如果是冷门，调整概率
        if is_upset and upset_score > 50:
            # 增加弱队获胜概率
            adjustment = (upset_score - 50) / 200  # 最大调整0.25
            if base_probs["away_win_prob"] < base_probs["home_win_prob"]:
                base_probs["away_win_prob"] = min(0.5, base_probs["away_win_prob"] + adjustment)
                base_probs["home_win_prob"] = max(0.2, base_probs["home_win_prob"] - adjustment * 0.5)
            else:
                base_probs["home_win_prob"] = min(0.5, base_probs["home_win_prob"] + adjustment)
                base_probs["away_win_prob"] = max(0.2, base_probs["away_win_prob"] - adjustment * 0.5)
        
        # 归一化
        total = base_probs["home_win_prob"] + base_probs["draw_prob"] + base_probs["away_win_prob"]
        home_prob = base_probs["home_win_prob"] / total
        draw_prob = base_probs["draw_prob"] / total
        away_prob = base_probs["away_win_prob"] / total
        
        # 确定预测方向
        if home_prob > away_prob and home_prob > draw_prob:
            prediction = "HOME_WIN"
            confidence = self._get_confidence(home_prob)
        elif away_prob > home_prob and away_prob > draw_prob:
            prediction = "AWAY_WIN"
            confidence = self._get_confidence(away_prob)
        else:
            prediction = "DRAW"
            confidence = "LOW"
        
        # 冷门比赛，标注信心
        if is_upset:
            confidence = "MEDIUM" if confidence == "HIGH" else confidence
        
        return {
            "home_win_prob": round(home_prob, 3),
            "draw_prob": round(draw_prob, 3),
            "away_win_prob": round(away_prob, 3),
            "prediction": prediction,
            "confidence": confidence,
            "upset_score": upset_score,
            "upset_factors": upset_factors,
            "is_potential_upset": is_upset,
        }
    
    def _calculate_base_probabilities(self, match_data: dict) -> dict:
        """计算基础概率"""
        
        # Elo概率
        home_elo = match_data.get("home_elo", 1500)
        away_elo = match_data.get("away_elo", 1500)
        elo_probs = self._elo_probability(home_elo, away_elo)
        
        # 近期状态概率
        home_form = match_data.get("home_recent_form", "DDD")
        away_form = match_data.get("away_recent_form", "DDD")
        form_probs = self._form_probability(home_form, away_form)
        
        # 主场优势（中立场降低）
        is_neutral = match_data.get("is_neutral", True)
        home_bonus = 0.0 if is_neutral else 0.08
        
        # 赛事阶段调整
        stage = match_data.get("stage", "GROUP")
        stage_probs = self._stage_adjustment(stage)
        
        # 综合概率
        home_prob = (
            elo_probs["home"] * self.params["elo_weight"] +
            form_probs["home"] * self.params["form_weight"] +
            stage_probs.get("home_bias", 0.4) * self.params["stage_weight"] +
            home_bonus
        )
        
        away_prob = (
            elo_probs["away"] * self.params["elo_weight"] +
            form_probs["away"] * self.params["form_weight"] +
            stage_probs.get("away_bias", 0.3) * self.params["stage_weight"]
        )
        
        draw_prob = max(0.15, 1 - home_prob - away_prob)
        
        return {
            "home_win_prob": home_prob,
            "draw_prob": draw_prob,
            "away_win_prob": away_prob,
        }
    
    def _elo_probability(self, home_elo: float, away_elo: float) -> dict:
        """基于Elo的概率计算"""
        diff = home_elo - away_elo
        # 主队胜率 = 1 / (1 + 10^(-diff/400))
        home_win = 1 / (1 + 10 ** (-diff / 400))
        # 世界杯中立场，降低主场优势
        draw = 0.25 - abs(diff) / 2000  # 差距越大，平局概率越低
        draw = max(0.1, min(0.35, draw))
        away_win = 1 - home_win - draw
        
        return {"home": home_win, "draw": draw, "away": max(0.05, away_win)}
    
    def _form_probability(self, home_form: str, away_form: str) -> dict:
        """基于近期状态的概率"""
        home_score = self._form_score(home_form)
        away_score = self._form_score(away_form)
        
        diff = home_score - away_score
        
        home_bias = 0.4 + diff * 0.1
        away_bias = 0.3 - diff * 0.1
        draw_bias = 1 - home_bias - away_bias
        
        return {
            "home": max(0.2, min(0.6, home_bias)),
            "draw": max(0.15, min(0.35, draw_bias)),
            "away": max(0.15, min(0.5, away_bias))
        }
    
    def _form_score(self, form: str) -> float:
        """状态得分 -1到1"""
        if not form:
            return 0
        score = 0
        weights = [0.4, 0.25, 0.2, 0.1, 0.05]  # 最近比赛权重最高
        for i, char in enumerate(form.upper()[:5]):
            if i < len(weights):
                if char == 'W':
                    score += weights[i]
                elif char == 'L':
                    score -= weights[i]
        return score
    
    def _stage_adjustment(self, stage: str) -> dict:
        """赛事阶段调整"""
        adjustments = {
            "GROUP": {"home_bias": 0.4, "away_bias": 0.3, "draw_bias": 0.3},
            "ROUND_OF_16": {"home_bias": 0.42, "away_bias": 0.33, "draw_bias": 0.25},
            "QUARTER_FINAL": {"home_bias": 0.45, "away_bias": 0.3, "draw_bias": 0.25},
            "SEMI_FINAL": {"home_bias": 0.45, "away_bias": 0.35, "draw_bias": 0.2},
            "FINAL": {"home_bias": 0.45, "away_bias": 0.4, "draw_bias": 0.15},
            "THIRD_PLACE": {"home_bias": 0.4, "away_bias": 0.35, "draw_bias": 0.25},
        }
        return adjustments.get(stage, adjustments["GROUP"])
    
    def _get_confidence(self, prob: float) -> str:
        """获取信心等级"""
        if prob >= 0.55:
            return "HIGH"
        elif prob >= 0.40:
            return "MEDIUM"
        else:
            return "LOW"