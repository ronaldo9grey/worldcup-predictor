"""
历史世界杯数据 - 用于训练和验证预测模型
包含2018俄罗斯世界杯和2022卡塔尔世界杯的完整比赛数据
"""

# 2018俄罗斯世界杯 - 64场比赛结果
WORLD_CUP_2018 = {
    "name": "2018 FIFA World Cup Russia",
    "year": 2018,
    "host": "RUS",
    
    # 小组赛阶段 (48场)
    "group_stage": [
        # A组
        {"group": "A", "home": "RUS", "away": "KSA", "score": "5-0", "result": "HOME_WIN"},
        {"group": "A", "home": "EGY", "away": "URU", "score": "0-1", "result": "AWAY_WIN"},
        {"group": "A", "home": "RUS", "away": "EGY", "score": "3-1", "result": "HOME_WIN"},
        {"group": "A", "home": "URU", "away": "KSA", "score": "1-0", "result": "HOME_WIN"},
        {"group": "A", "home": "URU", "away": "RUS", "score": "3-0", "result": "HOME_WIN"},
        {"group": "A", "home": "KSA", "away": "EGY", "score": "2-1", "result": "HOME_WIN"},
        
        # B组
        {"group": "B", "home": "MAR", "away": "IRN", "score": "1-0", "result": "HOME_WIN"},
        {"group": "B", "home": "POR", "away": "ESP", "score": "3-3", "result": "DRAW"},
        {"group": "B", "home": "POR", "away": "MAR", "score": "1-0", "result": "HOME_WIN"},
        {"group": "B", "home": "IRN", "away": "ESP", "score": "0-1", "result": "AWAY_WIN"},
        {"group": "B", "home": "IRN", "away": "POR", "score": "1-1", "result": "DRAW"},
        {"group": "B", "home": "ESP", "away": "MAR", "score": "2-2", "result": "DRAW"},
        
        # C组
        {"group": "C", "home": "FRA", "away": "AUS", "score": "2-1", "result": "HOME_WIN"},
        {"group": "C", "home": "PER", "away": "DEN", "score": "0-1", "result": "AWAY_WIN"},
        {"group": "C", "home": "DEN", "away": "AUS", "score": "1-1", "result": "DRAW"},
        {"group": "C", "home": "FRA", "away": "PER", "score": "1-0", "result": "HOME_WIN"},
        {"group": "C", "home": "DEN", "away": "FRA", "score": "0-0", "result": "DRAW"},
        {"group": "C", "home": "AUS", "away": "PER", "score": "0-2", "result": "AWAY_WIN"},
        
        # D组
        {"group": "D", "home": "ARG", "away": "ISL", "score": "1-1", "result": "DRAW"},
        {"group": "D", "home": "CRO", "away": "NGA", "score": "2-0", "result": "HOME_WIN"},
        {"group": "D", "home": "ARG", "away": "CRO", "score": "0-3", "result": "AWAY_WIN"},
        {"group": "D", "home": "NGA", "away": "ISL", "score": "2-0", "result": "HOME_WIN"},
        {"group": "D", "home": "NGA", "away": "ARG", "score": "1-2", "result": "AWAY_WIN"},
        {"group": "D", "home": "ISL", "away": "CRO", "score": "1-2", "result": "AWAY_WIN"},
        
        # E组
        {"group": "E", "home": "BRA", "away": "SUI", "score": "1-1", "result": "DRAW"},
        {"group": "E", "home": "SRB", "away": "CRC", "score": "0-1", "result": "AWAY_WIN"},
        {"group": "E", "home": "BRA", "away": "CRC", "score": "2-0", "result": "HOME_WIN"},
        {"group": "E", "home": "SRB", "away": "SUI", "score": "1-2", "result": "AWAY_WIN"},
        {"group": "E", "home": "SRB", "away": "BRA", "score": "0-2", "result": "AWAY_WIN"},
        {"group": "E", "home": "SUI", "away": "CRC", "score": "2-2", "result": "DRAW"},
        
        # F组
        {"group": "F", "home": "GER", "away": "MEX", "score": "0-1", "result": "AWAY_WIN"},  # 冷门！
        {"group": "F", "home": "SWE", "away": "KOR", "score": "1-0", "result": "HOME_WIN"},
        {"group": "F", "home": "KOR", "away": "MEX", "score": "1-2", "result": "AWAY_WIN"},
        {"group": "F", "home": "GER", "away": "SWE", "score": "2-1", "result": "HOME_WIN"},
        {"group": "F", "home": "KOR", "away": "GER", "score": "2-0", "result": "HOME_WIN"},  # 大冷门！
        {"group": "F", "home": "MEX", "away": "SWE", "score": "0-3", "result": "AWAY_WIN"},
        
        # G组
        {"group": "G", "home": "BEL", "away": "PAN", "score": "3-0", "result": "HOME_WIN"},
        {"group": "G", "home": "ENG", "away": "TUN", "score": "2-1", "result": "HOME_WIN"},
        {"group": "G", "home": "BEL", "away": "TUN", "score": "5-2", "result": "HOME_WIN"},
        {"group": "G", "home": "ENG", "away": "PAN", "score": "6-1", "result": "HOME_WIN"},
        {"group": "G", "home": "ENG", "away": "BEL", "score": "0-1", "result": "AWAY_WIN"},
        {"group": "G", "home": "PAN", "away": "TUN", "score": "1-2", "result": "AWAY_WIN"},
        
        # H组
        {"group": "H", "home": "COL", "away": "JPN", "score": "1-2", "result": "AWAY_WIN"},
        {"group": "H", "home": "POL", "away": "SEN", "score": "1-2", "result": "AWAY_WIN"},
        {"group": "H", "home": "JPN", "away": "SEN", "score": "2-2", "result": "DRAW"},
        {"group": "H", "home": "POL", "away": "COL", "score": "0-3", "result": "AWAY_WIN"},
        {"group": "H", "home": "JPN", "away": "POL", "score": "0-1", "result": "AWAY_WIN"},
        {"group": "H", "home": "SEN", "away": "COL", "score": "0-1", "result": "AWAY_WIN"},
    ],
    
    # 淘汰赛阶段 (16场)
    "knockout_stage": [
        # 16强
        {"round": "R16", "home": "FRA", "away": "ARG", "score": "4-3", "result": "HOME_WIN"},
        {"round": "R16", "home": "URU", "away": "POR", "score": "2-1", "result": "HOME_WIN"},
        {"round": "R16", "home": "ESP", "away": "RUS", "score": "1-1(p)", "result": "AWAY_WIN"},  # 点球
        {"round": "R16", "home": "CRO", "away": "DEN", "score": "1-1(p)", "result": "HOME_WIN"},  # 点球
        {"round": "R16", "home": "BRA", "away": "MEX", "score": "2-0", "result": "HOME_WIN"},
        {"round": "R16", "home": "BEL", "away": "JPN", "score": "3-2", "result": "HOME_WIN"},
        {"round": "R16", "home": "SWE", "away": "SUI", "score": "1-0", "result": "HOME_WIN"},
        {"round": "R16", "home": "COL", "away": "ENG", "score": "1-1(p)", "result": "AWAY_WIN"},  # 点球
        
        # 8强
        {"round": "QF", "home": "URU", "away": "FRA", "score": "0-2", "result": "AWAY_WIN"},
        {"round": "QF", "home": "BRA", "away": "BEL", "score": "1-2", "result": "AWAY_WIN"},  # 冷门
        {"round": "QF", "home": "SWE", "away": "ENG", "score": "0-2", "result": "AWAY_WIN"},
        {"round": "QF", "home": "RUS", "away": "CRO", "score": "2-2(p)", "result": "AWAY_WIN"},  # 点球
        
        # 半决赛
        {"round": "SF", "home": "FRA", "away": "BEL", "score": "1-0", "result": "HOME_WIN"},
        {"round": "SF", "home": "CRO", "away": "ENG", "score": "2-1", "result": "HOME_WIN"},
        
        # 三四名
        {"round": "3RD", "home": "BEL", "away": "ENG", "score": "2-0", "result": "HOME_WIN"},
        
        # 决赛
        {"round": "FI", "home": "FRA", "away": "CRO", "score": "4-2", "result": "HOME_WIN"},
    ],
    
    # 冠军
    "champion": "FRA",
    
    # 关键冷门比赛（用于训练冷门检测）
    "upsets": [
        {"match": "KOR-GER", "desc": "韩国2-0德国，卫冕冠军小组出局", "severity": 5},
        {"match": "MEX-GER", "desc": "墨西哥1-0德国，卫冕冠军首战失利", "severity": 4},
        {"match": "BEL-BRA", "desc": "比利时2-1巴西，八强淘汰夺冠热门", "severity": 4},
        {"match": "RUS-ESP", "desc": "俄罗斯点球淘汰西班牙", "severity": 3},
    ]
}

