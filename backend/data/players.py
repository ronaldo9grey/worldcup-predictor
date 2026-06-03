"""
2026世界杯球员数据
包含各队核心球员、能力值、状态等信息
"""

# 球员数据结构
PLAYER_DATA = {
    # 阿根廷
    "ARG": {
        "squad": [
            {"name": "Lionel Messi", "name_cn": "梅西", "position": "FW", "rating": 93, "age": 38, "is_key": True, "form": "excellent"},
            {"name": "Julián Álvarez", "name_cn": "阿尔瓦雷斯", "position": "FW", "rating": 85, "age": 26, "is_key": True, "form": "good"},
            {"name": "Enzo Fernández", "name_cn": "恩佐", "position": "MF", "rating": 84, "age": 25, "is_key": True, "form": "good"},
            {"name": "Alexis Mac Allister", "name_cn": "麦卡利斯特", "position": "MF", "rating": 83, "age": 27, "is_key": True, "form": "good"},
            {"name": "Rodrigo De Paul", "name_cn": "德保罗", "position": "MF", "rating": 82, "age": 31, "is_key": False, "form": "average"},
            {"name": "Cristian Romero", "name_cn": "罗梅罗", "position": "DF", "rating": 83, "age": 27, "is_key": True, "form": "good"},
            {"name": "Nahuel Molina", "name_cn": "莫利纳", "position": "DF", "rating": 81, "age": 27, "is_key": False, "form": "good"},
            {"name": "Emiliano Martínez", "name_cn": "马丁内斯", "position": "GK", "rating": 88, "age": 33, "is_key": True, "form": "excellent"},
        ],
        "avg_rating": 85.0,
        "key_players_available": 6,
        "star_power": 95,  # 有超级巨星
    },
    
    # 法国
    "FRA": {
        "squad": [
            {"name": "Kylian Mbappé", "name_cn": "姆巴佩", "position": "FW", "rating": 91, "age": 27, "is_key": True, "form": "excellent"},
            {"name": "Antoine Griezmann", "name_cn": "格列兹曼", "position": "MF", "rating": 85, "age": 35, "is_key": True, "form": "good"},
            {"name": "Aurélien Tchouaméni", "name_cn": "楚阿梅尼", "position": "MF", "rating": 84, "age": 26, "is_key": True, "form": "good"},
            {"name": "Eduardo Camavinga", "name_cn": "卡马文加", "position": "MF", "rating": 83, "age": 23, "is_key": False, "form": "good"},
            {"name": "William Saliba", "name_cn": "萨利巴", "position": "DF", "rating": 84, "age": 25, "is_key": True, "form": "excellent"},
            {"name": "Dayot Upamecano", "name_cn": "于帕梅卡诺", "position": "DF", "rating": 81, "age": 27, "is_key": False, "form": "average"},
            {"name": "Mike Maignan", "name_cn": "迈尼昂", "position": "GK", "rating": 86, "age": 30, "is_key": True, "form": "good"},
        ],
        "avg_rating": 85.0,
        "key_players_available": 5,
        "star_power": 90,
    },
    
    # 巴西
    "BRA": {
        "squad": [
            {"name": "Vinícius Jr.", "name_cn": "维尼修斯", "position": "FW", "rating": 90, "age": 26, "is_key": True, "form": "excellent"},
            {"name": "Rodrygo", "name_cn": "罗德里戈", "position": "FW", "rating": 85, "age": 25, "is_key": True, "form": "good"},
            {"name": "Raphinha", "name_cn": "拉菲尼亚", "position": "FW", "rating": 83, "age": 29, "is_key": False, "form": "good"},
            {"name": "Bruno Guimarães", "name_cn": "吉马良斯", "position": "MF", "rating": 84, "age": 27, "is_key": True, "form": "good"},
            {"name": "Lucas Paquetá", "name_cn": "帕奎塔", "position": "MF", "rating": 83, "age": 28, "is_key": True, "form": "average"},
            {"name": "Marquinhos", "name_cn": "马尔基尼奥斯", "position": "DF", "rating": 86, "age": 32, "is_key": True, "form": "good"},
            {"name": "Alisson", "name_cn": "阿利松", "position": "GK", "rating": 88, "age": 33, "is_key": True, "form": "excellent"},
        ],
        "avg_rating": 85.5,
        "key_players_available": 6,
        "star_power": 88,
    },
    
    # 德国
    "GER": {
        "squad": [
            {"name": "Jamal Musiala", "name_cn": "穆西亚拉", "position": "MF", "rating": 87, "age": 23, "is_key": True, "form": "excellent"},
            {"name": "Florian Wirtz", "name_cn": "维尔茨", "position": "MF", "rating": 86, "age": 22, "is_key": True, "form": "excellent"},
            {"name": "Kai Havertz", "name_cn": "哈弗茨", "position": "FW", "rating": 84, "age": 26, "is_key": True, "form": "good"},
            {"name": "Joshua Kimmich", "name_cn": "基米希", "position": "MF", "rating": 86, "age": 31, "is_key": True, "form": "good"},
            {"name": "Antonio Rüdiger", "name_cn": "吕迪格", "position": "DF", "rating": 84, "age": 33, "is_key": True, "form": "good"},
            {"name": "Manuel Neuer", "name_cn": "诺伊尔", "position": "GK", "rating": 87, "age": 40, "is_key": True, "form": "good"},
        ],
        "avg_rating": 85.0,
        "key_players_available": 6,
        "star_power": 82,
    },
    
    # 英格兰
    "ENG": {
        "squad": [
            {"name": "Harry Kane", "name_cn": "凯恩", "position": "FW", "rating": 88, "age": 32, "is_key": True, "form": "excellent"},
            {"name": "Jude Bellingham", "name_cn": "贝林厄姆", "position": "MF", "rating": 89, "age": 22, "is_key": True, "form": "excellent"},
            {"name": "Phil Foden", "name_cn": "福登", "position": "FW", "rating": 87, "age": 26, "is_key": True, "form": "good"},
            {"name": "Declan Rice", "name_cn": "赖斯", "position": "MF", "rating": 85, "age": 27, "is_key": True, "form": "good"},
            {"name": "John Stones", "name_cn": "斯通斯", "position": "DF", "rating": 84, "age": 32, "is_key": True, "form": "good"},
            {"name": "Jordan Pickford", "name_cn": "皮克福德", "position": "GK", "rating": 83, "age": 31, "is_key": False, "form": "good"},
        ],
        "avg_rating": 85.5,
        "key_players_available": 5,
        "star_power": 88,
    },
    
    # 西班牙
    "ESP": {
        "squad": [
            {"name": "Pedri", "name_cn": "佩德里", "position": "MF", "rating": 88, "age": 23, "is_key": True, "form": "excellent"},
            {"name": "Gavi", "name_cn": "加维", "position": "MF", "rating": 85, "age": 22, "is_key": True, "form": "good"},
            {"name": "Lamine Yamal", "name_cn": "亚马尔", "position": "FW", "rating": 84, "age": 18, "is_key": True, "form": "excellent"},
            {"name": "Rodri", "name_cn": "罗德里", "position": "MF", "rating": 89, "age": 29, "is_key": True, "form": "excellent"},
            {"name": "Aymeric Laporte", "name_cn": "拉波尔特", "position": "DF", "rating": 83, "age": 31, "is_key": False, "form": "good"},
            {"name": "Unai Simón", "name_cn": "西蒙", "position": "GK", "rating": 83, "age": 27, "is_key": False, "form": "good"},
        ],
        "avg_rating": 85.0,
        "key_players_available": 4,
        "star_power": 85,
    },
    
    # 葡萄牙
    "POR": {
        "squad": [
            {"name": "Rafael Leão", "name_cn": "莱奥", "position": "FW", "rating": 87, "age": 27, "is_key": True, "form": "good"},
            {"name": "Bruno Fernandes", "name_cn": "布鲁诺", "position": "MF", "rating": 86, "age": 31, "is_key": True, "form": "good"},
            {"name": "Bernardo Silva", "name_cn": "伯纳多", "position": "MF", "rating": 87, "age": 30, "is_key": True, "form": "good"},
            {"name": "Rúben Dias", "name_cn": "鲁本·迪亚斯", "position": "DF", "rating": 86, "age": 27, "is_key": True, "form": "excellent"},
            {"name": "Diogo Costa", "name_cn": "科斯塔", "position": "GK", "rating": 84, "age": 26, "is_key": False, "form": "good"},
        ],
        "avg_rating": 84.5,
        "key_players_available": 4,
        "star_power": 80,
    },
    
    # 荷兰
    "NED": {
        "squad": [
            {"name": "Cody Gakpo", "name_cn": "加克波", "position": "FW", "rating": 85, "age": 27, "is_key": True, "form": "good"},
            {"name": "Frenkie de Jong", "name_cn": "德容", "position": "MF", "rating": 87, "age": 29, "is_key": True, "form": "good"},
            {"name": "Virgil van Dijk", "name_cn": "范迪克", "position": "DF", "rating": 88, "age": 34, "is_key": True, "form": "good"},
            {"name": "Nathan Aké", "name_cn": "阿克", "position": "DF", "rating": 83, "age": 31, "is_key": False, "form": "good"},
        ],
        "avg_rating": 84.0,
        "key_players_available": 3,
        "star_power": 78,
    },
    
    # 美国
    "USA": {
        "squad": [
            {"name": "Christian Pulisic", "name_cn": "普利西奇", "position": "FW", "rating": 82, "age": 27, "is_key": True, "form": "good"},
            {"name": "Giovanni Reyna", "name_cn": "雷纳", "position": "MF", "rating": 80, "age": 23, "is_key": True, "form": "average"},
            {"name": "Weston McKennie", "name_cn": "麦肯尼", "position": "MF", "rating": 79, "age": 27, "is_key": False, "form": "good"},
            {"name": "Matt Turner", "name_cn": "特纳", "position": "GK", "rating": 78, "age": 30, "is_key": False, "form": "average"},
        ],
        "avg_rating": 79.0,
        "key_players_available": 2,
        "star_power": 45,
    },
    
    # 墨西哥
    "MEX": {
        "squad": [
            {"name": "Hirving Lozano", "name_cn": "洛萨诺", "position": "FW", "rating": 81, "age": 30, "is_key": True, "form": "good"},
            {"name": "Edson Álvarez", "name_cn": "埃德松", "position": "MF", "rating": 80, "age": 28, "is_key": True, "form": "good"},
        ],
        "avg_rating": 78.0,
        "key_players_available": 2,
        "star_power": 40,
    },
}


