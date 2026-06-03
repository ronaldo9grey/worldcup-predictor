"""比赛预测引擎 v2 - 完整赛程模拟 + 因子可视化"""
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import random
import math

# 因子定义（可视化用）
FACTOR_DEFINITIONS = {
    "elo_diff": {"name": "Elo实力差", "icon": "📊", "color": "#4A90D9", "desc": "基于Elo评分的双方实力差距"},
    "rank_gap": {"name": "排名差距", "icon": "🏅", "color": "#F5A623", "desc": "FIFA排名差异，差距大则冷门潜力大"},
    "form_diff": {"name": "状态差异", "icon": "📈", "color": "#7ED321", "desc": "近5场战绩对比，状态好的一方能超常发挥"},
    "home_advantage": {"name": "主场/中立场", "icon": "🏟️", "color": "#9B59B6", "desc": "东道主有显著主场优势，中立场影响较小"},
    "stage_factor": {"name": "赛事阶段", "icon": "🏆", "color": "#E74C3C", "desc": "小组赛冷门更多，淘汰赛强队更稳"},
    "continent_factor": {"name": "洲际因素", "icon": "🌍", "color": "#1ABC9C", "desc": "跨洲作战的适应性问题"},
}

FACTOR_WEIGHTS = {
    "elo_diff": 0.30,
    "rank_gap": 0.10,
    "form_diff": 0.25,
    "home_advantage": 0.10,
    "stage_factor": 0.15,
    "continent_factor": 0.10,
}


@dataclass
class FactorContribution:
    """单个因子的贡献"""
    key: str
    name: str
    icon: str
    color: str
    desc: str
    weight: float          # 该因子的权重
    raw_value: float       # 原始计算值
    contribution: float    # 对最终结果的贡献（-1到1，正值倾向主队）


@dataclass
class MatchPrediction:
    """单场预测结果"""
    home_code: str
    home_name: str
    home_name_cn: str
    away_code: str
    away_name: str
    away_name_cn: str
    
    home_win_prob: float
    draw_prob: float
    away_win_prob: float
    
    prediction: str        # HOME_WIN / DRAW / AWAY_WIN
    confidence: str        # HIGH / MEDIUM / LOW
    
    upset_score: float
    is_upset: bool
    upset_factors: List[str]
    
    # 因子可视化
    factors: List[FactorContribution] = field(default_factory=list)
    
    # 比赛元信息
    stage: str = "GROUP"
    group: str = ""
    match_id: str = ""


