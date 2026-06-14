#!/usr/bin/env python3
"""
测试小组赛页面的所有功能
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8011"

def test_api_response_time():
    """测试API响应时间"""
    print("=" * 60)
    print("📊 测试API响应时间")
    print("=" * 60)
    
    tests = [
        ("/api/groups/static", "小组静态信息"),
        ("/api/groups/A", "A组详情"),
        ("/api/groups/B", "B组详情"),
        ("/api/groups/C", "C组详情"),
        ("/api/groups/D", "D组详情"),
    ]
    
    for endpoint, name in tests:
        start = time.time()
        try:
            resp = requests.get(f"{BASE_URL}{endpoint}", timeout=5)
            elapsed = (time.time() - start) * 1000
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ {name}: {elapsed:.0f}ms")
            else:
                print(f"❌ {name}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
    
    print()


def test_data_integrity():
    """测试数据完整性"""
    print("=" * 60)
    print("🔍 测试数据完整性")
    print("=" * 60)
    
    # 获取所有小组
    resp = requests.get(f"{BASE_URL}/api/groups/static")
    groups = resp.json().get("groups", {})
    
    print(f"小组数量: {len(groups)}")
    
    issues = []
    
    for group_name in groups.keys():
        resp = requests.get(f"{BASE_URL}/api/groups/{group_name}")
        data = resp.json()
        
        # 检查积分榜
        if len(data.get("standings", [])) != 4:
            issues.append(f"{group_name}组: 积分榜数据不完整")
        
        # 检查比赛数据
        matches = data.get("matches", [])
        if len(matches) != 6:
            issues.append(f"{group_name}组: 比赛数据不完整（{len(matches)}场）")
        
        # 检查每场比赛的预测数据
        for i, m in enumerate(matches):
            if not m.get("home_win_prob"):
                issues.append(f"{group_name}组第{i+1}场: 缺少预测数据")
            
            # 检查三模型对比
            mc = m.get("models_comparison", {})
            if not mc:
                issues.append(f"{group_name}组第{i+1}场: 缺少三模型对比")
            
            # 检查赔率对比
            oc = m.get("odds_comparison", {})
            if not oc:
                issues.append(f"{group_name}组第{i+1}场: 缺少赔率对比")
    
    if issues:
        print("\n❌ 发现问题:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ 所有数据完整")
    
    print()


def test_prediction_consistency():
    """测试预测一致性"""
    print("=" * 60)
    print("🎯 测试预测一致性")
    print("=" * 60)
    
    # 测试B组（卡塔尔vs瑞士）
    resp = requests.get(f"{BASE_URL}/api/groups/B")
    data = resp.json()
    
    match = data["matches"][1]  # 卡塔尔vs瑞士
    
    mc = match["models_comparison"]
    
    print("【卡塔尔 vs 瑞士】")
    print(f"贝叶斯: 主{mc['bayesian']['home_win']*100:.1f}% | 平{mc['bayesian']['draw']*100:.1f}% | 客{mc['bayesian']['away_win']*100:.1f}%")
    print(f"神经网络: 主{mc['neural_network']['home_win']*100:.1f}% | 平{mc['neural_network']['draw']*100:.1f}% | 客{mc['neural_network']['away_win']*100:.1f}%")
    print(f"随机森林: 主{mc['random_forest']['home_win']*100:.1f}% | 平{mc['random_forest']['draw']*100:.1f}% | 客{mc['random_forest']['away_win']*100:.1f}%")
    print(f"集成预测: 主{mc['ensemble']['home_win']*100:.1f}% | 平{mc['ensemble']['draw']*100:.1f}% | 客{mc['ensemble']['away_win']*100:.1f}%")
    
    # 检查随机森林是否异常
    if mc['random_forest']['home_win'] > 0.8:
        print("\n⚠️ 随机森林预测异常（主胜>80%）")
    else:
        print("\n✅ 随机森林预测正常")
    
    print()


def test_frontend_resources():
    """测试前端资源"""
    print("=" * 60)
    print("📦 测试前端资源")
    print("=" * 60)
    
    import os
    
    dist_path = "/var/www/worldcup-predictor/frontend/dist"
    
    # 检查文件
    files = [
        "index.html",
        "assets/index-D6M38rDz.js",
        "assets/index-Pg5m687I.css",
    ]
    
    for file in files:
        path = os.path.join(dist_path, file)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {file}: {size/1024:.1f}KB")
        else:
            print(f"❌ {file}: 不存在")
    
    print()


if __name__ == "__main__":
    test_api_response_time()
    test_data_integrity()
    test_prediction_consistency()
    test_frontend_resources()
    
    print("=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
