"""
足球比赛预测 - 数据收集系统
第一阶段：接入免费数据源
"""
import requests
import json
import os
from datetime import datetime
import sqlite3

# =====================
# 1. 博彩赔率数据源
# =====================

class OddsAPI:
    """The Odds API - 免费500次/月"""
    
    BASE_URL = "https://api.the-odds-api.com/v4"
    
    def __init__(self, api_key=None):
        # 如果没有API密钥，使用免费额度
        self.api_key = api_key or os.getenv("ODDS_API_KEY", "demo")
        
    def get_football_odds(self):
        """获取足球赔率"""
        url = f"{self.BASE_URL}/sports/soccer/odds"
        params = {
            "apiKey": self.api_key,
            "regions": "us",  # 美国市场
            "markets": "h2h",  # 胜平负
            "dateFormat": "iso"
        }
        
        try:
            resp = requests.get(url, params=params, timeout=10)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"API错误: {resp.status_code}")
                return None
        except Exception as e:
            print(f"请求失败: {e}")
            return None
    
    def calculate_implied_probability(self, odds):
        """计算赔率隐含概率"""
        # 美式赔率转概率
        if odds > 0:
            return 100 / (odds + 100)
        else:
            return abs(odds) / (abs(odds) + 100)
    
    def parse_odds_data(self, raw_data):
        """解析赔率数据"""
        matches = []
        
        for event in raw_data:
            home_team = event.get("home_team")
            away_team = event.get("away_team")
            
            # 提取各博彩公司赔率
            bookmakers = event.get("bookmakers", [])
            
            for bm in bookmakers:
                markets = bm.get("markets", [])
                for market in markets:
                    if market.get("key") == "h2h":
                        outcomes = market.get("outcomes", [])
                        
                        odds_data = {}
                        for outcome in outcomes:
                            team = outcome.get("name")
                            price = outcome.get("price")
                            
                            if team == home_team:
                                odds_data['home'] = price
                            elif team == away_team:
                                odds_data['away'] = price
                            else:
                                odds_data['draw'] = price
                        
                        # 计算隐含概率
                        if odds_data.get('home') and odds_data.get('away'):
                            probs = {
                                'home_prob': self.calculate_implied_probability(odds_data['home']),
                                'draw_prob': self.calculate_implied_probability(odds_data.get('draw', 3.0)),
                                'away_prob': self.calculate_implied_probability(odds_data['away']),
                                'source': bm.get("title"),
                                'timestamp': event.get("commence_time")
                            }
                            
                            matches.append({
                                'home': home_team,
                                'away': away_team,
                                'odds': odds_data,
                                'probabilities': probs
                            })
        
        return matches


# =====================
# 2. 球员评分数据源
# =====================

class PlayerRatingAPI:
    """球员评分数据"""
    
    # FIFA官方评分数据（公开）
    FIFA_RATINGS = {
        # 示例数据 - 需要补充完整
        "ARG": {
            "avg_rating": 85.5,
            "star_players": 8,  # 评分>80的球员数
            "forward_rating": 88.0,  # Messi + others
            "midfield_rating": 84.0,
            "defense_rating": 82.0,
            "goalkeeper_rating": 83.0,
            "top_players": ["Messi(94)", "Di Maria(86)", "De Paul(82)"]
        },
        "BRA": {
            "avg_rating": 84.8,
            "star_players": 7,
            "forward_rating": 87.0,
            "midfield_rating": 83.5,
            "defense_rating": 81.5,
            "goalkeeper_rating": 82.0,
            "top_players": ["Neymar(89)", "Vinicius(88)", "Richarlison(84)"]
        },
        "FRA": {
            "avg_rating": 85.2,
            "star_players": 9,
            "forward_rating": 87.5,
            "midfield_rating": 85.0,
            "defense_rating": 84.0,
            "goalkeeper_rating": 86.0,
            "top_players": ["Mbappe(91)", "Griezmann(84)", "Benzema(87)"]
        },
        # ... 需要补充48支球队
    }
    
    def get_team_ratings(self, team_code):
        """获取球队评分"""
        return self.FIFA_RATINGS.get(team_code, {
            "avg_rating": 75.0,
            "star_players": 0,
            "forward_rating": 75.0,
            "midfield_rating": 75.0,
            "defense_rating": 75.0,
            "goalkeeper_rating": 75.0,
            "top_players": []
        })
    
    def calculate_strength_diff(self, home_code, away_code):
        """计算实力差距"""
        home = self.get_team_ratings(home_code)
        away = self.get_team_ratings(away_code)
        
        return {
            'avg_rating_diff': home['avg_rating'] - away['avg_rating'],
            'forward_diff': home['forward_rating'] - away['forward_rating'],
            'midfield_diff': home['midfield_rating'] - away['midfield_rating'],
            'defense_diff': home['defense_rating'] - away['defense_rating'],
            'goalkeeper_diff': home['goalkeeper_rating'] - away['goalkeeper_rating'],
            'star_players_diff': home['star_players'] - away['star_players']
        }