# 2022卡塔尔世界杯 - 64场比赛结果
WORLD_CUP_2022 = {
    "name": "2022 FIFA World Cup Qatar",
    "year": 2022,
    "host": "QAT",
    
    # 小组赛阶段 (48场)
    "group_stage": [
        # A组
        {"group": "A", "home": "SEN", "away": "NED", "score": "0-2", "result": "AWAY_WIN"},
        {"group": "A", "home": "QAT", "away": "ECU", "score": "0-2", "result": "AWAY_WIN"},
        {"group": "A", "home": "QAT", "away": "SEN", "score": "1-3", "result": "AWAY_WIN"},
        {"group": "A", "home": "NED", "away": "ECU", "score": "1-1", "result": "DRAW"},
        {"group": "A", "home": "NED", "away": "QAT", "score": "2-0", "result": "HOME_WIN"},
        {"group": "A", "home": "ECU", "away": "SEN", "score": "1-2", "result": "AWAY_WIN"},
        
        # B组
        {"group": "B", "home": "ENG", "away": "IRN", "score": "6-2", "result": "HOME_WIN"},
        {"group": "B", "home": "USA", "away": "WAL", "score": "1-1", "result": "DRAW"},
        {"group": "B", "home": "WAL", "away": "IRN", "score": "0-2", "result": "AWAY_WIN"},
        {"group": "B", "home": "ENG", "away": "USA", "score": "0-0", "result": "DRAW"},
        {"group": "B", "home": "IRN", "away": "USA", "score": "0-1", "result": "AWAY_WIN"},
        {"group": "B", "home": "WAL", "away": "ENG", "score": "0-3", "result": "AWAY_WIN"},
        
        # C组
        {"group": "C", "home": "ARG", "away": "KSA", "score": "1-2", "result": "AWAY_WIN"},  # 大冷门！
        {"group": "C", "home": "MEX", "away": "POL", "score": "0-0", "result": "DRAW"},
        {"group": "C", "home": "ARG", "away": "MEX", "score": "2-0", "result": "HOME_WIN"},
        {"group": "C", "home": "POL", "away": "KSA", "score": "2-0", "result": "HOME_WIN"},
        {"group": "C", "home": "POL", "away": "ARG", "score": "0-2", "result": "AWAY_WIN"},
        {"group": "C", "home": "KSA", "away": "MEX", "score": "1-2", "result": "AWAY_WIN"},
        
        # D组
        {"group": "D", "home": "DEN", "away": "TUN", "score": "0-0", "result": "DRAW"},
        {"group": "D", "home": "FRA", "away": "AUS", "score": "4-1", "result": "HOME_WIN"},
        {"group": "D", "home": "FRA", "away": "DEN", "score": "2-1", "result": "HOME_WIN"},
        {"group": "D", "home": "TUN", "away": "AUS", "score": "0-1", "result": "AWAY_WIN"},
        {"group": "D", "home": "AUS", "away": "DEN", "score": "1-0", "result": "HOME_WIN"},  # 小冷门
        {"group": "D", "home": "TUN", "away": "FRA", "score": "1-0", "result": "HOME_WIN"},  # 小冷门
        
        # E组
        {"group": "E", "home": "GER", "away": "JPN", "score": "1-2", "result": "AWAY_WIN"},  # 冷门！
        {"group": "E", "home": "ESP", "away": "CRC", "score": "7-0", "result": "HOME_WIN"},
        {"group": "E", "home": "JPN", "away": "CRC", "score": "0-1", "result": "AWAY_WIN"},
        {"group": "E", "home": "ESP", "away": "GER", "score": "1-1", "result": "DRAW"},
        {"group": "E", "home": "JPN", "away": "ESP", "score": "2-1", "result": "HOME_WIN"},  # 冷门！
        {"group": "E", "home": "CRC", "away": "GER", "score": "2-4", "result": "AWAY_WIN"},
        
        # F组
        {"group": "F", "home": "MAR", "away": "CRO", "score": "0-0", "result": "DRAW"},
        {"group": "F", "home": "BEL", "away": "CAN", "score": "1-0", "result": "HOME_WIN"},
        {"group": "F", "home": "BEL", "away": "MAR", "score": "0-2", "result": "AWAY_WIN"},  # 冷门
        {"group": "F", "home": "CRO", "away": "CAN", "score": "4-1", "result": "HOME_WIN"},
        {"group": "F", "home": "CRO", "away": "BEL", "score": "0-0", "result": "DRAW"},
        {"group": "F", "home": "CAN", "away": "MAR", "score": "1-2", "result": "AWAY_WIN"},
        
        # G组
        {"group": "G", "home": "SUI", "away": "CMR", "score": "1-0", "result": "HOME_WIN"},
        {"group": "G", "home": "BRA", "away": "SRB", "score": "2-0", "result": "HOME_WIN"},
        {"group": "G", "home": "CMR", "away": "SRB", "score": "3-3", "result": "DRAW"},
        {"group": "G", "home": "BRA", "away": "SUI", "score": "1-0", "result": "HOME_WIN"},
        {"group": "G", "home": "SRB", "away": "SUI", "score": "2-3", "result": "AWAY_WIN"},
        {"group": "G", "home": "CMR", "away": "BRA", "score": "1-0", "result": "HOME_WIN"},  # 小冷门
        
        # H组
        {"group": "H", "home": "URU", "away": "KOR", "score": "0-0", "result": "DRAW"},
        {"group": "H", "home": "POR", "away": "GHA", "score": "3-2", "result": "HOME_WIN"},
        {"group": "H", "home": "KOR", "away": "GHA", "score": "2-3", "result": "AWAY_WIN"},
        {"group": "H", "home": "POR", "away": "URU", "score": "2-0", "result": "HOME_WIN"},
        {"group": "H", "home": "GHA", "away": "URU", "score": "0-2", "result": "AWAY_WIN"},
        {"group": "H", "home": "KOR", "away": "POR", "score": "2-1", "result": "HOME_WIN"},  # 冷门
    ],
    
    # 淘汰赛阶段 (16场)
    "knockout_stage": [
        # 16强
        {"round": "R16", "home": "NED", "away": "USA", "score": "3-1", "result": "HOME_WIN"},
        {"round": "R16", "home": "ARG", "away": "AUS", "score": "2-1", "result": "HOME_WIN"},
        {"round": "R16", "home": "JPN", "away": "CRO", "score": "1-1(p)", "result": "AWAY_WIN"},  # 点球
        {"round": "R16", "home": "BRA", "away": "KOR", "score": "4-1", "result": "HOME_WIN"},
        {"round": "R16", "home": "ENG", "away": "SEN", "score": "3-0", "result": "HOME_WIN"},
        {"round": "R16", "home": "FRA", "away": "POL", "score": "3-1", "result": "HOME_WIN"},
        {"round": "R16", "home": "MAR", "away": "ESP", "score": "0-0(p)", "result": "HOME_WIN"},  # 大冷门！点球
        {"round": "R16", "home": "POR", "away": "SUI", "score": "6-1", "result": "HOME_WIN"},
        
        # 8强
        {"round": "QF", "home": "CRO", "away": "BRA", "score": "1-1(p)", "result": "HOME_WIN"},  # 冷门！点球
        {"round": "QF", "home": "NED", "away": "ARG", "score": "2-2(p)", "result": "AWAY_WIN"},  # 点球
        {"round": "QF", "home": "MAR", "away": "POR", "score": "1-0", "result": "HOME_WIN"},  # 大冷门！
        {"round": "QF", "home": "ENG", "away": "FRA", "score": "1-2", "result": "AWAY_WIN"},
        
        # 半决赛
        {"round": "SF", "home": "ARG", "away": "CRO", "score": "3-0", "result": "HOME_WIN"},
        {"round": "SF", "home": "FRA", "away": "MAR", "score": "2-0", "result": "HOME_WIN"},
        
        # 三四名
        {"round": "3RD", "home": "CRO", "away": "MAR", "score": "2-1", "result": "HOME_WIN"},
        
        # 决赛
        {"round": "FI", "home": "ARG", "away": "FRA", "score": "3-3(p)", "result": "HOME_WIN"},  # 点球
    ],
    
    # 冠军
    "champion": "ARG",
    
    # 关键冷门比赛
    "upsets": [
        {"match": "KSA-ARG", "desc": "沙特2-1阿根廷，世界杯最大冷门之一", "severity": 5},
        {"match": "JPN-GER", "desc": "日本2-1德国，亚洲球队再创奇迹", "severity": 5},
        {"match": "JPN-ESP", "desc": "日本2-1西班牙，小组第一出线", "severity": 4},
        {"match": "MAR-ESP", "desc": "摩洛哥点球淘汰西班牙，非洲之光", "severity": 5},
        {"match": "MAR-POR", "desc": "摩洛哥1-0葡萄牙，晋级四强", "severity": 5},
        {"match": "CRO-BRA", "desc": "克罗地亚点球淘汰巴西", "severity": 4},
    ]
}

