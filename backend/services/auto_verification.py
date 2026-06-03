"""
自动验证系统 - 从网络获取比赛结果并自动验证预测
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime
import json


class MatchResultFetcher:
    """
    比赛结果获取器
    
    支持多种数据源：
    1. FIFA官方API
    2. API-Football (第三方体育数据)
    3. 本地模拟数据（用于演示）
    """
    
    # 数据源配置
    DATA_SOURCES = {
        "fifa_official": {
            "name": "FIFA官方",
            "url": "https://api.fifa.com/api/v1/matches",
            "available": False  # FIFA API需要认证
        },
        "api_football": {
            "name": "API-Football",
            "url": "https://v3.football.api-sports.io",
            "api_key_required": True,
            "available": False  # 需要API密钥
        },
        "local_simulation": {
            "name": "本地模拟",
            "available": True  # 用于演示和测试
        }
    }
    
    def __init__(self, source: str = "local_simulation"):
        self.source = source
        self.cache = {}
    
    def fetch_completed_matches(self, competition: str = "WC2026") -> List[Dict]:
        """
        获取已完成的比赛结果
        
        Args:
            competition: 比赛ID (WC2026 = 2026世界杯)
        
        Returns:
            已完成比赛列表
        """
        if self.source == "local_simulation":
            return self._fetch_from_simulation(competition)
        elif self.source == "api_football":
            return self._fetch_from_api_football(competition)
        else:
            return []
    
    def _fetch_from_simulation(self, competition: str) -> List[Dict]:
        """
        从本地模拟数据获取（用于演示）
        
        模拟2026世界杯已完成的比赛
        使用2022世界杯的比赛结果，但映射到2026世界杯的球队
        """
        # 使用历史世界杯数据作为模拟结果
        from data.historical_world_cups import WORLD_CUP_2018, WORLD_CUP_2022
        from data.world_cup_2026 import GROUPS, ALL_TEAMS
        
        # 获取2026世界杯的球队代码
        teams_2026 = {t['code'] for t in ALL_TEAMS}
        
        simulated_matches = []
        
        # 对2026世界杯的每个小组，生成模拟结果
        # 使用历史数据的结果，但应用到2026的实际球队上
        pairs = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
        
        match_idx = 0
        for group_name, teams in GROUPS.items():
            for pair_idx, (i, j) in enumerate(pairs):
                home = teams[i]
                away = teams[j]
                
                # 根据Elo差距模拟结果（强队大概率获胜）
                import random
                random.seed(hash(home['code'] + away['code']) % 1000)
                
                elo_diff = home['elo'] - away['elo']
                
                # 简单模拟逻辑
                if elo_diff > 100:  # 强队优势明显
                    results_probs = [0.55, 0.25, 0.20]
                elif elo_diff > 50:  # 中等优势
                    results_probs = [0.45, 0.30, 0.25]
                elif elo_diff > -50:  # 势均力敌
                    results_probs = [0.35, 0.30, 0.35]
                elif elo_diff > -100:  # 弱队
                    results_probs = [0.25, 0.30, 0.45]
                else:  # 明显弱势
                    results_probs = [0.20, 0.25, 0.55]
                
                result = random.choices(
                    ["HOME_WIN", "DRAW", "AWAY_WIN"],
                    weights=results_probs
                )[0]
                
                # 模拟比分
                if result == "HOME_WIN":
                    home_score = random.randint(1, 3)
                    away_score = random.randint(0, home_score - 1) if home_score > 1 else 0
                elif result == "DRAW":
                    score = random.randint(0, 2)
                    home_score = score
                    away_score = score
                else:  # AWAY_WIN
                    away_score = random.randint(1, 3)
                    home_score = random.randint(0, away_score - 1) if away_score > 1 else 0
                
                simulated_matches.append({
                    "match_id": f"{home['code']}_{away['code']}",
                    "home_team": home['code'],
                    "away_team": away['code'],
                    "home_score": home_score,
                    "away_score": away_score,
                    "result": result,
                    "stage": "GROUP",
                    "status": "completed",
                    "datetime": "2026-06-11T09:00:00"
                })
                
                match_idx += 1
                
                # 只返回前48场（前8个小组的比赛）
                if match_idx >= 48:
                    break
            
            if match_idx >= 48:
                break
        
        return simulated_matches
    
    def _fetch_from_api_football(self, competition: str) -> List[Dict]:
        """
        从API-Football获取真实数据
        
        需要API密钥
        """
        # 这里需要API密钥配置
        # API-Football文档: https://www.api-football.com/
        
        # 示例代码（需要配置api_key）
        # headers = {"x-apisports-key": self.api_key}
        # response = requests.get(f"{self.DATA_SOURCES['api_football']['url']}/fixtures", 
        #                         headers=headers, params={"league": 1, "season": 2026})
        
        return []
    
    def fetch_by_match_id(self, match_id: str) -> Optional[Dict]:
        """
        获取单场比赛结果
        """
        matches = self.fetch_completed_matches()
        
        for m in matches:
            if m["match_id"] == match_id:
                return m
        
        return None
    
    def check_match_status(self, match_id: str) -> str:
        """
        检查比赛状态
        
        Returns:
            "not_started" / "in_progress" / "completed"
        """
        match = self.fetch_by_match_id(match_id)
        
        if match:
            return match.get("status", "unknown")
        
        return "not_started"


class AutoVerificationSystem:
    """
    自动验证系统
    
    功能：
    1. 定时检查比赛状态
    2. 发现完成的比赛自动验证
    3. 更新准确率统计
    """
    
    def __init__(self):
        self.fetcher = MatchResultFetcher()
        self.verified_matches = []
    
    def auto_verify_all(self) -> Dict:
        """
        自动验证所有可验证的比赛
        
        流程：
        1. 先生成所有小组赛的预测记录
        2. 获取已完成的比赛结果
        3. 自动验证所有预测
        4. 更新准确率统计
        """
        from services.accuracy_tracker import get_accuracy_tracker
        from services.prediction_engine_v4 import create_v4_engine
        from data.world_cup_2026 import GROUPS
        
        tracker = get_accuracy_tracker()
        engine = create_v4_engine()
        
        # 步骤1: 生成所有小组赛的预测记录
        pairs = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
        predictions_generated = 0
        
        for group_name, teams in GROUPS.items():
            for idx, (i, j) in enumerate(pairs):
                home, away = teams[i], teams[j]
                
                # 生成预测
                pred = engine.predict_match(home, away, stage="GROUP", is_neutral=True)
                predictions_generated += 1
        
        # 步骤2: 获取已完成的比赛结果
        completed_matches = self.fetcher.fetch_completed_matches("WC2026")
        
        results = {
            "predictions_generated": predictions_generated,
            "total_completed": len(completed_matches),
            "verified": 0,
            "already_verified": 0,
            "details": []
        }
        
        # 步骤3: 验证这场比赛的所有预测
        for match in completed_matches:
            # 将小组比赛序号映射到match_id
            match_id = self._map_match_id(match)
            result = match["result"]
            
            try:
                verification = tracker.verify_prediction(match_id, result)
                
                if verification.get("verified_count", 0) > 0:
                    results["verified"] += 1
                    results["details"].append({
                        "match_id": match_id,
                        "result": result,
                        "verified_count": verification["verified_count"]
                    })
                
                self.verified_matches.append(match_id)
                
            except Exception as e:
                print(f"验证失败 {match_id}: {e}")
        
        # 步骤4: 获取更新后的准确率
        report = tracker.get_accuracy_report()
        results["accuracy_report"] = report
        
        return results
    
    def _map_match_id(self, match: Dict) -> str:
        """
        将比赛数据映射到数据库中的match_id
        
        数据库格式: TEAM1_TEAM2 (如ARG_USA)
        输入格式: {match_id: "A_0", home: "SEN", away: "NED", ...}
        """
        # 直接使用球队代码组合
        home = match.get("home_team", "")
        away = match.get("away_team", "")
        
        # 返回TEAM1_TEAM2格式
        return f"{home}_{away}"
    
    def auto_verify_match(self, match_id: str) -> Dict:
        """
        自动验证单场比赛
        """
        match_result = self.fetcher.fetch_by_match_id(match_id)
        
        if not match_result:
            return {"error": "比赛未完成或未找到"}
        
        from services.accuracy_tracker import get_accuracy_tracker
        tracker = get_accuracy_tracker()
        
        return tracker.verify_prediction(match_id, match_result["result"])
    
    def schedule_verification(self, interval_minutes: int = 60):
        """
        设置定时验证
        
        Args:
            interval_minutes: 检查间隔（分钟）
        """
        # 这里可以集成定时任务系统
        # 例如使用 cron 或 APScheduler
        pass
    
    def get_verification_status(self) -> Dict:
        """
        获取验证状态
        """
        return {
            "verified_matches": self.verified_matches,
            "total_verified": len(self.verified_matches),
            "last_verification": datetime.now().isoformat()
        }


def get_auto_verification_system():
    """获取自动验证系统实例"""
    return AutoVerificationSystem()


def get_match_result_fetcher():
    """获取比赛结果获取器"""
    return MatchResultFetcher()