# =====================
# 3. xG数据源
# =====================

class XGDataAPI:
    """预期进球数据"""
    
    FBREF_URL = "https://fbref.com"
    
    def get_team_xg(self, team_code):
        """获取球队xG数据"""
        # 示例数据 - 需要从FBref抓取
        # 这里先用估算值
        return {
            'avg_xg': 1.5,  # 场均预期进球
            'avg_xga': 1.2,  # 场均失球xG
            'xg_diff': 0.3,
            'possession': 55.0,  # 控球率
            'shots_per_game': 12.0
        }
    
    def calculate_xg_diff(self, home_code, away_code):
        """计算xG差距"""
        home = self.get_team_xg(home_code)
        away = self.get_team_xg(away_code)
        
        return {
            'xg_diff': home['avg_xg'] - away['avg_xg'],
            'xga_diff': away['avg_xga'] - home['avg_xga'],
            'possession_diff': home['possession'] - away['possession']
        }


# =====================
# 4. 伤病数据
# =====================

class InjuryDataAPI:
    """伤病数据"""
    
    def get_injury_report(self, team_code):
        """获取伤病报告"""
        # 示例数据 - 需要从官方新闻抓取
        return {
            'injured_players': [],  # 伤停球员列表
            'injured_rating': 0,  # 伤停球员总评分
            'key_forward_injured': False,
            'key_goalkeeper_injured': False,
            'injury_index': 0  # 伤停影响指数
        }
    
    def calculate_injury_impact(self, team_code, player_ratings):
        """计算伤病影响"""
        injuries = self.get_injury_report(team_code)
        
        total_impact = 0
        for player in injuries['injured_players']:
            # 根据位置权重计算影响
            position_weight = {
                'forward': 0.30,
                'midfield': 0.25,
                'defense': 0.25,
                'goalkeeper': 0.20
            }
            
            rating = player_ratings.get(player['name'], 75)
            weight = position_weight.get(player['position'], 0.25)
            total_impact += rating * weight
        
        return {
            'injury_impact_score': total_impact,
            'injury_percentage': total_impact / 85.0  # 相对于满分85
        }


# =====================
# 5. 综合特征生成
# =====================

class FeatureGenerator:
    """特征生成器"""
    
    def __init__(self):
        self.odds_api = OddsAPI()
        self.player_api = PlayerRatingAPI()
        self.xg_api = XGDataAPI()
        self.injury_api = InjuryDataAPI()
    
    def generate_features(self, home_code, away_code):
        """生成完整特征集"""
        
        # 1. 球员实力特征
        strength = self.player_api.calculate_strength_diff(home_code, away_code)
        
        # 2. xG特征
        xg = self.xg_api.calculate_xg_diff(home_code, away_code)
        
        # 3. 伤病特征
        injury_home = self.injury_api.calculate_injury_impact(
            home_code, 
            self.player_api.get_team_ratings(home_code)
        )
        injury_away = self.injury_api.calculate_injury_impact(
            away_code,
            self.player_api.get_team_ratings(away_code)
        )
        
        # 4. 组合所有特征
        features = {
            # 球员实力
            'avg_rating_diff': strength['avg_rating_diff'],
            'forward_diff': strength['forward_diff'],
            'midfield_diff': strength['midfield_diff'],
            'defense_diff': strength['defense_diff'],
            'goalkeeper_diff': strength['goalkeeper_diff'],
            'star_players_diff': strength['star_players_diff'],
            
            # xG数据
            'xg_diff': xg['xg_diff'],
            'xga_diff': xg['xga_diff'],
            'possession_diff': xg['possession_diff'],
            
            # 伤病影响
            'injury_impact_home': injury_home['injury_impact_score'],
            'injury_impact_away': injury_away['injury_impact_score'],
            'injury_diff': injury_home['injury_percentage'] - injury_away['injury_percentage'],
            
            # 位置标记
            'key_forward_injured_home': injury_home.get('key_forward_injured', False),
            'key_goalkeeper_injured_home': injury_home.get('key_goalkeeper_injured', False),
            
            # 球队基础数据
            'home_code': home_code,
            'away_code': away_code
        }
        
        return features
    
    def generate_features_with_odds(self, home_code, away_code, odds_data=None):
        """生成带赔率的特征"""
        
        features = self.generate_features(home_code, away_code)
        
        # 如果有赔率数据，添加赔率特征
        if odds_data:
            features['odds_home_prob'] = odds_data['probabilities']['home_prob']
            features['odds_draw_prob'] = odds_data['probabilities']['draw_prob']
            features['odds_away_prob'] = odds_data['probabilities']['away_prob']
            features['odds_source'] = odds_data['probabilities']['source']
        
        return features