# 2014巴西世界杯（额外数据）
WORLD_CUP_2014 = {
    "name": "2014 FIFA World Cup Brazil",
    "year": 2014,
    "host": "BRA",
    "champion": "GER",
    "runner_up": "ARG",
    
    # 关键冷门
    "upsets": [
        {"match": "BRA-GER", "desc": "德国7-1巴西，世界杯半决赛历史性惨案", "severity": 5},
        {"match": "CRC-URU", "desc": "哥斯达黎加3-1乌拉圭，小组赛开门红", "severity": 4},
        {"match": "CRC-ITA", "desc": "哥斯达黎加1-0意大利，小组出线", "severity": 4},
    ]
}


def get_all_world_cup_matches():
    """获取所有历史世界杯比赛数据"""
    matches = []
    
    for wc in [WORLD_CUP_2018, WORLD_CUP_2022]:
        # 小组赛
        for m in wc.get("group_stage", []):
            matches.append({
                "year": wc["year"],
                "stage": "GROUP",
                "group": m.get("group", ""),
                "home": m["home"],
                "away": m["away"],
                "result": m["result"]
            })
        
        # 淘汰赛
        for m in wc.get("knockout_stage", []):
            matches.append({
                "year": wc["year"],
                "stage": m["round"],
                "home": m["home"],
                "away": m["away"],
                "result": m["result"]
            })
    
    return matches


