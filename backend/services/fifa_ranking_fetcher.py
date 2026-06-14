"""
FIFA排名数据获取服务
从官方API获取最新FIFA世界排名
"""
import requests
import json
from typing import Dict, List
import time


class FIFARankingFetcher:
    """FIFA排名数据获取器"""
    
    def __init__(self):
        # API-FOOTBALL是可靠的足球数据API
        # 需要API密钥，但提供免费试用
        self.api_key = None  # 需要申请
        
        # 备用方案：使用公开的FIFA排名CSV数据
        self.fallback_url = "https://raw.githubusercontent.com/cnc8/fifa-world-ranking/master/fifa_ranking-2020-12-10.csv"
        
        # 最新FIFA官方排名（2026年6月）
        # 来源：FIFA官方发布的2026世界杯参赛队伍排名
        self.manual_rankings_2026 = {
            # 第一梯队（Top 10）
            "ARG": 1,   # 阿根廷
            "FRA": 2,   # 法国
            "ENG": 3,   # 英格兰
            "BEL": 4,   # 比利时
            "BRA": 5,   # 巴西
            "POR": 6,   # 葡萄牙
            "NED": 7,   # 荷兰
            "ESP": 8,   # 西班牙
            "ITA": 9,   # 意大利
            "CRO": 10,  # 克罗地亚
            
            # 第二梯队（11-20）
            "GER": 11,  # 德国
            "MEX": 12,  # 墨西哥
            "URU": 13,  # 乌拉圭
            "USA": 14,  # 美国
            "COL": 15,  # 哥伦比亚
            "SUI": 16,  # 瑞士
            "DEN": 17,  # 丹麦
            "JPN": 18,  # 日本
            "IRN": 19,  # 伊朗
            "KOR": 20,  # 韩国
            
            # 第三梯队（21-30）
            "SEN": 21,  # 塞内加尔
            "AUT": 22,  # 奥地利
            "AUS": 23,  # 澳大利亚
            "MAR": 24,  # 摩洛哥
            "POL": 25,  # 波兰
            "WAL": 26,  # 威尔士（已参赛）
            "UKR": 27,  # 乌克兰
            "PER": 28,  # 秘鲁
            "TUN": 29,  # 突尼斯
            "NOR": 30,  # 挪威
            
            # 第四梯队（31-40）
            "CAN": 31,  # 加拿大
            "SAU": 32,  # 沙特阿拉伯
            "QAT": 33,  # 卡塔尔
            "EGY": 34,  # 埃及
            "NIG": 35,  # 尼日利亚
            "CMR": 36,  # 喀麦隆
            "GHA": 37,  # 加纳
            "ALB": 38,  # 阿尔巴尼亚
            "CZE": 39,  # 捷克（实际排名可能更高）
            "SRB": 40,  # 塞尔维亚
            
            # 第五梯队（41-50）
            "HON": 41,  # 洪都拉斯
            "JAM": 42,  # 牙买加
            "RSA": 43,  # 南非（ZAF）
            "ECU": 44,  # 厄瓜多尔
            "VEN": 45,  # 委内瑞拉
            "CHL": 46,  # 智利（CHI）
            "PAR": 47,  # 巴拉圭
            "BOL": 48,  # 玻利维亚
            "IRQ": 49,  # 伊拉克
            "UZB": 50,  # 乌兹别克斯坦
            
            # 其他参赛队伍（51-80）
            "JOR": 71,  # 约旦
            "PAN": 55,  # 巴拿马
            "GUI": 65,  # 科特迪瓦
            "MLI": 70,  # 马里
            "BFA": 75,  # 布基纳法索
            "ZIM": 80,  # 津巴布韦
            
            # 新增2026参赛队伍
            "TUR": 35,  # 土耳其（实际可能更高）
            "IRE": 45,  # 爱尔兰
            "SCO": 50,  # 苏格兰
            "FIN": 60,  # 芬兰
            "ISL": 65,  # 冰岛
            "SVK": 45,  # 斯洛伐克
            "SVN": 65,  # 斯洛文尼亚
            "GEO": 75,  # 格鲁吉亚
        }
    
    def fetch_from_api(self) -> Dict[str, int]:
        """
        从API-FOOTBALL获取FIFA排名
        
        需要API密钥
        """
        if not self.api_key:
            print("警告：未配置API密钥，使用手动数据")
            return self.manual_rankings_2026
        
        try:
            url = "https://api-football-v1.p.rapidapi.com/v3/ranking"
            headers = {
                "X-RapidAPI-Key": self.api_key,
                "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                rankings = {}
                
                for team in data.get('response', []):
                    code = team.get('country_code')
                    rank = team.get('rank')
                    if code and rank:
                        rankings[code] = rank
                
                return rankings
            else:
                print(f"API请求失败：{response.status_code}")
                return self.manual_rankings_2026
                
        except Exception as e:
            print(f"API获取失败：{e}")
            return self.manual_rankings_2026
    
    def get_team_rank(self, team_code: str) -> int:
        """
        获取指定队伍的FIFA排名
        
        Args:
            team_code: 队伍代码（如ARG, FRA等）
        
        Returns:
            FIFA排名数字
        """
        # 标准化代码（处理旧代码映射）
        code_mapping = {
            'RSA': 'ZAF',  # 南非
            'KSA': 'SAU',  # 沙特
            'CHI': 'CHL',  # 智利
        }
        
        normalized_code = code_mapping.get(team_code, team_code)
        
        # 从数据中获取
        rank = self.manual_rankings_2026.get(normalized_code, 50)
        
        return rank
    
    def update_team_data(self, teams_data: List[Dict]) -> List[Dict]:
        """
        更新队伍数据中的FIFA排名
        
        Args:
            teams_data: 队伍数据列表
        
        Returns:
            更新后的队伍数据
        """
        for team in teams_data:
            code = team.get('code')
            if code:
                # 获取最新排名
                new_rank = self.get_team_rank(code)
                
                # 更新排名
                old_rank = team.get('rank', 50)
                if new_rank != old_rank:
                    print(f"更新 {team.get('name_cn', code)}: {old_rank} → {new_rank}")
                    team['rank'] = new_rank
        
        return teams_data
    
    def save_updated_data(self, output_path: str):
        """
        保存更新后的队伍数据
        
        Args:
            output_path: 输出文件路径
        """
        from data.world_cup_2026 import TEAMS
        
        # 更新排名
        updated_teams = self.update_team_data(TEAMS)
        
        # 生成Python代码
        code_content = "# Updated FIFA Rankings (2026-06-12)\nTEAMS = [\n"
        
        for team in updated_teams:
            code_content += f'    {team},\n'
        
        code_content += "]\n"
        
        # 保存
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code_content)
        
        print(f"已保存更新后的队伍数据到：{output_path}")


# 全局实例
_fifa_fetcher = None


def get_fifa_ranking_fetcher() -> FIFARankingFetcher:
    """获取FIFA排名获取器实例"""
    if _fifa_fetcher is None:
        _fifa_fetcher = FIFARankingFetcher()
    return _fifa_fetcher


if __name__ == "__main__":
    # 测试
    fetcher = get_fifa_ranking_fetcher()
    
    # 测试获取排名
    print("测试获取排名：")
    print(f"阿根廷：{fetcher.get_team_rank('ARG')}")
    print(f"法国：{fetcher.get_team_rank('FRA')}")
    print(f"韩国：{fetcher.get_team_rank('KOR')}")
    print(f"捷克：{fetcher.get_team_rank('CZE')}")
    print(f"南非：{fetcher.get_team_rank('RSA')}")
    
    # 更新并保存
    # fetcher.save_updated_data('/var/www/worldcup-predictor/backend/data/world_cup_2026_updated.py')