class PredictionEngineV2:
    """预测引擎 v2"""
    
    def __init__(self):
        self.weights = FACTOR_WEIGHTS
    
    def predict_match(self, home: dict, away: dict, 
                      stage: str = "GROUP", is_neutral: bool = True,
                      host_countries: list = None) -> MatchPrediction:
        """
        预测单场比赛，返回详细因子分解
        """
        factors = []
        
        # 1. Elo实力差
        elo_diff = home.get("elo", 1500) - away.get("elo", 1500)
        elo_contribution = min(1, max(-1, elo_diff / 300))
        factors.append(FactorContribution(
            key="elo_diff", name="Elo实力差", icon="📊", color="#4A90D9",
            desc=f"Elo差{abs(elo_diff):.0f}分，{'主队' if elo_diff > 0 else '客队'}更强",
            weight=self.weights["elo_diff"],
            raw_value=elo_diff,
            contribution=elo_contribution
        ))
        
        # 2. 排名差距
        rank_gap = away.get("rank", 50) - home.get("rank", 50)
        rank_contribution = min(1, max(-1, rank_gap / 40))
        factors.append(FactorContribution(
            key="rank_gap", name="排名差距", icon="🏅", color="#F5A623",
            desc=f"FIFA排名差{abs(rank_gap)}位",
            weight=self.weights["rank_gap"],
            raw_value=rank_gap,
            contribution=rank_contribution
        ))
        
        # 3. 状态差异
        home_form_score = self._form_score(home.get("form", "WDWDW"))
        away_form_score = self._form_score(away.get("form", "WDWDW"))
        form_diff = home_form_score - away_form_score
        form_contribution = min(1, max(-1, form_diff / 2))
        factors.append(FactorContribution(
            key="form_diff", name="状态差异", icon="📈", color="#7ED321",
            desc=f"近5场：{home.get('form','?')} vs {away.get('form','?')}",
            weight=self.weights["form_diff"],
            raw_value=form_diff,
            contribution=form_contribution
        ))
        
        # 4. 主场/中立场
        home_adv = 0.0
        home_country = home.get("code", "")
        if host_countries and home_country in host_countries:
            home_adv = 0.6
            adv_desc = f"{home.get('name_cn','')}是东道主，显著主场优势"
        elif not is_neutral:
            home_adv = 0.3
            adv_desc = "主场比赛，有一定优势"
        else:
            home_adv = 0.0
            adv_desc = "中立场，无主场优势"
        factors.append(FactorContribution(
            key="home_advantage", name="主场/中立场", icon="🏟️", color="#9B59B6",
            desc=adv_desc,
            weight=self.weights["home_advantage"],
            raw_value=home_adv,
            contribution=home_adv
        ))
        
        # 5. 赛事阶段
        stage_bias = {"GROUP": 0.0, "R32": 0.05, "R16": 0.08, "QF": 0.12, "SF": 0.15, "FI": 0.18, "3RD": -0.05}
        stage_val = stage_bias.get(stage, 0.0)
        stage_desc = {"GROUP": "小组赛冷门频发", "R32": "32强赛开始淘汰", "R16": "16强赛强队渐稳",
                      "QF": "8强赛强队主导", "SF": "4强赛实力说话", "FI": "决赛容错率最低", "3RD": "季军赛战意成疑"}
        factors.append(FactorContribution(
            key="stage_factor", name="赛事阶段", icon="🏆", color="#E74C3C",
            desc=stage_desc.get(stage, ""),
            weight=self.weights["stage_factor"],
            raw_value=stage_val,
            contribution=stage_val
        ))
        
        # 6. 洲际因素
        home_continent = home.get("continent", "EU")
        away_continent = away.get("continent", "EU")
        # 跨洲作战的客队有劣势
        if host_countries:
            # 在美洲举办
            americas = {"NA", "SA"}
            if home_continent in americas and away_continent not in americas:
                cont_adv = 0.2
            elif away_continent in americas and home_continent not in americas:
                cont_adv = -0.2
            else:
                cont_adv = 0.0
        else:
            cont_adv = 0.0
        factors.append(FactorContribution(
            key="continent_factor", name="洲际因素", icon="🌍", color="#1ABC9C",
            desc=f"{home_continent} vs {away_continent}" + ("，美洲球队适应性好" if cont_adv != 0 else "，同洲作战"),
            weight=self.weights["continent_factor"],
            raw_value=cont_adv,
            contribution=cont_adv
        ))
        
        # 综合计算概率
        total_contribution = sum(f.contribution * f.weight for f in factors)
        
        # 基础概率
        home_prob = 0.4 + total_contribution * 0.35
        draw_prob = max(0.1, 0.28 - abs(total_contribution) * 0.2)
        away_prob = 1 - home_prob - draw_prob
        
        # 确保概率合理
        home_prob = max(0.05, min(0.85, home_prob))
        away_prob = max(0.05, min(0.85, away_prob))
        draw_prob = max(0.08, 1 - home_prob - away_prob)
        
        # 归一化
        total = home_prob + draw_prob + away_prob
        home_prob /= total
        draw_prob /= total
        away_prob /= total
        
        # 判断预测方向
        if home_prob > away_prob and home_prob > draw_prob:
            prediction = "HOME_WIN"
        elif away_prob > home_prob and away_prob > draw_prob:
            prediction = "AWAY_WIN"
        else:
            prediction = "DRAW"
        
        # 信心等级
        max_prob = max(home_prob, draw_prob, away_prob)
        confidence = "HIGH" if max_prob >= 0.50 else "MEDIUM" if max_prob >= 0.38 else "LOW"
        
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
            upset_score=upset_score,
            is_upset=is_upset,
            upset_factors=upset_factors,
            factors=factors,
            stage=stage,
            group=home.get("group", ""),
        )
    
    def predict_group(self, group_teams: list, group_name: str) -> dict:
        """
        预测小组赛全部比赛，计算积分排名
        返回: { standings, matches, qualified }
        """
        matches = []
        standings = {t["code"]: {"team": t, "points": 0, "gf": 0, "ga": 0, "w": 0, "d": 0, "l": 0} 
                     for t in group_teams}
        
        pairs = [(0,1), (0,2), (0,3), (1,2), (1,3), (2,3)]
        for a, b in pairs:
            home = group_teams[a]
            away = group_teams[b]
            pred = self.predict_match(home, away, stage="GROUP", is_neutral=True)
            matches.append(pred)
            
            # 模拟比赛结果（基于概率）
            result = self._simulate_result(pred)
            
            hc, ac = home["code"], away["code"]
            standings[hc]["gf"] += result["home_goals"]
            standings[hc]["ga"] += result["away_goals"]
            standings[ac]["gf"] += result["away_goals"]
            standings[ac]["ga"] += result["home_goals"]
            
            if result["home_win"]:
                standings[hc]["w"] += 1; standings[hc]["points"] += 3
                standings[ac]["l"] += 1
            elif result["draw"]:
                standings[hc]["d"] += 1; standings[hc]["points"] += 1
                standings[ac]["d"] += 1; standings[ac]["points"] += 1
            else:
                standings[ac]["w"] += 1; standings[ac]["points"] += 3
                standings[hc]["l"] += 1
        
        # 排名
        ranked = sorted(standings.values(), 
                       key=lambda x: (x["points"], x["gf"]-x["ga"], x["gf"]), reverse=True)
        
        return {
            "group": group_name,
            "matches": matches,
            "standings": ranked,
            "qualified_1st": ranked[0]["team"]["code"],
            "qualified_2nd": ranked[1]["team"]["code"],
            "third_place": ranked[2]["team"]["code"],
            "third_points": ranked[2]["points"],
        }
    
    def simulate_tournament(self, groups_data: dict) -> dict:
        """
        模拟整届杯赛：从小组赛到冠军
        返回完整的赛程和结果
        """
        # 1. 小组赛
        group_results = {}
        all_thirds = []
        
        for gname, gteams in groups_data.items():
            result = self.predict_group(gteams, gname)
            group_results[gname] = result
            all_thirds.append({
                "code": result["third_place"],
                "points": result["third_points"],
                "group": gname,
            })
        
        # 2. 选出8个最佳第3名
        best_thirds = sorted(all_thirds, key=lambda x: x["points"], reverse=True)[:8]
        best_third_codes = {t["code"] for t in best_thirds}
        
        # 3. 构建32强对阵表
        knockout = self._build_knockout_bracket(group_results, best_third_codes)
        
        # 4. 模拟淘汰赛
        bracket_results = self._simulate_knockout(knockout)
        
        return {
            "group_stage": group_results,
            "best_thirds": [t["code"] for t in best_thirds],
            "knockout": bracket_results,
            "champion": bracket_results.get("champion", ""),
            "runner_up": bracket_results.get("runner_up", ""),
            "third_place_team": bracket_results.get("third_place", ""),
        }
    
    def _build_knockout_bracket(self, group_results: dict, best_third_codes: set) -> list:
        """构建淘汰赛对阵表"""
        # 简化版：按小组名排序配对
        # 实际世界杯有复杂的配对规则，这里用简化逻辑
        group_names = sorted(group_results.keys())
        
        bracket = []
        # 32强：第1名 vs 第3名(外卡)，第2名 vs 第2名
        for i in range(0, len(group_names), 2):
            g1 = group_names[i]
            g2 = group_names[i+1] if i+1 < len(group_names) else group_names[i]
            
            r1 = group_results[g1]
            r2 = group_results[g2]
            
            # 对阵1: A1 vs B3(如果B3是外卡)
            bracket.append({
                "round": "R32",
                "home": r1["qualified_1st"],
                "away": r2["qualified_2nd"],
                "home_source": f"{g1}组第1",
                "away_source": f"{g2}组第2",
            })
            
            # 对阵2: A2 vs B1
            bracket.append({
                "round": "R32",
                "home": r2["qualified_1st"],
                "away": r1["qualified_2nd"],
                "home_source": f"{g2}组第1",
                "away_source": f"{g1}组第2",
            })
        
        # 添加外卡队伍的对阵（第3名）
        wildcard_matches = []
        for gname in group_names:
            r = group_results[gname]
            if r["third_place"] in best_third_codes:
                # 找一个第2名对手
                for other_gname in group_names:
                    if other_gname != gname:
                        other_r = group_results[other_gname]
                        wildcard_matches.append({
                            "round": "R32",
                            "home": other_r["qualified_1st"],
                            "away": r["third_place"],
                            "home_source": f"{other_gname}组第1",
                            "away_source": f"{gname}组第3(外卡)",
                        })
                        break
                if len(wildcard_matches) >= 8:
                    break
        
        bracket.extend(wildcard_matches)
        
        return bracket[:16]  # 32强=16场
    
    def _simulate_knockout(self, bracket: list) -> dict:
        """模拟淘汰赛"""
        from data.world_cup_2026 import GROUPS
        
        # 构建球队查找表
        all_teams = {}
        for gteams in GROUPS.values():
            for t in gteams:
                all_teams[t["code"]] = t
        
        results = {"R32": [], "R16": [], "QF": [], "SF": [], "3RD": [], "FI": []}
        current_round = list(bracket)
        
        round_names = ["R32", "R16", "QF", "SF"]
        
        for round_name in round_names:
            next_round = []
            for i in range(0, len(current_round), 2):
                if i >= len(current_round):
                    break
                
                match_a = current_round[i]
                match_b = current_round[i+1] if i+1 < len(current_round) else None
                
                # 模拟match_a
                home_a = all_teams.get(match_a["home"], {"code": match_a["home"], "name": match_a["home"], "name_cn": match_a["home"], "elo": 1600, "rank": 30, "form": "WDWDW", "continent": "EU"})
                away_a = all_teams.get(match_a["away"], {"code": match_a["away"], "name": match_a["away"], "name_cn": match_a["away"], "elo": 1600, "rank": 30, "form": "WDWDW", "continent": "EU"})
                
                pred_a = self.predict_match(home_a, away_a, stage=round_name, is_neutral=True)
                winner_a = self._simulate_knockout_result(pred_a)
                
                results[round_name].append({
                    "home": match_a["home"], "away": match_a["away"],
                    "home_source": match_a.get("home_source", ""),
                    "away_source": match_a.get("away_source", ""),
                    "prediction": pred_a,
                    "winner": winner_a,
                })
                next_round.append({"home": winner_a, "away": "", "home_source": f"{round_name}胜者", "away_source": ""})
                
                # 模拟match_b
                if match_b:
                    home_b = all_teams.get(match_b["home"], {"code": match_b["home"], "name": match_b["home"], "name_cn": match_b["home"], "elo": 1600, "rank": 30, "form": "WDWDW", "continent": "EU"})
                    away_b = all_teams.get(match_b["away"], {"code": match_b["away"], "name": match_b["away"], "name_cn": match_b["away"], "elo": 1600, "rank": 30, "form": "WDWDW", "continent": "EU"})
                    
                    pred_b = self.predict_match(home_b, away_b, stage=round_name, is_neutral=True)
                    winner_b = self._simulate_knockout_result(pred_b)
                    
                    results[round_name].append({
                        "home": match_b["home"], "away": match_b["away"],
                        "home_source": match_b.get("home_source", ""),
                        "away_source": match_b.get("away_source", ""),
                        "prediction": pred_b,
                        "winner": winner_b,
                    })
                    next_round.append({"home": winner_b, "away": "", "home_source": f"{round_name}胜者", "away_source": ""})
            
            # 配对下一轮
            paired = []
            for i in range(0, len(next_round)-1, 2):
                paired.append({
                    "home": next_round[i]["home"],
                    "away": next_round[i+1]["home"],
                    "home_source": next_round[i]["home_source"],
                    "away_source": next_round[i+1]["home_source"],
                })
            current_round = paired
        
        # 半决赛结果 → 决赛和季军赛
        sf_results = results.get("SF", [])
        if len(sf_results) >= 2:
            finalist_1 = sf_results[0]["winner"]
            finalist_2 = sf_results[1]["winner"]
            loser_1 = sf_results[0]["home"] if sf_results[0]["winner"] != sf_results[0]["home"] else sf_results[0]["away"]
            loser_2 = sf_results[1]["home"] if sf_results[1]["winner"] != sf_results[1]["home"] else sf_results[1]["away"]
            
            # 决赛
            f_home = all_teams.get(finalist_1, {"code": finalist_1, "name": finalist_1, "name_cn": finalist_1, "elo": 1600, "rank": 30, "form": "WDWDW", "continent": "EU"})
            f_away = all_teams.get(finalist_2, {"code": finalist_2, "name": finalist_2, "name_cn": finalist_2, "elo": 1600, "rank": 30, "form": "WDWDW", "continent": "EU"})
            pred_fi = self.predict_match(f_home, f_away, stage="FI", is_neutral=True)
            champion = self._simulate_knockout_result(pred_fi)
            runner_up = finalist_2 if champion == finalist_1 else finalist_1
            results["FI"] = [{"home": finalist_1, "away": finalist_2, "prediction": pred_fi, "winner": champion}]
            
            # 季军赛
            t_home = all_teams.get(loser_1, {"code": loser_1, "name": loser_1, "name_cn": loser_1, "elo": 1600, "rank": 30, "form": "WDWDW", "continent": "EU"})
            t_away = all_teams.get(loser_2, {"code": loser_2, "name": loser_2, "name_cn": loser_2, "elo": 1600, "rank": 30, "form": "WDWDW", "continent": "EU"})
            pred_3rd = self.predict_match(t_home, t_away, stage="3RD", is_neutral=True)
            third = self._simulate_knockout_result(pred_3rd)
            results["3RD"] = [{"home": loser_1, "away": loser_2, "prediction": pred_3rd, "winner": third}]
            
            results["champion"] = champion
            results["runner_up"] = runner_up
            results["third_place"] = third
        
        return results
    
    def _form_score(self, form: str) -> float:
        """状态得分 -2到2"""
        if not form:
            return 0
        score = 0
        weights = [0.4, 0.25, 0.2, 0.1, 0.05]
        for i, c in enumerate(form.upper()[:5]):
            if i < len(weights):
                if c == 'W': score += weights[i]
                elif c == 'L': score -= weights[i]
        return score
    
    def _simulate_result(self, pred: MatchPrediction) -> dict:
        """基于概率模拟比赛结果"""
        r = random.random()
        if r < pred.home_win_prob:
            return {"home_win": True, "draw": False, "home_goals": random.randint(1,3), "away_goals": random.randint(0,2)}
        elif r < pred.home_win_prob + pred.draw_prob:
            goals = random.randint(0,3)
            return {"home_win": False, "draw": True, "home_goals": goals, "away_goals": goals}
        else:
            return {"home_win": False, "draw": False, "home_goals": random.randint(0,2), "away_goals": random.randint(1,3)}
    
    def _simulate_knockout_result(self, pred: MatchPrediction) -> str:
        """模拟淘汰赛结果（不允许平局，加时赛/点球）"""
        r = random.random()
        if r < pred.home_win_prob:
            return pred.home_code
        elif r < pred.home_win_prob + pred.draw_prob:
            # 平局则看谁更强
            return pred.home_code if random.random() < 0.55 else pred.away_code
        else:
            return pred.away_code
    
    def _analyze_upset(self, home, away, home_prob, away_prob, stage, factors) -> Tuple[float, bool, List[str]]:
        """分析冷门潜力"""
        upset_factors = []
        
        # 找出弱队
        if home.get("rank", 50) < away.get("rank", 50):
            strong_team, weak_team = home, away
        else:
            strong_team, weak_team = away, home
        
        rank_gap = abs(home.get("rank", 50) - away.get("rank", 50))
        score = 0
        
        if rank_gap > 20:
            upset_factors.append(f"排名差{rank_gap}位")
            score += min(30, rank_gap / 2)
        
        # 状态差异
        weak_form = weak_team.get("form", "WDWDW")
        strong_form = strong_team.get("form", "WDWDW")
        if weak_form.count('W') >= 3:
            upset_factors.append("弱队状态火热")
            score += 20
        if strong_form[:3].count('L') >= 2:
            upset_factors.append("强队近期低迷")
            score += 25
        
        # 小组赛更容易冷门
        if stage == "GROUP":
            score += 10
        
        # 概率接近
        if max(home_prob, away_prob) - min(home_prob, away_prob) < 0.1:
            score += 10
            upset_factors.append("实力接近")
        
        is_upset = score >= 40
        return round(score, 1), is_upset, upset_factors