def get_world_cup_upsets(min_severity=3):
    """获取指定严重程度以上的冷门比赛"""
    upsets = []
    
    for wc in [WORLD_CUP_2018, WORLD_CUP_2022, WORLD_CUP_2014]:
        for upset in wc.get("upsets", []):
            if upset.get("severity", 0) >= min_severity:
                upsets.append({
                    "year": wc["year"],
                    "match": upset["match"],
                    "desc": upset["desc"],
                    "severity": upset["severity"]
                })
    
    return sorted(upsets, key=lambda x: -x["severity"])


def analyze_upset_patterns():
    """分析冷门规律"""
    # 统计冷门发生的场景
    patterns = {
        "champion_early_loss": 0,  # 卫冕冠军小组赛失利
        "asian_team_upset": 0,     # 亚洲球队爆冷
        "african_team_upset": 0,   # 非洲球队爆冷
        "knockout_upset": 0,       # 淘汰赛冷门
    }
    
    all_upsets = get_world_cup_upsets(min_severity=4)
    
    for upset in all_upsets:
        desc = upset["desc"].lower()
        
        if "卫冕" in desc or "冠军" in desc:
            patterns["champion_early_loss"] += 1
        if "日本" in desc or "韩国" in desc or "沙特" in desc:
            patterns["asian_team_upset"] += 1
        if "摩洛哥" in desc or "塞内加尔" in desc:
            patterns["african_team_upset"] += 1
        if "淘汰" in desc or "八强" in desc or "四强" in desc:
            patterns["knockout_upset"] += 1
    
    return patterns


# 统计数据
def get_world_cup_stats():
    """获取世界杯历史统计"""
    return {
        "total_matches_analyzed": len(get_all_world_cup_matches()),
        "total_upsets": len(get_world_cup_upsets()),
        "major_upsets": len(get_world_cup_upsets(min_severity=4)),
        "upset_patterns": analyze_upset_patterns(),
        
        # 各洲球队表现
        "champions_by_continent": {
            "SA": 5,   # 巴西5次，阿根廷3次，乌拉圭2次
            "EU": 12,  # 欧洲12次
        },
        
        # 东道主优势
        "host_advantage": {
            "champions": 6,  # 东道主夺冠6次
            "finals": 10,    # 进决赛10次
        }
    }