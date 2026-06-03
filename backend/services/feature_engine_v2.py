"""
特征引擎 V2 - P0优化版
新增：
1. 补充 h2h（历史交锋）特征
2. 补充 venue_factor（场地影响）特征
3. 特征交互（elo×form、rank×stage）
"""
from typing import Dict, List, Optional
from dataclasses import dataclass
import math


@dataclass
class FeatureSet:
    """特征集合"""
    # 基础特征（11维）
    elo_diff: float = 0.0
    rank_diff: float = 0.0
    form_diff: float = 0.0
    stage_factor: float = 0.0
    home_advantage: float = 0.0
    continent_factor: float = 0.0
    h2h: float = 0.0  # 新增：历史交锋
    wc_experience: float = 0.0
    squad_strength: float = 0.0
    coach_rating: float = 0.0
    venue_factor: float = 0.0  # 新增：场地影响
    
    # 特征交互（新增）
    elo_form_combined: float = 0.0  # 实力×状态
    rank_stage_combined: float = 0.0  # 排名×阶段
    
    def to_vector(self) -> List[float]:
        """转换为特征向量"""
        return [
            self.elo_diff,
            self.rank_diff,
            self.form_diff,
            self.stage_factor,
            self.home_advantage,
            self.continent_factor,
            self.h2h,
            self.wc_experience,
            self.squad_strength,
            self.coach_rating,
            self.venue_factor,
            # 交互特征
            self.elo_form_combined,
            self.rank_stage_combined,
        ]
    
    def to_dict(self) -> Dict[str, float]:
        """转换为字典"""
        return {
            'elo_diff': self.elo_diff,
            'rank_diff': self.rank_diff,
            'form_diff': self.form_diff,
            'stage_factor': self.stage_factor,
            'home_advantage': self.home_advantage,
            'continent_factor': self.continent_factor,
            'h2h': self.h2h,
            'wc_experience': self.wc_experience,
            'squad_strength': self.squad_strength,
            'coach_rating': self.coach_rating,
            'venue_factor': self.venue_factor,
            'elo_form_combined': self.elo_form_combined,
            'rank_stage_combined': self.rank_stage_combined,
        }


