# 2026世界杯参赛队伍数据
# 48支球队，按大洲分布（基于预选赛情况和预测）

# ========== 球队基础数据 ==========
ALL_TEAMS = [
    # ========== 亚洲区 (8.5个名额) ==========
    {"code": "JPN", "name": "Japan", "name_cn": "日本", "rank": 18, "elo": 1650, "continent": "AS", "form": "WDWDL", "wc_titles": 0},
    {"code": "IRN", "name": "Iran", "name_cn": "伊朗", "rank": 19, "elo": 1620, "continent": "AS", "form": "WWWDL", "wc_titles": 0},
    {"code": "KOR", "name": "South Korea", "name_cn": "韩国", "rank": 22, "elo": 1580, "continent": "AS", "form": "WDWWL", "wc_titles": 0},
    {"code": "AUS", "name": "Australia", "name_cn": "澳大利亚", "rank": 24, "elo": 1560, "continent": "AS", "form": "WDWDW", "wc_titles": 0},
    {"code": "SAU", "name": "Saudi Arabia", "name_cn": "沙特", "rank": 53, "elo": 1520, "continent": "AS", "form": "LDWLL", "wc_titles": 0},
    {"code": "UZB", "name": "Uzbekistan", "name_cn": "乌兹别克斯坦", "rank": 58, "elo": 1490, "continent": "AS", "form": "WDWWD", "wc_titles": 0},
    {"code": "JOR", "name": "Jordan", "name_cn": "约旦", "rank": 71, "elo": 1450, "continent": "AS", "form": "WDLDW", "wc_titles": 0},
    {"code": "IRQ", "name": "Iraq", "name_cn": "伊拉克", "rank": 55, "elo": 1500, "continent": "AS", "form": "DWLWD", "wc_titles": 0},
    {"code": "QAT", "name": "Qatar", "name_cn": "卡塔尔", "rank": 48, "elo": 1530, "continent": "AS", "form": "WDLWD", "wc_titles": 0},
    
    # ========== 欧洲区 (16个名额) ==========
    {"code": "FRA", "name": "France", "name_cn": "法国", "rank": 2, "elo": 1870, "continent": "EU", "form": "WWWWD", "wc_titles": 2},
    {"code": "ENG", "name": "England", "name_cn": "英格兰", "rank": 4, "elo": 1810, "continent": "EU", "form": "WDWWD", "wc_titles": 1},
    {"code": "GER", "name": "Germany", "name_cn": "德国", "rank": 12, "elo": 1740, "continent": "EU", "form": "WDLDW", "wc_titles": 4},
    {"code": "ESP", "name": "Spain", "name_cn": "西班牙", "rank": 8, "elo": 1770, "continent": "EU", "form": "WDWDL", "wc_titles": 1},
    {"code": "POR", "name": "Portugal", "name_cn": "葡萄牙", "rank": 6, "elo": 1790, "continent": "EU", "form": "WWWDW", "wc_titles": 0},
    {"code": "NED", "name": "Netherlands", "name_cn": "荷兰", "rank": 7, "elo": 1780, "continent": "EU", "form": "WDWWD", "wc_titles": 0},
    {"code": "BEL", "name": "Belgium", "name_cn": "比利时", "rank": 3, "elo": 1820, "continent": "EU", "form": "WDWDL", "wc_titles": 0},
    {"code": "CRO", "name": "Croatia", "name_cn": "克罗地亚", "rank": 10, "elo": 1750, "continent": "EU", "form": "DWLWD", "wc_titles": 0},
    {"code": "SUI", "name": "Switzerland", "name_cn": "瑞士", "rank": 14, "elo": 1700, "continent": "EU", "form": "WDWDL", "wc_titles": 0},
    {"code": "DEN", "name": "Denmark", "name_cn": "丹麦", "rank": 21, "elo": 1590, "continent": "EU", "form": "DLWWD", "wc_titles": 0},
    {"code": "AUT", "name": "Austria", "name_cn": "奥地利", "rank": 25, "elo": 1550, "continent": "EU", "form": "WDWDL", "wc_titles": 0},
    {"code": "TUR", "name": "Turkey", "name_cn": "土耳其", "rank": 28, "elo": 1530, "continent": "EU", "form": "WWDLD", "wc_titles": 0},
    {"code": "POL", "name": "Poland", "name_cn": "波兰", "rank": 30, "elo": 1520, "continent": "EU", "form": "WDLDW", "wc_titles": 0},
    {"code": "SRB", "name": "Serbia", "name_cn": "塞尔维亚", "rank": 33, "elo": 1500, "continent": "EU", "form": "LDWDL", "wc_titles": 0},
    {"code": "BIH", "name": "Bosnia and Herzegovina", "name_cn": "波黑", "rank": 57, "elo": 1495, "continent": "EU", "form": "WDLDW", "wc_titles": 0},
    {"code": "NOR", "name": "Norway", "name_cn": "挪威", "rank": 43, "elo": 1470, "continent": "EU", "form": "WDLWD", "wc_titles": 0},
    {"code": "SWE", "name": "Sweden", "name_cn": "瑞典", "rank": 26, "elo": 1540, "continent": "EU", "form": "DLDLW", "wc_titles": 0},
    {"code": "CZE", "name": "Czech Republic", "name_cn": "捷克", "rank": 32, "elo": 1510, "continent": "EU", "form": "WDWDL", "wc_titles": 0},
    {"code": "SCO", "name": "Scotland", "name_cn": "苏格兰", "rank": 39, "elo": 1480, "continent": "EU", "form": "LDWDW", "wc_titles": 0},
    
    # ========== 南美区 (6个名额) ==========
    {"code": "ARG", "name": "Argentina", "name_cn": "阿根廷", "rank": 1, "elo": 1885, "continent": "SA", "form": "WDWWL", "wc_titles": 3},
    {"code": "BRA", "name": "Brazil", "name_cn": "巴西", "rank": 5, "elo": 1830, "continent": "SA", "form": "WDWDL", "wc_titles": 5},
    {"code": "COL", "name": "Colombia", "name_cn": "哥伦比亚", "rank": 15, "elo": 1690, "continent": "SA", "form": "WDWWD", "wc_titles": 0},
    {"code": "URU", "name": "Uruguay", "name_cn": "乌拉圭", "rank": 17, "elo": 1660, "continent": "SA", "form": "WDLWD", "wc_titles": 2},
    {"code": "ECU", "name": "Ecuador", "name_cn": "厄瓜多尔", "rank": 35, "elo": 1480, "continent": "SA", "form": "DWLWD", "wc_titles": 0},
    {"code": "PAR", "name": "Paraguay", "name_cn": "巴拉圭", "rank": 50, "elo": 1445, "continent": "SA", "form": "LDLDW", "wc_titles": 0},
    
    # ========== 北中美及加勒比海地区 (6个名额) ==========
    {"code": "USA", "name": "USA", "name_cn": "美国", "rank": 13, "elo": 1745, "continent": "NA", "form": "WDLWW", "wc_titles": 0},
    {"code": "MEX", "name": "Mexico", "name_cn": "墨西哥", "rank": 16, "elo": 1680, "continent": "NA", "form": "WDLDW", "wc_titles": 0},
    {"code": "CAN", "name": "Canada", "name_cn": "加拿大", "rank": 47, "elo": 1410, "continent": "NA", "form": "WDLWL", "wc_titles": 0},
    {"code": "PAN", "name": "Panama", "name_cn": "巴拿马", "rank": 45, "elo": 1430, "continent": "NA", "form": "DLWDW", "wc_titles": 0},
    {"code": "CRC", "name": "Costa Rica", "name_cn": "哥斯达黎加", "rank": 54, "elo": 1440, "continent": "NA", "form": "WDLDL", "wc_titles": 0},
    {"code": "HTI", "name": "Haiti", "name_cn": "海地", "rank": 85, "elo": 1280, "continent": "NA", "form": "LDLWD", "wc_titles": 0},
    
    # ========== 非洲区 (9个名额) ==========
    {"code": "MAR", "name": "Morocco", "name_cn": "摩洛哥", "rank": 13, "elo": 1740, "continent": "AF", "form": "WWWDW", "wc_titles": 0},
    {"code": "SEN", "name": "Senegal", "name_cn": "塞内加尔", "rank": 20, "elo": 1600, "continent": "AF", "form": "WDWWD", "wc_titles": 0},
    {"code": "NGA", "name": "Nigeria", "name_cn": "尼日利亚", "rank": 40, "elo": 1460, "continent": "AF", "form": "WDLWD", "wc_titles": 0},
    {"code": "CIV", "name": "Cote d'Ivoire", "name_cn": "科特迪瓦", "rank": 42, "elo": 1450, "continent": "AF", "form": "WDLDW", "wc_titles": 0},
    {"code": "CMR", "name": "Cameroon", "name_cn": "喀麦隆", "rank": 38, "elo": 1470, "continent": "AF", "form": "DLWLD", "wc_titles": 0},
    {"code": "GHA", "name": "Ghana", "name_cn": "加纳", "rank": 61, "elo": 1390, "continent": "AF", "form": "WDLDL", "wc_titles": 0},
    {"code": "EGY", "name": "Egypt", "name_cn": "埃及", "rank": 36, "elo": 1480, "continent": "AF", "form": "WDLWD", "wc_titles": 0},
    {"code": "COD", "name": "DR Congo", "name_cn": "民主刚果", "rank": 59, "elo": 1400, "continent": "AF", "form": "LDWWD", "wc_titles": 0},
    {"code": "ALG", "name": "Algeria", "name_cn": "阿尔及利亚", "rank": 34, "elo": 1490, "continent": "AF", "form": "WDWDL", "wc_titles": 0},
    {"code": "TUN", "name": "Tunisia", "name_cn": "突尼斯", "rank": 29, "elo": 1520, "continent": "AF", "form": "DWDLD", "wc_titles": 0},
    
    # ========== 大洋洲区 (1个名额) ==========
    {"code": "NZL", "name": "New Zealand", "name_cn": "新西兰", "rank": 94, "elo": 1260, "continent": "OC", "form": "WDWDW", "wc_titles": 0},
    
    # ========== 其他 ==========
    {"code": "CPV", "name": "Cape Verde", "name_cn": "佛得角", "rank": 65, "elo": 1370, "continent": "AF", "form": "WDLDL", "wc_titles": 0},
    {"code": "CUR", "name": "Curacao", "name_cn": "库拉索", "rank": 80, "elo": 1300, "continent": "NA", "form": "DWLWD", "wc_titles": 0},
    {"code": "ZAF", "name": "South Africa", "name_cn": "南非", "rank": 60, "elo": 1395, "continent": "AF", "form": "LDWDW", "wc_titles": 0},
]


