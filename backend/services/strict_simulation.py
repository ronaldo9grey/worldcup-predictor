"""严谨的淘汰赛模拟引擎 v2 - 修复对阵逻辑"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import random
import math


@dataclass
class KnockoutMatch:
    """淘汰赛比赛"""
    round_name: str
    round_cn: str
    match_num: int
    home_code: str
    home_name: str
    home_name_cn: str
    away_code: str
    away_name: str
    away_name_cn: str
    home_score: int = 0
    away_score: int = 0
    winner: str = ""
    loser: str = ""
    is_extra_time: bool = False
    is_penalty: bool = False
    home_win_prob: float = 0.0
    away_win_prob: float = 0.0


class StrictSimulationEngine:
    """严谨的模拟引擎"""
    
    def __init__(self, groups_data: dict, team_lookup: dict):
        self.groups = groups_data
        self.teams = team_lookup
    
    def simulate_tournament(self, deterministic: bool = True) -> dict:
        """
        模拟整届杯赛
        
        Args:
            deterministic: True = 严谨模式（选概率最高），False = 概率模式
        """
        # 1. 小组赛出线结果
        qualified = self._get_group_results()
        
        # 2. 构建32强对阵表
        r32_matches = self._build_round_of_32(qualified)
        
        # 2.5 先模拟32强比赛
        for m in r32_matches:
            self._simulate_match(m, "R32", deterministic)
        
        # 3. 模拟各轮
        r16_matches = self._simulate_round(r32_matches, "R16", "16强", deterministic)
        qf_matches = self._simulate_round(r16_matches, "QF", "1/4决赛", deterministic)
        sf_matches = self._simulate_round(qf_matches, "SF", "半决赛", deterministic)
        
        # 4. 季军赛
        third_match = self._create_third_place_match(sf_matches)
        self._simulate_match(third_match, "THIRD", deterministic)
        
        # 5. 决赛
        final_match = self._create_final_match(sf_matches)
        self._simulate_match(final_match, "FI", deterministic)
        
        # 6. 组装结果
        return {
            "mode": "严谨模式" if deterministic else "概率模式",
            "group_stage": qualified,
            "knockout": {
                "R32": [self._format_match(m) for m in r32_matches],
                "R16": [self._format_match(m) for m in r16_matches],
                "QF": [self._format_match(m) for m in qf_matches],
                "SF": [self._format_match(m) for m in sf_matches],
                "THIRD": [self._format_match(third_match)],
                "FI": [self._format_match(final_match)],
            },
            "champion": final_match.winner,
            "champion_name_cn": self.teams.get(final_match.winner, {}).get("name_cn", final_match.winner),
            "runner_up": final_match.loser,
            "runner_up_name_cn": self.teams.get(final_match.loser, {}).get("name_cn", final_match.loser),
            "third_place": third_match.winner,
            "third_place_name_cn": self.teams.get(third_match.winner, {}).get("name_cn", third_match.winner),
        }
    
    def _get_group_results(self) -> dict:
        """获取小组赛出线结果"""
        results = {}
        for gname, teams in self.groups.items():
            # 按Elo排序出线
            sorted_teams = sorted(teams, key=lambda t: -t.get("elo", 1500))
            results[gname] = {
                "first": sorted_teams[0]["code"],
                "first_name_cn": sorted_teams[0].get("name_cn", sorted_teams[0]["code"]),
                "second": sorted_teams[1]["code"],
                "second_name_cn": sorted_teams[1].get("name_cn", sorted_teams[1]["code"]),
                "third": sorted_teams[2]["code"],
                "third_name_cn": sorted_teams[2].get("name_cn", sorted_teams[2]["code"]),
            }
        
        # 选8个最佳第3名（按Elo）
        all_thirds = [(gname, data["third"], self.teams.get(data["third"], {}).get("elo", 1500))
                      for gname, data in results.items()]
        best_thirds = sorted(all_thirds, key=lambda x: -x[2])[:8]
        best_third_codes = {t[1] for t in best_thirds}
        
        for gname in results:
            results[gname]["third_qualified"] = results[gname]["third"] in best_third_codes
        
        return results
    
    def _build_round_of_32(self, qualified: dict) -> List[KnockoutMatch]:
        """构建32强对阵（简化逻辑）"""
        matches = []
        match_num = 1
        
        # 收集所有出线球队
        all_teams = []
        for gname in sorted(qualified.keys()):
            data = qualified[gname]
            all_teams.append((data["first"], data["first_name_cn"], gname + "组第1"))
            all_teams.append((data["second"], data["second_name_cn"], gname + "组第2"))
        
        # 添加外卡球队
        for gname in sorted(qualified.keys()):
            if qualified[gname].get("third_qualified"):
                data = qualified[gname]
                all_teams.append((data["third"], data["third_name_cn"], gname + "组第3(外卡)"))
        
        # 确保正好32队
        all_teams = all_teams[:32]
        
        # 按Elo排序
        all_teams_sorted = sorted(all_teams, key=lambda x: -self.teams.get(x[0], {}).get("elo", 1500))
        
        # 配对：第1-16名 vs 第17-32名（种子 vs 非种子）
        seeds = all_teams_sorted[:16]
        non_seeds = all_teams_sorted[16:]
        
        for i in range(16):
            home = seeds[i]
            away = non_seeds[i]
            matches.append(KnockoutMatch(
                round_name="R32",
                round_cn="32强",
                match_num=i + 1,
                home_code=home[0],
                home_name=self.teams.get(home[0], {}).get("name", home[0]),
                home_name_cn=home[1],
                away_code=away[0],
                away_name=self.teams.get(away[0], {}).get("name", away[0]),
                away_name_cn=away[1],
            ))
        
        return matches
    
    def _simulate_round(self, prev_matches: List[KnockoutMatch], round_name: str, round_cn: str, deterministic: bool) -> List[KnockoutMatch]:
        """模拟一轮并生成下一轮"""
        next_matches = []
        
        for i in range(0, len(prev_matches), 2):
            if i + 1 >= len(prev_matches):
                break
            
            winner1 = prev_matches[i].winner
            winner2 = prev_matches[i + 1].winner
            
            home_team = self.teams.get(winner1, {"name": winner1, "name_cn": winner1})
            away_team = self.teams.get(winner2, {"name": winner2, "name_cn": winner2})
            
            match = KnockoutMatch(
                round_name=round_name,
                round_cn=round_cn,
                match_num=i // 2 + 1,
                home_code=winner1,
                home_name=home_team.get("name", winner1),
                home_name_cn=home_team.get("name_cn", winner1),
                away_code=winner2,
                away_name=away_team.get("name", winner2),
                away_name_cn=away_team.get("name_cn", winner2),
            )
            
            self._simulate_match(match, round_name, deterministic)
            next_matches.append(match)
        
        return next_matches
    
    def _create_third_place_match(self, sf_matches: List[KnockoutMatch]) -> KnockoutMatch:
        """创建季军赛"""
        loser1 = sf_matches[0].loser
        loser2 = sf_matches[1].loser if len(sf_matches) > 1 else sf_matches[0].loser
        
        home_team = self.teams.get(loser1, {"name": loser1, "name_cn": loser1})
        away_team = self.teams.get(loser2, {"name": loser2, "name_cn": loser2})
        
        return KnockoutMatch(
            round_name="THIRD",
            round_cn="季军赛",
            match_num=1,
            home_code=loser1,
            home_name=home_team.get("name", loser1),
            home_name_cn=home_team.get("name_cn", loser1),
            away_code=loser2,
            away_name=away_team.get("name", loser2),
            away_name_cn=away_team.get("name_cn", loser2),
        )
    
    def _create_final_match(self, sf_matches: List[KnockoutMatch]) -> KnockoutMatch:
        """创建决赛"""
        winner1 = sf_matches[0].winner
        winner2 = sf_matches[1].winner if len(sf_matches) > 1 else sf_matches[0].winner
        
        home_team = self.teams.get(winner1, {"name": winner1, "name_cn": winner1})
        away_team = self.teams.get(winner2, {"name": winner2, "name_cn": winner2})
        
        return KnockoutMatch(
            round_name="FI",
            round_cn="决赛",
            match_num=1,
            home_code=winner1,
            home_name=home_team.get("name", winner1),
            home_name_cn=home_team.get("name_cn", winner1),
            away_code=winner2,
            away_name=away_team.get("name", winner2),
            away_name_cn=away_team.get("name_cn", winner2),
        )
    
    def _simulate_match(self, match: KnockoutMatch, round_name: str, deterministic: bool):
        """模拟单场比赛"""
        home = self.teams.get(match.home_code, {"elo": 1600, "rank": 30})
        away = self.teams.get(match.away_code, {"elo": 1600, "rank": 30})
        
        home_elo = home.get("elo", 1600)
        away_elo = away.get("elo", 1600)
        
        # Elo概率
        diff = home_elo - away_elo
        home_win_prob = 1 / (1 + math.pow(10, -diff / 400))
        draw_prob = max(0.1, 0.25 - abs(diff) / 800)
        away_win_prob = max(0.05, 1 - home_win_prob - draw_prob)
        
        match.home_win_prob = round(home_win_prob, 3)
        match.away_win_prob = round(away_win_prob, 3)
        
        # 决定胜者
        if deterministic:
            if home_win_prob > away_win_prob:
                winner_code = match.home_code
            elif away_win_prob > home_win_prob:
                winner_code = match.away_code
            else:
                winner_code = match.home_code if home_elo >= away_elo else match.away_code
        else:
            r = random.random()
            if r < home_win_prob:
                winner_code = match.home_code
            elif r < home_win_prob + draw_prob:
                winner_code = match.home_code if random.random() < 0.55 else match.away_code
            else:
                winner_code = match.away_code
        
        match.winner = winner_code
        match.loser = match.away_code if winner_code == match.home_code else match.home_code
        
        # 比分
        if round_name == "FI":
            match.home_score = random.randint(0, 2)
            match.away_score = random.randint(0, 2)
            if match.home_score == match.away_score:
                if match.winner == match.home_code:
                    match.home_score += 1
                else:
                    match.away_score += 1
                match.is_extra_time = True
        else:
            match.home_score = random.randint(1, 3) if match.winner == match.home_code else random.randint(0, 2)
            match.away_score = random.randint(1, 3) if match.winner == match.away_code else random.randint(0, 2)
        
        # 确保胜者比分高
        if match.winner == match.home_code and match.home_score <= match.away_score:
            match.home_score = match.away_score + 1
        elif match.winner == match.away_code and match.away_score <= match.home_score:
            match.away_score = match.home_score + 1
    
    def _format_match(self, m: KnockoutMatch) -> dict:
        """格式化比赛"""
        return {
            "round": m.round_name,
            "round_cn": m.round_cn,
            "match_num": m.match_num,
            "home": m.home_code,
            "home_name": m.home_name,
            "home_name_cn": m.home_name_cn,
            "away": m.away_code,
            "away_name": m.away_name,
            "away_name_cn": m.away_name_cn,
            "home_score": m.home_score,
            "away_score": m.away_score,
            "winner": m.winner,
            "loser": m.loser,
            "winner_name_cn": m.home_name_cn if m.winner == m.home_code else m.away_name_cn,
            "home_win_prob": m.home_win_prob,
            "away_win_prob": m.away_win_prob,
            "is_extra_time": m.is_extra_time,
        }