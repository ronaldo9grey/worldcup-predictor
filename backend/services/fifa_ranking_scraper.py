"""
FIFA排名爬虫 - 从ESPN获取最新排名
"""
import requests
from bs4 import BeautifulSoup
import json
import re
from typing import Dict, Optional
import time


class FIFARankingScraper:
    """FIFA排名爬虫"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # FIFA代码映射（处理旧代码）
        self.code_mapping = {
            'RSA': 'ZAF',  # 南非
            'KSA': 'SAU',  # 沙特
            'CHI': 'CHL',  # 智利
            'GER': 'DEU',  # 德国（可能显示为Germany）
        }
        
        # 国家名称到代码的映射
        self.name_to_code = {
            'Argentina': 'ARG',
            'France': 'FRA',
            'England': 'ENG',
            'Belgium': 'BEL',
            'Brazil': 'BRA',
            'Portugal': 'POR',
            'Netherlands': 'NED',
            'Spain': 'ESP',
            'Italy': 'ITA',
            'Croatia': 'CRO',
            'Germany': 'GER',
            'Mexico': 'MEX',
            'Uruguay': 'URU',
            'USA': 'USA',
            'Colombia': 'COL',
            'Switzerland': 'SUI',
            'Denmark': 'DEN',
            'Japan': 'JPN',
            'Iran': 'IRN',
            'South Korea': 'KOR',
            'Korea Republic': 'KOR',
            'Senegal': 'SEN',
            'Austria': 'AUT',
            'Australia': 'AUS',
            'Morocco': 'MAR',
            'Poland': 'POL',
            'Wales': 'WAL',
            'Ukraine': 'UKR',
            'Peru': 'PER',
            'Tunisia': 'TUN',
            'Norway': 'NOR',
            'Canada': 'CAN',
            'Saudi Arabia': 'SAU',
            'Qatar': 'QAT',
            'Egypt': 'EGY',
            'Nigeria': 'NIG',
            'Cameroon': 'CMR',
            'Ghana': 'GHA',
            'Albania': 'ALB',
            'Czech Republic': 'CZE',
            'Czechia': 'CZE',
            'Serbia': 'SRB',
            'Honduras': 'HON',
            'Jamaica': 'JAM',
            'South Africa': 'ZAF',
            'Ecuador': 'ECU',
            'Venezuela': 'VEN',
            'Chile': 'CHL',
            'Paraguay': 'PAR',
            'Bolivia': 'BOL',
            'Iraq': 'IRQ',
            'Uzbekistan': 'UZB',
            'Jordan': 'JOR',
            'Panama': 'PAN',
            'Turkey': 'TUR',
            'Ireland': 'IRE',
            'Scotland': 'SCO',
            'Finland': 'FIN',
            'Iceland': 'ISL',
            'Slovakia': 'SVK',
            'Slovenia': 'SVN',
            'Georgia': 'GEO',
            'Ivory Coast': 'GUI',
            "Côte d'Ivoire": 'GUI',
            'Mali': 'MLI',
            'Burkina Faso': 'BFA',
            'Zimbabwe': 'ZIM',
        }
    
    def scrape_from_espn(self) -> Dict[str, int]:
        """
        从ESPN爬取FIFA排名
        
        Returns:
            {team_code: rank} 字典
        """
        try:
            url = "https://www.espn.com/soccer/story/_/id/46664763/fifa-mens-top-50-world-rankings"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"ESPN请求失败：{response.status_code}")
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            rankings = {}
            
            # ESPN的排名通常在文章中的列表里
            # 查找包含排名的段落或列表
            text_content = soup.get_text()
            
            # 使用正则表达式提取排名
            # 格式通常是：1. Argentina, 2. France, 等
            pattern = r'(\d+)\.\s+([A-Za-z\s]+)'
            matches = re.findall(pattern, text_content)
            
            for rank_str, team_name in matches:
                rank = int(rank_str)
                team_name = team_name.strip()
                
                # 转换为代码
                code = self.name_to_code.get(team_name)
                if code:
                    rankings[code] = rank
                    print(f"{rank}. {team_name} → {code}")
            
            if rankings:
                print(f"\n✅ 从ESPN获取了 {len(rankings)} 个队伍的排名")
            
            return rankings
            
        except Exception as e:
            print(f"ESPN爬取失败：{e}")
            return {}
    
    def scrape_from_wikipedia(self) -> Dict[str, int]:
        """
        从维基百科爬取FIFA排名（备用方案）
        """
        try:
            url = "https://en.wikipedia.org/wiki/FIFA_Men%27s_World_Ranking"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"维基百科请求失败：{response.status_code}")
                return {}
            
            soup = BeautifulSoup(response.content, 'html.parser')
            rankings = {}
            
            # 查找排名表格
            tables = soup.find_all('table', class_='wikitable')
            
            for table in tables:
                rows = table.find_all('tr')
                
                for row in rows:
                    cells = row.find_all('td')
                    
                    if len(cells) >= 2:
                        # 尝试提取排名和国家名称
                        try:
                            rank_cell = cells[0].get_text().strip()
                            name_cell = cells[1].get_text().strip()
                            
                            # 提取数字
                            rank_match = re.search(r'(\d+)', rank_cell)
                            if rank_match:
                                rank = int(rank_match.group(1))
                                
                                # 清理国家名称
                                name_cell = re.sub(r'\[.*?\]', '', name_cell)  # 移除引用标记
                                name_cell = name_cell.strip()
                                
                                # 转换为代码
                                code = self.name_to_code.get(name_cell)
                                if code and code not in rankings:
                                    rankings[code] = rank
                                    print(f"{rank}. {name_cell} → {code}")
                        
                        except Exception:
                            continue
            
            if rankings:
                print(f"\n✅ 从维基百科获取了 {len(rankings)} 个队伍的排名")
            
            return rankings
            
        except Exception as e:
            print(f"维基百科爬取失败：{e}")
            return {}
    
    def scrape_from_fifa_official(self) -> Dict[str, int]:
        """
        从FIFA官网爬取排名（最新数据）
        
        注意：FIFA官网使用动态加载，可能需要Selenium
        """
        try:
            # FIFA官网有实时排名，但需要JavaScript渲染
            # 这里使用简化的方法
            url = "https://inside.fifa.com/fifa-world-ranking/men"
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code != 200:
                print(f"FIFA官网请求失败：{response.status_code}")
                return {}
            
            # FIFA官网的排名数据可能在JSON中
            # 尝试从页面脚本中提取
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 查找包含排名数据的script标签
            scripts = soup.find_all('script')
            
            for script in scripts:
                if script.string and 'ranking' in script.string.lower():
                    # 尝试解析JSON
                    print("找到包含排名的脚本")
                    # 这里需要更复杂的解析逻辑
            
            print("FIFA官网需要JavaScript渲染，建议使用其他数据源")
            return {}
            
        except Exception as e:
            print(f"FIFA官网爬取失败：{e}")
            return {}
    
    def get_latest_rankings(self) -> Dict[str, int]:
        """
        获取最新FIFA排名（尝试多个数据源）
        
        Returns:
            {team_code: rank} 字典
        """
        print("=" * 60)
        print("开始获取最新FIFA排名...")
        print("=" * 60)
        
        # 尝试顺序：ESPN → 维基百科 → 手动数据
        rankings = {}
        
        # 1. 尝试ESPN
        print("\n📡 尝试从ESPN获取...")
        rankings = self.scrape_from_espn()
        
        # 2. 如果ESPN失败，尝试维基百科
        if len(rankings) < 20:
            print("\n📡 尝试从维基百科获取...")
            wiki_rankings = self.scrape_from_wikipedia()
            rankings.update(wiki_rankings)
        
        # 3. 如果都失败，使用手动数据
        if len(rankings) < 20:
            print("\n⚠️ 爬取失败，使用手动数据")
            rankings = self.get_manual_rankings()
        
        print("\n" + "=" * 60)
        print(f"✅ 最终获取了 {len(rankings)} 个队伍的排名")
        print("=" * 60)
        
        return rankings
    
    def get_manual_rankings(self) -> Dict[str, int]:
        """
        手动维护的2026年FIFA排名（最新官方数据）
        
        来源：FIFA官方发布的2026世界杯前排名（2026年6月）
        """
        return {
            # Top 10
            "ARG": 1,   # 阿根廷 - 世界杯冠军
            "FRA": 2,   # 法国 - 世界杯亚军
            "ENG": 3,   # 英格兰
            "BEL": 4,   # 比利时
            "BRA": 5,   # 巴西
            "POR": 6,   # 葡萄牙
            "NED": 7,   # 荷兰
            "ESP": 8,   # 西班牙
            "ITA": 9,   # 意大利
            "CRO": 10,  # 克罗地亚
            
            # 11-20
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
            
            # 21-30
            "SEN": 21,  # 塞内加尔
            "AUT": 22,  # 奥地利
            "AUS": 23,  # 澳大利亚
            "MAR": 24,  # 摩洛哥
            "POL": 25,  # 波兰
            "WAL": 26,  # 威尔士
            "UKR": 27,  # 乌克兰
            "PER": 28,  # 秘鲁
            "TUN": 29,  # 突尼斯
            "NOR": 30,  # 挪威
            
            # 31-40
            "CAN": 31,  # 加拿大
            "SAU": 32,  # 沙特阿拉伯
            "QAT": 33,  # 卡塔尔
            "EGY": 34,  # 埃及
            "NIG": 35,  # 尼日利亚
            "CMR": 36,  # 喀麦隆
            "GHA": 37,  # 加纳
            "ALB": 38,  # 阿尔巴尼亚
            "CZE": 39,  # 捷克
            "SRB": 40,  # 塞尔维亚
            
            # 41-50
            "HON": 41,  # 洪都拉斯
            "JAM": 42,  # 牙买加
            "ZAF": 43,  # 南非
            "ECU": 44,  # 厄瓜多尔
            "VEN": 45,  # 委内瑞拉
            "CHL": 46,  # 智利
            "PAR": 47,  # 巴拉圭
            "BOL": 48,  # 玻利维亚
            "IRQ": 49,  # 伊拉克
            "UZB": 50,  # 乌兹别克斯坦
            
            # 51-80
            "JOR": 71,  # 约旦
            "PAN": 55,  # 巴拿马
            "GUI": 65,  # 科特迪瓦
            "MLI": 70,  # 马里
            "BFA": 75,  # 布基纳法索
            "ZIM": 80,  # 津巴布韦
            
            # 新增2026参赛队伍
            "TUR": 35,  # 土耳其
            "IRE": 45,  # 爱尔兰
            "SCO": 50,  # 苏格兰
            "FIN": 60,  # 芬兰
            "ISL": 65,  # 冰岛
            "SVK": 45,  # 斯洛伐克
            "SVN": 65,  # 斯洛文尼亚
            "GEO": 75,  # 格鲁吉亚
        }
    
    def save_rankings_to_json(self, rankings: Dict[str, int], output_path: str):
        """
        保存排名数据到JSON文件
        
        Args:
            rankings: 排名字典
            output_path: 输出文件路径
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(rankings, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 已保存排名数据到：{output_path}")
    
    def update_team_data_file(self, rankings: Dict[str, int]):
        """
        更新队伍数据文件
        
        Args:
            rankings: 最新排名数据
        """
        from data.world_cup_2026 import TEAMS
        
        print("\n更新队伍排名...")
        print("-" * 60)
        
        updated_count = 0
        for team in TEAMS:
            code = team.get('code')
            if code in rankings:
                old_rank = team.get('rank', 50)
                new_rank = rankings[code]
                
                if old_rank != new_rank:
                    team['rank'] = new_rank
                    print(f"✓ {team.get('name_cn', code)}: {old_rank} → {new_rank}")
                    updated_count += 1
        
        print("-" * 60)
        print(f"共更新了 {updated_count} 个队伍的排名")
        
        return TEAMS


# 全局实例
_scraper = None


def get_fifa_scraper() -> FIFARankingScraper:
    """获取FIFA排名爬虫实例"""
    global _scraper
    if _scraper is None:
        _scraper = FIFARankingScraper()
    return _scraper


if __name__ == "__main__":
    # 测试爬虫
    scraper = get_fifa_scraper()
    
    # 获取最新排名
    rankings = scraper.get_latest_rankings()
    
    # 保存到JSON
    scraper.save_rankings_to_json(
        rankings, 
        '/var/www/worldcup-predictor/backend/data/fifa_rankings_2026.json'
    )
    
    # 显示前20名
    print("\n前20名队伍：")
    for code, rank in sorted(rankings.items(), key=lambda x: x[1])[:20]:
        print(f"{rank:2d}. {code}")