# ========== 正确的分组信息（2026世界杯抽签结果）==========
GROUPS = {
    "A": ["MEX", "ZAF", "KOR", "CZE"],  # 墨西哥、南非、韩国、捷克
    "B": ["CAN", "BIH", "QAT", "SUI"],  # 加拿大、波黑、卡塔尔、瑞士
    "C": ["BRA", "MAR", "HTI", "SCO"],  # 巴西、摩洛哥、海地、苏格兰
    "D": ["USA", "PAR", "AUS", "TUR"],  # 美国、巴拉圭、澳大利亚、土耳其
    "E": ["GER", "CUR", "CIV", "ECU"],  # 德国、库拉索、科特迪瓦、厄瓜多尔
    "F": ["NED", "JPN", "SWE", "TUN"],  # 荷兰、日本、瑞典、突尼斯
    "G": ["BEL", "EGY", "IRN", "NZL"],  # 比利时、埃及、伊朗、新西兰
    "H": ["ESP", "CPV", "SAU", "URU"],  # 西班牙、佛得角、沙特、乌拉圭
    "I": ["FRA", "SEN", "IRQ", "NOR"],  # 法国、塞内加尔、伊拉克、挪威
    "J": ["ARG", "ALG", "AUT", "JOR"],  # 阿根廷、阿尔及利亚、奥地利、约旦
    "K": ["POR", "COD", "UZB", "COL"],  # 葡萄牙、民主刚果、乌兹别克斯坦、哥伦比亚
    "L": ["ENG", "CRO", "GHA", "PAN"],  # 英格兰、克罗地亚、加纳、巴拿马
}