class FeatureEngineV2:
    """
    特征引擎 V2
    
    P0优化：
    1. 补充 h2h 历史交锋特征
    2. 补充 venue_factor 场地影响特征
    3. 新增特征交互
    """
    
    def __init__(self, h2h_provider=None, venue_provider=None):
        self.h2h_provider = h2h_provider
        self.venue_provider = venue_provider
        
        # 特征名称（13维）
        self.feature_names = [
            'elo_diff', 'rank_diff', 'form_diff', 'stage_factor',
            'home_advantage', 'continent_factor', 'h2h', 'wc_experience',
            'squad_strength', 'coach_rating', 'venue_factor',
            'elo_form_combined', 'rank_stage_combined'
        ]
    
    def compute_features(
        self,
        home: Dict,
        away: Dict,
        stage: str = "GROUP",
        group: Optional[str] = None,
        h2h_data: Optional[Dict] = None,
        venue_data: Optional[Dict] = None
    ) -> FeatureSet:
        """
        计算完整特征集
        
        Args:
            home: 主队数据
            away: 客队数据
            stage: 比赛阶段
            group: 小组名称（用于场地查询）
            h2h_data: 历史交锋数据（可选）
            venue_data: 场地数据（可选）
        
        Returns:
            FeatureSet: 特征集合
        """
        features = FeatureSet()
        
        # 1. Elo差异（归一化到[-1, 1]）
        home_elo = home.get('elo', 1500)
        away_elo = away.get('elo', 1500)
        features.elo_diff = (home_elo - away_elo) / 300  # 300分差距=1
        
        # 2. 排名差异（归一化）
        home_rank = home.get('rank', 50)
        away_rank = away.get('rank', 50)
        features.rank_diff = (away_rank - home_rank) / 50  # 排名越靠前，值越大
        
        # 3. 近期状态差异
        home_form = self._parse_form(home.get('form', 'DDD'))
        away_form = self._parse_form(away.get('form', 'DDD'))
        features.form_diff = (home_form - away_form) / 5  # 归一化
        
        # 4. 阶段因子
        features.stage_factor = self._get_stage_factor(stage)
        
        # 5. 主场优势
        features.home_advantage = self._compute_home_advantage(home, away, group)
        
        # 6. 洲际因素
        features.continent_factor = self._compute_continent_factor(home, away)
        
        # 7. 历史交锋（P0新增）
        features.h2h = self._compute_h2h_factor(home, away, h2h_data)
        
        # 8. 世界杯经验
        home_exp = home.get('wc_titles', 0) + home.get('wc_participations', 5)
        away_exp = away.get('wc_titles', 0) + away.get('wc_participations', 5)
        features.wc_experience = (home_exp - away_exp) / 10
        
        # 9. 阵容实力
        home_squad = home.get('squad_rating', 75)
        away_squad = away.get('squad_rating', 75)
        features.squad_strength = (home_squad - away_squad) / 20
        
        # 10. 教练评级
        home_coach = home.get('coach_rating', 70)
        away_coach = away.get('coach_rating', 70)
        features.coach_rating = (home_coach - away_coach) / 20
        
        # 11. 场地影响（P0新增）
        features.venue_factor = self._compute_venue_factor(home, away, group, venue_data)
        
        # ========== 特征交互（P0新增）==========
        
        # 12. 实力×状态交互
        features.elo_form_combined = features.elo_diff * features.form_diff
        
        # 13. 排名×阶段交互
        features.rank_stage_combined = features.rank_diff * features.stage_factor
        
        return features
    
    def _parse_form(self, form: str) -> float:
        """解析近期状态得分"""
        score = 0
        weights = [0.4, 0.25, 0.2, 0.1, 0.05]  # 最近比赛权重最高
        
        for i, char in enumerate(form.upper()[:5]):
            if i < len(weights):
                if char == 'W':
                    score += weights[i] * 3
                elif char == 'D':
                    score += weights[i] * 1
                # L = 0分
        
        return score
    
    def _get_stage_factor(self, stage: str) -> float:
        """获取阶段因子"""
        stage_map = {
            'GROUP': 0.0,
            'R16': 0.2,
            'ROUND_OF_16': 0.2,
            'QF': 0.4,
            'QUARTER_FINAL': 0.4,
            'SF': 0.6,
            'SEMI_FINAL': 0.6,
            'FI': 0.8,
            'FINAL': 0.8,
            'THIRD_PLACE': 0.3,
        }
        return stage_map.get(stage.upper(), 0.0)
    
    def _compute_home_advantage(self, home: Dict, away: Dict, group: Optional[str]) -> float:
        """计算主场优势"""
        # 东道主国家
        host_countries = ['USA', 'CAN', 'MEX']
        home_country = home.get('country', home.get('code', '')[:3])
        
        # 如果是东道主球队
        if home_country in host_countries or home.get('code') in ['USA', 'MEX', 'CAN']:
            return 0.15
        
        # 中立场无主场优势
        return 0.0
    
    def _compute_continent_factor(self, home: Dict, away: Dict) -> float:
        """计算洲际因素"""
        home_continent = home.get('continent', '')
        away_continent = away.get('continent', '')
        
        # 欧洲球队对其他洲有优势
        if home_continent == 'EU' and away_continent != 'EU':
            return 0.1
        elif away_continent == 'EU' and home_continent != 'EU':
            return -0.1
        
        # 南美球队对亚洲、非洲有优势
        if home_continent == 'SA' and away_continent in ['AS', 'AF']:
            return 0.08
        elif away_continent == 'SA' and home_continent in ['AS', 'AF']:
            return -0.08
        
        return 0.0
    
    def _compute_h2h_factor(
        self,
        home: Dict,
        away: Dict,
        h2h_data: Optional[Dict] = None
    ) -> float:
        """
        计算历史交锋因子（P0新增）
        
        数据来源优先级：
        1. 传入的 h2h_data（从数据库查询）
        2. 内置的经典对决数据
        """
        home_code = home.get('code', '')
        away_code = away.get('code', '')
        
        # 如果有传入数据
        if h2h_data:
            return h2h_data.get('h2h_factor', 0.0)
        
        # 内置经典对决数据（关键比赛）
        classic_matchups = {
            # 阿根廷 vs 巴西（南美德比）
            ('ARG', 'BRA'): 0.05,  # 阿根廷略占优
            ('BRA', 'ARG'): -0.05,
            
            # 德国 vs 英格兰（英德大战）
            ('GER', 'ENG'): 0.10,  # 德国占优
            ('ENG', 'GER'): -0.10,
            
            # 法国 vs 德国（欧陆对决）
            ('FRA', 'GER'): 0.05,
            ('GER', 'FRA'): -0.05,
            
            # 阿根廷 vs 法国
            ('ARG', 'FRA'): -0.08,  # 法国近年占优
            ('FRA', 'ARG'): 0.08,
            
            # 巴西 vs 德国
            ('BRA', 'GER'): -0.15,  # 德国占优（7-1阴影）
            ('GER', 'BRA'): 0.15,
            
            # 西班牙 vs 葡萄牙（伊比利亚德比）
            ('ESP', 'POR'): 0.05,
            ('POR', 'ESP'): -0.05,
            
            # 日本 vs 韩国（亚洲德比）
            ('JPN', 'KOR'): -0.05,
            ('KOR', 'JPN'): 0.05,
            
            # 墨西哥 vs 美国（北美德比）
            ('MEX', 'USA'): 0.08,
            ('USA', 'MEX'): -0.08,
        }
        
        key = (home_code, away_code)
        return classic_matchups.get(key, 0.0)
    
    def _compute_venue_factor(
        self,
        home: Dict,
        away: Dict,
        group: Optional[str],
        venue_data: Optional[Dict] = None
    ) -> float:
        """
        计算场地影响因子（P0新增）
        
        考虑因素：
        1. 高原影响（墨西哥城海拔2240米）
        2. 气候适应（高温、高湿）
        3. 东道主场地熟悉度
        """
        if not venue_data and not group:
            return 0.0
        
        # 如果有传入场地数据
        if venue_data:
            altitude = venue_data.get('altitude', 100)
            temp = venue_data.get('avg_temp_june', 25)
            humidity = venue_data.get('avg_humidity', 60)
        else:
            # 根据小组获取默认场地
            group_venues = {
                'A': {'altitude': 2240, 'avg_temp_june': 20, 'avg_humidity': 50},  # 墨西哥城
                'B': {'altitude': 150, 'avg_temp_june': 30, 'avg_humidity': 60},   # 达拉斯
                'C': {'altitude': 90, 'avg_temp_june': 22, 'avg_humidity': 50},    # 洛杉矶
                'D': {'altitude': 10, 'avg_temp_june': 24, 'avg_humidity': 70},   # 纽约
            }
            default_venue = {'altitude': 100, 'avg_temp_june': 25, 'avg_humidity': 60}
            venue = group_venues.get(group, default_venue)
            altitude = venue['altitude']
            temp = venue['avg_temp_june']
            humidity = venue['avg_humidity']
        
        factor = 0.0
        
        home_code = home.get('code', '')
        away_code = away.get('code', '')
        
        # 高原影响（墨西哥主场）
        if altitude > 1500:
            # 墨西哥球队适应高原
            if home_code == 'MEX':
                factor += 0.12
            elif away_code == 'MEX':
                factor -= 0.12
            else:
                # 非高原球队，体能消耗大
                factor += 0.05 if home_code in ['COL', 'ECU', 'VEN'] else 0.0
        
        # 气候影响
        if temp > 30:
            # 高温：欧洲、南美南部球队不适应
            home_continent = home.get('continent', '')
            away_continent = away.get('continent', '')
            
            if home_continent == 'EU':
                factor -= 0.03
            if away_continent == 'EU':
                factor += 0.03
        
        if humidity > 70:
            # 高湿：欧洲球队不适应
            home_continent = home.get('continent', '')
            if home_continent == 'EU':
                factor -= 0.02
        
        return max(-0.15, min(0.15, factor))  # 限制在[-0.15, 0.15]
    
    def get_feature_importance(self) -> Dict[str, float]:
        """获取特征重要性说明"""
        return {
            'elo_diff': 0.28,
            'form_diff': 0.18,
            'rank_diff': 0.10,
            'stage_factor': 0.12,
            'home_advantage': 0.08,
            'continent_factor': 0.05,
            'h2h': 0.07,  # P0新增
            'wc_experience': 0.05,
            'squad_strength': 0.03,
            'coach_rating': 0.02,
            'venue_factor': 0.05,  # P0新增
            'elo_form_combined': 0.15,  # P0新增交互
            'rank_stage_combined': 0.08,  # P0新增交互
        }


# 单例
_feature_engine_v2_instance = None


def get_feature_engine_v2() -> FeatureEngineV2:
    """获取特征引擎V2实例"""
    global _feature_engine_v2_instance
    if _feature_engine_v2_instance is None:
        _feature_engine_v2_instance = FeatureEngineV2()
    return _feature_engine_v2_instance
