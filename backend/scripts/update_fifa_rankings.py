#!/usr/bin/env python3
"""
更新队伍FIFA排名数据
从最新的FIFA排名JSON更新world_cup_2026.py中的队伍数据
"""
import json
import sys
import os

# 添加backend目录到路径
sys.path.insert(0, '/var/www/worldcup-predictor/backend')


def load_latest_rankings():
    """加载最新FIFA排名"""
    json_path = '/var/www/worldcup-predictor/backend/data/fifa_rankings_2026.json'
    
    with open(json_path, 'r', encoding='utf-8') as f:
        rankings = json.load(f)
    
    return rankings


def update_team_data(rankings):
    """更新队伍数据"""
    # 读取原始数据
    from data.world_cup_2026 import TEAMS
    
    print("更新队伍FIFA排名...")
    print("=" * 60)
    
    updated_count = 0
    
    for team in TEAMS:
        code = team.get('code')
        if code in rankings:
            old_rank = team.get('rank', 50)
            new_rank = rankings[code]
            
            if old_rank != new_rank:
                team['rank'] = new_rank
                name_cn = team.get('name_cn', code)
                print(f"✓ {name_cn}（{code}）: {old_rank} → {new_rank}")
                updated_count += 1
    
    print("=" * 60)
    print(f"共更新了 {updated_count} 个队伍的排名")
    
    return TEAMS, updated_count


def save_updated_data(teams):
    """保存更新后的数据到Python文件"""
    output_path = '/var/www/worldcup-predictor/backend/data/world_cup_2026.py'
    
    # 备份原文件
    backup_path = output_path + '.backup'
    os.system(f'cp {output_path} {backup_path}')
    print(f"✓ 已备份原文件到：{backup_path}")
    
    # 生成新的Python代码
    with open(output_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 找到TEAMS数组的开始和结束
    import re
    
    # 匹配 TEAMS = [...] 的内容
    pattern = r'(TEAMS\s*=\s*\[)(.*?)(\])'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        # 生成新的队伍列表代码
        teams_code = ""
        for team in teams:
            teams_code += f'    {team},\n'
        
        # 替换内容
        new_content = content[:match.start()] + \
                     f'TEAMS = [\n{teams_code}]' + \
                     content[match.end():]
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ 已更新文件：{output_path}")
        return True
    else:
        print("❌ 无法找到TEAMS数组")
        return False


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("FIFA排名数据更新工具")
    print("=" * 60)
    
    # 1. 加载最新排名
    print("\n1. 加载最新FIFA排名...")
    rankings = load_latest_rankings()
    print(f"   ✓ 加载了 {len(rankings)} 个队伍的排名")
    
    # 2. 更新队伍数据
    print("\n2. 更新队伍数据...")
    teams, updated_count = update_team_data(rankings)
    
    if updated_count > 0:
        # 3. 保存更新
        print("\n3. 保存更新...")
        if save_updated_data(teams):
            print("\n✅ 更新完成！")
            print("\n请重启服务使更改生效：")
            print("  systemctl restart worldcup-predictor")
        else:
            print("\n❌ 保存失败")
            return 1
    else:
        print("\n✓ 所有排名已是最新，无需更新")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())