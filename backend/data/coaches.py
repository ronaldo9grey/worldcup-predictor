"""
2026世界杯教练数据
包含各队主教练信息、执教能力、战术风格等
"""

COACH_DATA = {
    # 阿根廷
    "ARG": {
        "name": "Lionel Scaloni",
        "name_cn": "斯卡洛尼",
        "country": "ARG",
        "age": 47,
        "experience_years": 8,
        "wc_titles": 1,  # 2022世界杯冠军
        "major_titles": 3,  # 世界杯+美洲杯
        "style": "balanced",  # 战术风格：balanced/attacking/defensive
        "win_rate": 72.5,
        "tactics_rating": 85,  # 战术能力 (0-100)
        "motivation_rating": 88,  # 激励能力
        "finals_experience": 3,  # 决赛经验场次
        "adaptability": 90,  # 临场调整能力
    },
    
    # 法国
    "FRA": {
        "name": "Didier Deschamps",
        "name_cn": "德尚",
        "country": "FRA",
        "age": 58,
        "experience_years": 20,
        "wc_titles": 1,  # 2018世界杯冠军
        "major_titles": 5,
        "style": "pragmatic",  # 务实风格
        "win_rate": 68.0,
        "tactics_rating": 82,
        "motivation_rating": 85,
        "finals_experience": 5,
        "adaptability": 88,
    },
    
    # 巴西
    "BRA": {
        "name": "Dorival Júnior",
        "name_cn": "多里瓦尔",
        "country": "BRA",
        "age": 62,
        "experience_years": 25,
        "wc_titles": 0,
        "major_titles": 2,
        "style": "attacking",
        "win_rate": 52.0,
        "tactics_rating": 75,
        "motivation_rating": 78,
        "finals_experience": 1,
        "adaptability": 70,
    },
    
    # 德国
    "GER": {
        "name": "Julian Nagelsmann",
        "name_cn": "纳格尔斯曼",
        "country": "GER",
        "age": 38,
        "experience_years": 8,
        "wc_titles": 0,
        "major_titles": 0,
        "style": "attacking",
        "win_rate": 65.0,
        "tactics_rating": 88,  # 年轻战术大师
        "motivation_rating": 75,
        "finals_experience": 0,
        "adaptability": 92,
    },
    
    # 英格兰
    "ENG": {
        "name": "Thomas Tuchel",
        "name_cn": "图赫尔",
        "country": "GER",
        "age": 51,
        "experience_years": 15,
        "wc_titles": 0,
        "major_titles": 3,  # 欧冠等
        "style": "flexible",
        "win_rate": 62.0,
        "tactics_rating": 90,
        "motivation_rating": 80,
        "finals_experience": 3,
        "adaptability": 95,
    },
    
    # 西班牙
    "ESP": {
        "name": "Luis de la Fuente",
        "name_cn": "德拉富恩特",
        "country": "ESP",
        "age": 63,
        "experience_years": 15,
        "wc_titles": 0,
        "major_titles": 2,  # 欧洲杯+欧国联
        "style": "possession",  # 控球风格
        "win_rate": 70.0,
        "tactics_rating": 82,
        "motivation_rating": 85,
        "finals_experience": 2,
        "adaptability": 80,
    },
    
    # 葡萄牙
    "POR": {
        "name": "Roberto Martínez",
        "name_cn": "马丁内斯",
        "country": "ESP",
        "age": 51,
        "experience_years": 12,
        "wc_titles": 0,
        "major_titles": 0,
        "style": "balanced",
        "win_rate": 65.0,
        "tactics_rating": 78,
        "motivation_rating": 80,
        "finals_experience": 0,
        "adaptability": 75,
    },
    
    # 荷兰
    "NED": {
        "name": "Ronald Koeman",
        "name_cn": "科曼",
        "country": "NED",
        "age": 61,
        "experience_years": 20,
        "wc_titles": 0,
        "major_titles": 2,
        "style": "attacking",
        "win_rate": 55.0,
        "tactics_rating": 78,
        "motivation_rating": 75,
        "finals_experience": 1,
        "adaptability": 72,
    },
    
    # 美国
    "USA": {
        "name": "Mauricio Pochettino",
        "name_cn": "波切蒂诺",
        "country": "ARG",
        "age": 53,
        "experience_years": 15,
        "wc_titles": 0,
        "major_titles": 0,
        "style": "pressing",  # 高压逼抢
        "win_rate": 52.0,
        "tactics_rating": 80,
        "motivation_rating": 82,
        "finals_experience": 1,
        "adaptability": 78,
    },
    
    # 墨西哥
    "MEX": {
        "name": "Jaime Lozano",
        "name_cn": "海梅·洛萨诺",
        "country": "MEX",
        "age": 46,
        "experience_years": 8,
        "wc_titles": 0,
        "major_titles": 0,
        "style": "counter-attack",
        "win_rate": 48.0,
        "tactics_rating": 72,
        "motivation_rating": 78,
        "finals_experience": 0,
        "adaptability": 70,
    },
}


def get_coach_info(team_code: str) -> dict:
    """获取球队教练信息"""
    default_coach = {
        "name": "Unknown",
        "name_cn": "未知",
        "country": team_code,
        "age": 50,
        "experience_years": 5,
        "wc_titles": 0,
        "major_titles": 0,
        "style": "balanced",
        "win_rate": 40.0,
        "tactics_rating": 60,
        "motivation_rating": 65,
        "finals_experience": 0,
        "adaptability": 65,
    }
    return COACH_DATA.get(team_code, default_coach)


def calculate_coach_rating(team_code: str) -> float:
    """计算教练综合能力 (0-100)"""
    coach = get_coach_info(team_code)
    
    # 综合评分：战术30% + 激励25% + 胜率20% + 决赛经验15% + 调整能力10%
    rating = (
        coach["tactics_rating"] * 0.30 +
        coach["motivation_rating"] * 0.25 +
        coach["win_rate"] * 0.20 +
        min(100, coach["finals_experience"] * 15) * 0.15 +
        coach["adaptability"] * 0.10
    )
    
    return round(rating, 1)


def compare_coaches(home_code: str, away_code: str) -> dict:
    """比较两队教练能力"""
    home_coach = get_coach_info(home_code)
    away_coach = get_coach_info(away_code)
    
    home_rating = calculate_coach_rating(home_code)
    away_rating = calculate_coach_rating(away_code)
    
    return {
        "home_coach": home_coach,
        "away_coach": away_coach,
        "home_rating": home_rating,
        "away_rating": away_rating,
        "rating_diff": round(home_rating - away_rating, 1),
        "advantage": "home" if home_rating > away_rating + 5 else "away" if away_rating > home_rating + 5 else "even",
        "analysis": get_coach_matchup_analysis(home_code, away_code)
    }


def get_coach_matchup_analysis(home_code: str, away_code: str) -> str:
    """分析教练对决"""
    home = get_coach_info(home_code)
    away = get_coach_info(away_code)
    
    home_rating = calculate_coach_rating(home_code)
    away_rating = calculate_coach_rating(away_code)
    
    if home_rating > away_rating + 10:
        return f"{home['name_cn']}执教经验丰富，大赛成绩优异，明显占优"
    elif home_rating > away_rating + 5:
        return f"{home['name_cn']}综合能力略胜一筹"
    elif away_rating > home_rating + 10:
        return f"{away['name_cn']}执教经验丰富，大赛成绩优异，明显占优"
    elif away_rating > home_rating + 5:
        return f"{away['name_cn']}综合能力略胜一筹"
    else:
        return "两位教练水平相当，临场指挥成关键"
