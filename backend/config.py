"""世界杯预测系统配置"""
import os
from pathlib import Path

# 项目路径
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# 数据库
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite+aiosqlite:///{DATA_DIR}/worldcup.db")

# 足球数据API (football-data.org - 免费版每月10次更新)
FOOTBALL_DATA_API_KEY = os.getenv("FOOTBALL_DATA_API_KEY", "")
FOOTBALL_DATA_BASE_URL = "https://api.football-data.org/v4"

# API-Football (api-football.com - 免费版每天100次)
API_FOOTBALL_KEY = os.getenv("API_FOOTBALL_KEY", "")
API_FOOTBALL_BASE_URL = "https://api-football-v2.p.rapidapi.com"

# FIFA排名数据源
FIFA_RANKING_URL = "https://www.fifa.com/fifa-world-ranking/men?dateId=ranking_202404"

# 比赛预测配置
PREDICTION_CONFIG = {
    # Elo评分权重
    "elo_weight": 0.35,
    # 近期状态权重
    "form_weight": 0.25,
    # 历史交锋权重
    "h2h_weight": 0.15,
    # 主场优势权重
    "home_advantage_weight": 0.15,
    # 赔率偏离权重
    "odds_deviation_weight": 0.10,
}

# 冷门因子配置
UPSET_CONFIG = {
    # 冷门阈值：弱队获胜概率超过此值视为冷门
    "upset_threshold": 0.25,
    # 强队状态低迷阈值
    "strong_team_slump_threshold": 0.4,
    # 赔率偏离阈值
    "odds_deviation_threshold": 0.15,
}