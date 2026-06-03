"""
2026世界杯场地和天气数据
包含比赛城市、场馆信息、天气预测等

2026世界杯将在美国、加拿大、墨西哥三国举办
"""

# 比赛城市和场馆
VENUE_DATA = {
    # 美国场馆
    "atlanta": {
        "city": "Atlanta",
        "city_cn": "亚特兰大",
        "country": "USA",
        "stadium": "Mercedes-Benz Stadium",
        "stadium_cn": "梅赛德斯奔驰球场",
        "capacity": 70000,
        "altitude": 320,  # 海拔(米)
        "climate": "humid_subtropical",  # 亚热带湿润气候
        "avg_temp_june": 27,  # 6月平均气温
        "avg_humidity": 65,
        "is_air_conditioned": True,
    },
    
    "dallas": {
        "city": "Dallas",
        "city_cn": "达拉斯",
        "country": "USA",
        "stadium": "AT&T Stadium",
        "stadium_cn": "AT&T球场",
        "capacity": 80000,
        "altitude": 150,
        "climate": "humid_subtropical",
        "avg_temp_june": 30,
        "avg_humidity": 60,
        "is_air_conditioned": True,
    },
    
    "los_angeles": {
        "city": "Los Angeles",
        "city_cn": "洛杉矶",
        "country": "USA",
        "stadium": "SoFi Stadium",
        "stadium_cn": "SoFi球场",
        "capacity": 70000,
        "altitude": 90,
        "climate": "mediterranean",  # 地中海气候
        "avg_temp_june": 22,
        "avg_humidity": 50,
        "is_air_conditioned": True,
    },
    
    "new_york": {
        "city": "New York",
        "city_cn": "纽约",
        "country": "USA",
        "stadium": "MetLife Stadium",
        "stadium_cn": "大都会球场",
        "capacity": 82500,
        "altitude": 10,
        "climate": "humid_subtropical",
        "avg_temp_june": 24,
        "avg_humidity": 70,
        "is_air_conditioned": False,
    },
    
    "miami": {
        "city": "Miami",
        "city_cn": "迈阿密",
        "country": "USA",
        "stadium": "Hard Rock Stadium",
        "stadium_cn": "硬石球场",
        "capacity": 65000,
        "altitude": 2,
        "climate": "tropical",
        "avg_temp_june": 28,
        "avg_humidity": 75,
        "is_air_conditioned": False,
    },
    
    "seattle": {
        "city": "Seattle",
        "city_cn": "西雅图",
        "country": "USA",
        "stadium": "Lumen Field",
        "stadium_cn": "流明球场",
        "capacity": 69000,
        "altitude": 50,
        "climate": "marine",  # 海洋性气候
        "avg_temp_june": 18,
        "avg_humidity": 65,
        "is_air_conditioned": False,
    },
    
    # 加拿大场馆
    "toronto": {
        "city": "Toronto",
        "city_cn": "多伦多",
        "country": "CAN",
        "stadium": "BMO Field",
        "stadium_cn": "BMO球场",
        "capacity": 45000,
        "altitude": 76,
        "climate": "continental",  # 大陆性气候
        "avg_temp_june": 21,
        "avg_humidity": 60,
        "is_air_conditioned": False,
    },
    
    "vancouver": {
        "city": "Vancouver",
        "city_cn": "温哥华",
        "country": "CAN",
        "stadium": "BC Place",
        "stadium_cn": "BC广场",
        "capacity": 54000,
        "altitude": 50,
        "climate": "marine",
        "avg_temp_june": 17,
        "avg_humidity": 65,
        "is_air_conditioned": False,
    },
    
    # 墨西哥场馆
    "mexico_city": {
        "city": "Mexico City",
        "city_cn": "墨西哥城",
        "country": "MEX",
        "stadium": "Estadio Azteca",
        "stadium_cn": "阿兹特克球场",
        "capacity": 83000,
        "altitude": 2240,  # 高海拔！
        "climate": "highland",  # 高原气候
        "avg_temp_june": 20,
        "avg_humidity": 50,
        "is_air_conditioned": False,
    },
    
    "guadalajara": {
        "city": "Guadalajara",
        "city_cn": "瓜达拉哈拉",
        "country": "MEX",
        "stadium": "Estadio Akron",
        "stadium_cn": "阿克龙球场",
        "capacity": 46000,
        "altitude": 1550,
        "climate": "highland",
        "avg_temp_june": 24,
        "avg_humidity": 45,
        "is_air_conditioned": False,
    },
    
    "monterrey": {
        "city": "Monterrey",
        "city_cn": "蒙特雷",
        "country": "MEX",
        "stadium": "Estadio BBVA",
        "stadium_cn": "BBVA球场",
        "capacity": 51000,
        "altitude": 540,
        "climate": "semi_arid",  # 半干旱气候
        "avg_temp_june": 32,
        "avg_humidity": 40,
        "is_air_conditioned": False,
    },
}