# =====================
# 6. 数据存储
# =====================

class DataStorage:
    """数据存储"""
    
    def __init__(self, db_path="/var/www/worldcup-predictor/backend/data/match_features.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """初始化数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS match_features (
                match_id TEXT PRIMARY KEY,
                home_code TEXT,
                away_code TEXT,
                timestamp TEXT,
                
                -- 球员实力特征
                avg_rating_diff REAL,
                forward_diff REAL,
                midfield_diff REAL,
                defense_diff REAL,
                goalkeeper_diff REAL,
                star_players_diff INTEGER,
                
                -- xG特征
                xg_diff REAL,
                xga_diff REAL,
                possession_diff REAL,
                
                -- 伤病特征
                injury_impact_home REAL,
                injury_impact_away REAL,
                injury_diff REAL,
                key_forward_injured_home INTEGER,
                key_goalkeeper_injured_home INTEGER,
                
                -- 赔率特征
                odds_home_prob REAL,
                odds_draw_prob REAL,
                odds_away_prob REAL,
                odds_source TEXT,
                
                -- 实际结果
                actual_result TEXT,
                is_correct INTEGER,
                
                created_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_features(self, match_id, features):
        """保存特征数据"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO match_features
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            match_id,
            features['home_code'],
            features['away_code'],
            datetime.now().isoformat(),
            
            features.get('avg_rating_diff', 0),
            features.get('forward_diff', 0),
            features.get('midfield_diff', 0),
            features.get('defense_diff', 0),
            features.get('goalkeeper_diff', 0),
            features.get('star_players_diff', 0),
            
            features.get('xg_diff', 0),
            features.get('xga_diff', 0),
            features.get('possession_diff', 0),
            
            features.get('injury_impact_home', 0),
            features.get('injury_impact_away', 0),
            features.get('injury_diff', 0),
            features.get('key_forward_injured_home', 0),
            features.get('key_goalkeeper_injured_home', 0),
            
            features.get('odds_home_prob', None),
            features.get('odds_draw_prob', None),
            features.get('odds_away_prob', None),
            features.get('odds_source', None),
            
            features.get('actual_result', None),
            features.get('is_correct', None),
            
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()


# =====================
# 测试代码
# =====================

if __name__ == "__main__":
    print("=" * 70)
    print("数据收集系统测试")
    print("=" * 70)
    
    # 测试特征生成
    generator = FeatureGenerator()
    features = generator.generate_features("ARG", "BRA")
    
    print("\n生成的特征（阿根廷 vs 巴西）：")
    for key, value in features.items():
        print(f"  {key}: {value}")
    
    # 测试数据存储
    storage = DataStorage()
    storage.save_features("ARG_BRA_TEST", features)
    
    print("\n✓ 特征已保存到数据库")
    print(f"数据库位置: {storage.db_path}")
    
    print("\n下一步：")
    print("  1. 补充完整的球员评分数据")
    print("  2. 接入真实的赔率API")
    print("  3. 抓取xG数据")
    print("  4. 整理伤病报告")