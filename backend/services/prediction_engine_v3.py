"""
预测引擎 V3 - 模块化、可扩展版本

核心设计：
1. 依赖注入 - 所有数据源通过构造函数注入
2. 可配置权重 - 支持不同阶段的自适应权重
3. 可测试 - 数据源可替换为 Mock
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Tuple


@dataclass
class FactorContribution:
    """预测因子贡献"""
    key: str
    name: str
    icon: str
    color: str
    desc: str
    weight: float
    raw_value: float
    contribution: float
    source: str = "engine"  # 标记数据来源


@dataclass
class MatchPrediction:
    """比赛预测结果"""
    # 基本信息
    home_code: str
    home_name: str
    home_name_cn: str
    away_code: str
    away_name: str
    away_name_cn: str
    
    # 预测概率
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    
    # 预测结果
    prediction: str  # HOME_WIN / DRAW / AWAY_WIN
    confidence: str  # HIGH / MEDIUM / LOW
    
    # 因子分解
    factors: List[FactorContribution] = field(default_factory=list)
    
    # 冷门分析
    upset_score: float = 0.0
    is_upset: bool = False
    upset_factors: List[str] = field(default_factory=list)
    
    # 比赛信息
    stage: str = "GROUP"
    group: str = ""


class PredictionEngineV3:
    """
    预测引擎 V3
    
    特点：
    - 模块化设计，数据源可插拔
    - 支持多种数据提供者
    - 缓存友好
    """
    
    # 基础因子权重（可被自适应权重覆盖）
    BASE_WEIGHTS = {
        "elo_diff": 0.25,
        "rank_gap": 0.08,
        "form_diff": 0.20,
        "home_advantage": 0.10,
        "stage_factor": 0.12,
        "continent_factor": 0.05,
        # 新增因子
        "h2h": 0.08,
        "team_value": 0.07,
        "wc_experience": 0.05,
    }
    
    # 阶段自适应权重
    STAGE_WEIGHTS = {
        "GROUP": {"form_diff": 0.22, "stage_factor": 0.15},  # 小组赛状态更重要
        "R16": {"elo_diff": 0.28, "wc_experience": 0.08},   # 淘汰赛实力更重要
        "QF": {"elo_diff": 0.30, "wc_experience": 0.10},
        "SF": {"elo_diff": 0.32, "wc_experience": 0.12},
        "FI": {"elo_diff": 0.35, "wc_experience": 0.15, "stage_factor": 0.08},
    }
    
    def __init__(self, database=None, cache=None, 
                 h2h_provider=None, value_provider=None, 
                 wc_history_provider=None, form_provider=None):
        """
        初始化预测引擎（依赖注入）
        
        Args:
            database: 数据库实例
            cache: 缓存实例
            h2h_provider: 历史交锋数据提供者
            value_provider: 球队身价数据提供者
            wc_history_provider: 世界杯历史数据提供者
            form_provider: 球队状态数据提供者
        """
        self.db = database
        self.cache = cache
        self.h2h_provider = h2h_provider
        self.value_provider = value_provider
        self.wc_history_provider = wc_history_provider
        self.form_provider = form_provider
    
    def predict_match(self, home: Dict, away: Dict,
                      stage: str = "GROUP",
                      is_neutral: bool = True,
                      host_countries: List[str] = None) -> MatchPrediction:
        """
        预测单场比赛
        
        Args:
            home: 主队信息字典
            away: 客队信息字典
            stage: 比赛阶段
            is_neutral: 是否中立场
            host_countries: 东道主国家代码列表
        
        Returns:
            MatchPrediction 预测结果
        """
        # 获取当前阶段权重
        weights = self._get_stage_weights(stage)
        
        # 收集所有因子
        factors = []
        
        # 1. Elo实力差
        factors.append(self._calc_elo_factor(home, away, weights))
        
        # 2. 排名差距
        factors.append(self._calc_rank_factor(home, away, weights))
        
        # 3. 状态差异
        factors.append(self._calc_form_factor(home, away, weights))
        
        # 4. 主场优势
        factors.append(self._calc_home_factor(home, is_neutral, host_countries, weights))
        
        # 5. 赛事阶段
        factors.append(self._calc_stage_factor(stage, weights))
        
        # 6. 洲际因素
        factors.append(self._calc_continent_factor(home, away, host_countries, weights))
        
        # === 新增因子 ===
        
        # 7. 历史交锋
        h2h_factor = self._calc_h2h_factor(home, away, weights)
        if h2h_factor:
            factors.append(h2h_factor)
        
        # 8. 球队身价
        value_factor = self._calc_value_factor(home, away, weights)
        if value_factor:
            factors.append(value_factor)
        
        # 9. 世界杯经验
        exp_factor = self._calc_experience_factor(home, away, weights)
        if exp_factor:
            factors.append(exp_factor)
        
        # 计算综合概率
        home_prob, draw_prob, away_prob = self._calculate_probabilities(factors)
        
        # 判断预测方向
        prediction = self._determine_prediction(home_prob, draw_prob, away_prob)
        
        # 判断信心等级
        confidence = self._determine_confidence(home_prob, draw_prob, away_prob)
        
        # 冷门分析
        upset_score, is_upset, upset_factors = self._analyze_upset(
            home, away, home_prob, away_prob, stage, factors
        )
        
        return MatchPrediction(
            home_code=home.get("code", ""),
            home_name=home.get("name", ""),
            home_name_cn=home.get("name_cn", ""),
            away_code=away.get("code", ""),
            away_name=away.get("name", ""),
            away_name_cn=away.get("name_cn", ""),
            home_win_prob=round(home_prob, 3),
            draw_prob=round(draw_prob, 3),
            away_win_prob=round(away_prob, 3),
            prediction=prediction,
            confidence=confidence,
            factors=factors,
            upset_score=upset_score,
            is_upset=is_upset,
            upset_factors=upset_factors,
            stage=stage,
            group=home.get("group", "")
        )
    
    def _get_stage_weights(self, stage: str) -> Dict[str, float]:
        """获取当前阶段的权重配置"""
        weights = self.BASE_WEIGHTS.copy()
        
        # 应用阶段自适应调整
        stage_overrides = self.STAGE_WEIGHTS.get(stage, {})
        weights.update(stage_overrides)
        
        # 归一化权重
        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()}
    
    # ========== 因子计算方法 ==========
    
    def _calc_elo_factor(self, home: Dict, away: Dict, weights: Dict) -> FactorContribution:
        """Elo实力差因子"""
        elo_diff = home.get("elo", 1500) - away.get("elo", 1500)
        contribution = min(1, max(-1, elo_diff / 300))
        
        return FactorContribution(
            key="elo_diff",
            name="Elo实力差",
            icon="📊",
            color="#4A90D9",
            desc=f"Elo差{abs(elo_diff):.0f}分，{'主队' if elo_diff > 0 else '客队'}更强",
            weight=weights.get("elo_diff", 0.25),
            raw_value=elo_diff,
            contribution=contribution,
            source="elo"
        )
    
    def _calc_rank_factor(self, home: Dict, away: Dict, weights: Dict) -> FactorContribution:
        """FIFA排名差距因子"""
        rank_gap = away.get("rank", 50) - home.get("rank", 50)
        contribution = min(1, max(-1, rank_gap / 40))
        
        return FactorContribution(
            key="rank_gap",
            name="排名差距",
            icon="🏅",
            color="#F5A623",
            desc=f"FIFA排名差{abs(rank_gap)}位",
            weight=weights.get("rank_gap", 0.08),
            raw_value=rank_gap,
            contribution=contribution,
            source="fifa_rank"
        )
    
    def _calc_form_factor(self, home: Dict, away: Dict, weights: Dict) -> FactorContribution:
        """状态差异因子"""
        home_form = home.get("form", "WDWDW")
        away_form = away.get("form", "WDWDW")
        
        # 使用 FormProvider 计算状态分数（如果有）
        if self.form_provider:
            home_score = self.form_provider._calculate_form_score(home_form)
            away_score = self.form_provider._calculate_form_score(away_form)
        else:
            # 简单计算
            home_score = sum(3 if c == 'W' else 1 if c == 'D' else 0 for c in home_form[:5]) / 15
            away_score = sum(3 if c == 'W' else 1 if c == 'D' else 0 for c in away_form[:5]) / 15
        
        form_diff = (home_score - away_score) / 100
        contribution = min(1, max(-1, form_diff * 2))
        
        return FactorContribution(
            key="form_diff",
            name="状态差异",
            icon="📈",
            color="#7ED321",
            desc=f"近5场：{home_form} vs {away_form}",
            weight=weights.get("form_diff", 0.20),
            raw_value=form_diff,
            contribution=contribution,
            source="form"
        )
    
    def _calc_home_factor(self, home: Dict, is_neutral: bool, 
                          host_countries: List[str], weights: Dict) -> FactorContribution:
        """主场优势因子"""
        home_code = home.get("code", "")
        
        if host_countries and home_code in host_countries:
            advantage = 0.6
            desc = f"{home.get('name_cn', '')}是东道主，显著主场优势"
        elif not is_neutral:
            advantage = 0.3
            desc = "主场比赛，有一定优势"
        else:
            advantage = 0.0
            desc = "中立场，无主场优势"
        
        return FactorContribution(
            key="home_advantage",
            name="主场/中立场",
            icon="🏟️",
            color="#9B59B6",
            desc=desc,
            weight=weights.get("home_advantage", 0.10),
            raw_value=advantage,
            contribution=advantage,
            source="match_info"
        )
    
    def _calc_stage_factor(self, stage: str, weights: Dict) -> FactorContribution:
        """赛事阶段因子"""
        stage_bias = {
            "GROUP": 0.0, "R32": 0.05, "R16": 0.08,
            "QF": 0.12, "SF": 0.15, "FI": 0.18, "3RD": -0.05
        }
        stage_desc = {
            "GROUP": "小组赛冷门频发", "R32": "32强赛开始淘汰",
            "R16": "16强赛强队渐稳", "QF": "8强赛强队主导",
            "SF": "4强赛实力说话", "FI": "决赛容错率最低",
            "3RD": "季军赛战意成疑"
        }
        
        stage_val = stage_bias.get(stage, 0.0)
        
        return FactorContribution(
            key="stage_factor",
            name="赛事阶段",
            icon="🏆",
            color="#E74C3C",
            desc=stage_desc.get(stage, ""),
            weight=weights.get("stage_factor", 0.12),
            raw_value=stage_val,
            contribution=stage_val,
            source="match_info"
        )
    
    def _calc_continent_factor(self, home: Dict, away: Dict,
                                host_countries: List[str], weights: Dict) -> FactorContribution:
        """洲际因素因子"""
        home_continent = home.get("continent", "EU")
        away_continent = away.get("continent", "EU")
        
        # 在美洲举办的世界杯
        if host_countries:
            americas = {"NA", "SA"}
            if home_continent in americas and away_continent not in americas:
                cont_adv = 0.2
            elif away_continent in americas and home_continent not in americas:
                cont_adv = -0.2
            else:
                cont_adv = 0.0
        else:
            cont_adv = 0.0
        
        return FactorContribution(
            key="continent_factor",
            name="洲际因素",
            icon="🌍",
            color="#1ABC9C",
            desc=f"{home_continent} vs {away_continent}" + 
                 ("，美洲球队适应性好" if cont_adv != 0 else "，同洲作战"),
            weight=weights.get("continent_factor", 0.05),
            raw_value=cont_adv,
            contribution=cont_adv,
            source="geography"
        )
    
    def _calc_h2h_factor(self, home: Dict, away: Dict, weights: Dict) -> Optional[FactorContribution]:
        """历史交锋因子（新增）"""
        if not self.h2h_provider:
            return None
        
        try:
            h2h_data = self.h2h_provider.get_match_data(
                home.get("code", ""),
                away.get("code", "")
            )
            
            if not h2h_data or h2h_data.get("total_matches", 0) == 0:
                return None
            
            h2h_factor = h2h_data.get("h2h_factor", 0)
            
            return FactorContribution(
                key="h2h",
                name="历史交锋",
                icon="⚔️",
                color="#8E44AD",
                desc=f"历史{h2h_data['total_matches']}战：主队{h2h_data['home_wins']}胜{h2h_data['draws']}平{h2h_data['away_wins']}负",
                weight=weights.get("h2h", 0.08),
                raw_value=h2h_factor,
                contribution=h2h_factor * 0.5,  # 缩放到合理范围
                source="h2h_provider"
            )
        except Exception:
            return None
    
    def _calc_value_factor(self, home: Dict, away: Dict, weights: Dict) -> Optional[FactorContribution]:
        """球队身价因子（新增）"""
        if not self.value_provider:
            return None
        
        try:
            value_data = self.value_provider.get_match_data(
                home.get("code", ""),
                away.get("code", "")
            )
            
            if not value_data:
                return None
            
            value_factor = value_data.get("value_factor", 0)
            
            return FactorContribution(
                key="team_value",
                name="球队身价",
                icon="💰",
                color="#F39C12",
                desc=f"身价对比：{value_data['home_value']}M vs {value_data['away_value']}M欧元",
                weight=weights.get("team_value", 0.07),
                raw_value=value_factor,
                contribution=value_factor * 0.8,
                source="value_provider"
            )
        except Exception:
            return None
    
    def _calc_experience_factor(self, home: Dict, away: Dict, weights: Dict) -> Optional[FactorContribution]:
        """世界杯经验因子（新增）"""
        if not self.wc_history_provider:
            return None
        
        try:
            exp_data = self.wc_history_provider.get_match_data(
                home.get("code", ""),
                away.get("code", "")
            )
            
            if not exp_data:
                return None
            
            exp_factor = exp_data.get("experience_factor", 0)
            
            return FactorContribution(
                key="wc_experience",
                name="世界杯经验",
                icon="🏆",
                color="#27AE60",
                desc=f"底蕴对比：{exp_data['home_pedigree']} vs {exp_data['away_pedigree']}",
                weight=weights.get("wc_experience", 0.05),
                raw_value=exp_factor,
                contribution=exp_factor * 0.6,
                source="wc_history_provider"
            )
        except Exception:
            return None
    
    # ========== 概率计算 ==========
    
    def _calculate_probabilities(self, factors: List[FactorContribution]) -> Tuple[float, float, float]:
        """计算胜平负概率"""
        total_contribution = sum(f.contribution * f.weight for f in factors)
        
        # 基础概率
        home_prob = 0.4 + total_contribution * 0.35
        draw_prob = max(0.1, 0.28 - abs(total_contribution) * 0.2)
        away_prob = 1 - home_prob - draw_prob
        
        # 约束
        home_prob = max(0.05, min(0.85, home_prob))
        away_prob = max(0.05, min(0.85, away_prob))
        draw_prob = max(0.08, 1 - home_prob - away_prob)
        
        # 归一化
        total = home_prob + draw_prob + away_prob
        return home_prob / total, draw_prob / total, away_prob / total
    
    def _determine_prediction(self, home: float, draw: float, away: float) -> str:
        """判断预测方向"""
        if home > away and home > draw:
            return "HOME_WIN"
        elif away > home and away > draw:
            return "AWAY_WIN"
        else:
            return "DRAW"
    
    def _determine_confidence(self, home: float, draw: float, away: float) -> str:
        """判断信心等级"""
        max_prob = max(home, draw, away)
        if max_prob >= 0.50:
            return "HIGH"
        elif max_prob >= 0.38:
            return "MEDIUM"
        else:
            return "LOW"
    
    # ========== 冷门分析 ==========
    
    def _analyze_upset(self, home: Dict, away: Dict,
                       home_prob: float, away_prob: float,
                       stage: str, factors: List[FactorContribution]) -> Tuple[float, bool, List[str]]:
        """冷门分析"""
        score = 0
        upset_factors = []
        
        # 排名差距大但强队概率不高
        rank_gap = abs(home.get("rank", 50) - away.get("rank", 50))
        if rank_gap >= 20 and home_prob < 0.55:
            score += min(rank_gap / 2, 20)
            upset_factors.append(f"排名差{rank_gap}位")
        
        # 弱队状态火热
        if self.form_provider:
            home_form_data = self.form_provider.get_team_data(home.get("code", ""), home.get("form"))
            away_form_data = self.form_provider.get_team_data(away.get("code", ""), away.get("form"))
            
            if home_form_data and away_form_data:
                # 弱队状态更好
                weak_team = home if home.get("rank", 50) > away.get("rank", 50) else away
                weak_form_score = home_form_data["form_score"] if weak_team == home else away_form_data["form_score"]
                strong_form_score = away_form_data["form_score"] if weak_team == home else home_form_data["form_score"]
                
                if weak_form_score > strong_form_score + 10:
                    score += 15
                    upset_factors.append("弱队状态火热")
                elif strong_form_score < 40:
                    score += 10
                    upset_factors.append("强队近期低迷")
        
        # 小组赛冷门高发
        if stage == "GROUP":
            score += 5
        
        # 实力接近
        if rank_gap < 10:
            score += 10
            if "实力接近" not in upset_factors:
                upset_factors.append("实力接近")
        
        is_upset = score >= 40
        
        return round(score, 1), is_upset, upset_factors


# 工厂函数 - 便于创建引擎实例
def create_prediction_engine(database=None, cache=None, 
                             providers: Dict[str, Any] = None) -> PredictionEngineV3:
    """
    创建预测引擎实例
    
    Args:
        database: 数据库实例
        cache: 缓存实例
        providers: 数据提供者字典
    
    Returns:
        PredictionEngineV3 实例
    """
    providers = providers or {}
    
    return PredictionEngineV3(
        database=database,
        cache=cache,
        h2h_provider=providers.get("h2h"),
        value_provider=providers.get("value"),
        wc_history_provider=providers.get("wc_history"),
        form_provider=providers.get("form")
    )