# 兼容旧格式的GROUPS_DICT（球队字典列表）
def get_groups_dict():
    """获取旧格式的GROUPS（球队字典列表）"""
    team_lookup = get_team_lookup()
    return {
        group: [team_lookup.get(code, {"code": code, "name_cn": code, "elo": 1500, "rank": 50}) 
                for code in codes]
        for group, codes in GROUPS.items()
    }


# 为了兼容旧API，创建GROUPS_DICT
GROUPS_DICT = None  # 延迟初始化


def get_groups():
    """获取GROUPS_DICT（兼容旧API）"""
    global GROUPS_DICT
    if GROUPS_DICT is None:
        GROUPS_DICT = get_groups_dict()
    return GROUPS_DICT


def get_all_teams():
    """获取所有球队列表"""
    return ALL_TEAMS


def get_team_lookup():
    """获取球队查询字典"""
    return {t["code"]: t for t in ALL_TEAMS}


def get_group_teams(group: str):
    """获取指定小组的球队"""
    group = group.upper()
    codes = GROUPS.get(group, [])
    team_lookup = get_team_lookup()
    return [team_lookup.get(code, {"code": code, "name_cn": code}) for code in codes]


def generate_groups():
    """返回预定义的分组"""
    result = {}
    team_lookup = get_team_lookup()
    for group, codes in GROUPS.items():
        result[group] = [team_lookup.get(code, {"code": code, "name_cn": code}) for code in codes]
    return result