def get_team_squad(team_code: str) -> dict:
    """获取球队阵容数据"""
    return PLAYER_DATA.get(team_code, {
        "squad": [],
        "avg_rating": 75.0,
        "key_players_available": 0,
        "star_power": 20
    })


def get_squad_strength(team_code: str) -> float:
    """计算球队阵容强度 (0-100)"""
    data = PLAYER_DATA.get(team_code, {})
    if not data.get("squad"):
        return 50.0
    
    avg_rating = data.get("avg_rating", 75)
    key_players = data.get("key_players_available", 0)
    star_power = data.get("star_power", 50)
    
    # 综合评分：平均能力60% + 核心球员20% + 明星效应20%
    strength = (avg_rating - 70) * 3 + key_players * 2 + star_power * 0.2
    return max(0, min(100, strength))


def compare_squads(home_code: str, away_code: str) -> dict:
    """比较两队阵容实力"""
    home_strength = get_squad_strength(home_code)
    away_strength = get_squad_strength(away_code)
    
    return {
        "home_strength": round(home_strength, 1),
        "away_strength": round(away_strength, 1),
        "strength_diff": round(home_strength - away_strength, 1),
        "advantage": "home" if home_strength > away_strength + 10 else "away" if away_strength > home_strength + 10 else "even",
        "home_squad": get_team_squad(home_code),
        "away_squad": get_team_squad(away_code)
    }