# 小组赛分配场馆（2026世界杯48队，12组）
GROUP_VENUES = {
    # A组：墨西哥城、瓜达拉哈拉（墨西哥主场优势）
    "A": ["mexico_city", "guadalajara"],
    
    # B组：达拉斯、亚特兰大（美国南部）
    "B": ["dallas", "atlanta"],
    
    # C组：洛杉矶、西雅图（美国西部）
    "C": ["los_angeles", "seattle"],
    
    # D组：纽约、多伦多（北美东部）
    "D": ["new_york", "toronto"],
    
    # E组：迈阿密、亚特兰大（美国东南）
    "E": ["miami", "atlanta"],
    
    # F组：温哥华、西雅图（北美西北）
    "F": ["vancouver", "seattle"],
    
    # G组：达拉斯、墨西哥城（中部）
    "G": ["dallas", "mexico_city"],
    
    # H组：洛杉矶、蒙特雷（西部-北部）
    "H": ["los_angeles", "monterrey"],
    
    # I组：纽约、多伦多（东部）
    "I": ["new_york", "toronto"],
    
    # J组：迈阿密、瓜达拉哈拉（东南-中部）
    "J": ["miami", "guadalajara"],
    
    # K组：亚特兰大、温哥华（东南-西北）
    "K": ["atlanta", "vancouver"],
    
    # L组：达拉斯、洛杉矶（南部-西部）
    "L": ["dallas", "los_angeles"],
}


def get_match_venue(group: str, match_index: int) -> dict:
    """获取比赛场馆信息"""
    venues = GROUP_VENUES.get(group.upper(), ["atlanta"])
    venue_key = venues[match_index % len(venues)]
    return VENUE_DATA.get(venue_key, VENUE_DATA["atlanta"])


def calculate_weather_impact(venue: dict) -> dict:
    """计算天气对比赛的影响"""
    temp = venue.get("avg_temp_june", 25)
    humidity = venue.get("avg_humidity", 60)
    altitude = venue.get("altitude", 100)
    
    # 高温影响：超过30°C，球员体能消耗增加
    temp_impact = 0 if temp < 25 else min(1, (temp - 25) / 10)
    
    # 高湿度影响：超过70%，球员体感温度更高
    humidity_impact = 0 if humidity < 60 else min(1, (humidity - 60) / 20)
    
    # 高海拔影响：超过1500米，对不适应高原的球队不利
    altitude_impact = 0 if altitude < 1000 else min(1, (altitude - 1000) / 1500)
    
    return {
        "temperature": {
            "value": temp,
            "unit": "°C",
            "impact": round(temp_impact, 2),
            "meaning": "适宜" if temp < 25 else "较热" if temp < 30 else "炎热"
        },
        "humidity": {
            "value": humidity,
            "unit": "%",
            "impact": round(humidity_impact, 2),
            "meaning": "舒适" if humidity < 60 else "潮湿" if humidity < 70 else "闷热"
        },
        "altitude": {
            "value": altitude,
            "unit": "m",
            "impact": round(altitude_impact, 2),
            "meaning": "平原" if altitude < 500 else "低高原" if altitude < 1500 else "高原"
        },
        "total_impact": round((temp_impact + humidity_impact + altitude_impact) / 3, 2),
        "is_air_conditioned": venue.get("is_air_conditioned", False)
    }


def get_home_advantage_from_venue(group: str, team_code: str) -> float:
    """根据场地计算主场优势"""
    venue = get_match_venue(group, 0)
    
    # 东道主优势
    host_countries = ["USA", "CAN", "MEX"]
    team_country = get_team_country(team_code)
    
    if venue["country"] == team_country:
        # 主场优势：15-25%
        return 0.20
    elif venue["country"] in host_countries and team_country in host_countries:
        # 同为东道主：5-10%
        return 0.08
    else:
        # 无主场优势
        return 0.0


def get_team_country(team_code: str) -> str:
    """根据球队代码获取所属国家"""
    # 简化映射
    country_map = {
        "USA": "USA", "MEX": "MEX", "CAN": "CAN",
        "ARG": "ARG", "BRA": "BRA", "COL": "COL",
        "FRA": "FRA", "GER": "GER", "ENG": "ENG",
        "ESP": "ESP", "POR": "POR", "NED": "NED",
    }
    return country_map.get(team_code, "OTHER")


def get_venue_factor_for_match(group: str, home_code: str, away_code: str) -> dict:
    """获取比赛场地因素"""
    venue = get_match_venue(group, 0)
    weather = calculate_weather_impact(venue)
    home_advantage = get_home_advantage_from_venue(group, home_code)
    
    # 分析高原优势（墨西哥主场）
    altitude_factor = 0
    if venue["altitude"] > 1500:
        # 墨西哥球队适应高原，其他球队不适应
        home_country = get_team_country(home_code)
        if home_country == "MEX":
            altitude_factor = 0.10
        elif get_team_country(away_code) != "MEX":
            altitude_factor = -0.05  # 客队不利
    
    return {
        "venue": venue,
        "weather": weather,
        "home_advantage": round(home_advantage + altitude_factor, 2),
        "altitude_factor": round(altitude_factor, 2),
        "analysis": get_venue_analysis(venue, home_code, away_code)
    }


def get_venue_analysis(venue: dict, home_code: str, away_code: str) -> str:
    """场地分析"""
    altitude = venue.get("altitude", 100)
    temp = venue.get("avg_temp_june", 25)
    
    analyses = []
    
    if altitude > 1500:
        analyses.append(f"高海拔球场({altitude}米)，对不适应高原的球队不利")
    
    if temp > 30:
        analyses.append(f"气温较高({temp}°C)，体能消耗大")
    
    if not venue.get("is_air_conditioned"):
        analyses.append("露天球场，受天气影响")
    
    return " | ".join(analyses) if analyses else "场地条件适宜，无明显影响"