def generate_match_schedule():
    """生成小组赛赛程"""
    schedule = {}
    match_num = 0
    
    for group_name, codes in GROUPS.items():
        teams = get_group_teams(group_name)
        
        # 小组赛6场比赛（轮换对阵）
        # 第1轮：0 vs 1, 2 vs 3
        # 第2轮：0 vs 2, 1 vs 3
        # 第3轮：0 vs 3, 1 vs 2
        match_pairs = [
            (0, 1), (2, 3),  # 第1轮
            (0, 2), (1, 3),  # 第2轮
            (0, 3), (1, 2),  # 第3轮
        ]
        
        group_matches = []
        for i, (home_idx, away_idx) in enumerate(match_pairs):
            group_matches.append({
                "match_id": f"{group_name}_{i+1}",
                "home": codes[home_idx],
                "away": codes[away_idx],
                "group": group_name,
                "match_index": i,
                "round": i // 2 + 1
            })
        
        schedule[group_name] = group_matches
    
    return schedule


MATCH_SCHEDULE = generate_match_schedule()


# ========== 数据验证 ==========
def validate_teams():
    """验证球队数据"""
    codes = [t["code"] for t in ALL_TEAMS]
    
    # 检查重复
    if len(codes) != len(set(codes)):
        print("错误：存在重复的球队代码")
        return False
    
    # 检查数量
    if len(ALL_TEAMS) != 48:
        print(f"警告：球队数量为{len(ALL_TEAMS)}，标准为48支")
    
    # 检查分组完整性
    team_lookup = get_team_lookup()
    for group, codes in GROUPS.items():
        for code in codes:
            if code not in team_lookup:
                print(f"警告：分组{group}中的球队{code}不在球队列表中")
    
    print(f"✓ 数据验证通过：{len(ALL_TEAMS)}支球队，{len(GROUPS)}个小组")
    return True


if __name__ == "__main__":
    validate_teams()
    
    # 打印分组
    print("\n" + "=" * 60)
    print("2026世界杯分组（官方抽签结果）")
    print("=" * 60)
    
    for group, codes in GROUPS.items():
        teams = get_group_teams(group)
        print(f"\n{group}组:")
        for t in teams:
            print(f"  {t['code']}: {t['name_cn']} (排名{t['rank']}, Elo {t['elo']})")
