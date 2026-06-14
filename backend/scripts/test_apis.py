#!/usr/bin/env python3
"""
测试贝叶斯分析和三模型对比API
"""
import requests
import json
import time

BASE_URL = "http://127.0.0.1:8011"

def test_calculation_api():
    """测试贝叶斯分析API"""
    print("=" * 60)
    print("📊 测试贝叶斯分析API")
    print("=" * 60)
    
    test_cases = [
        ("A组第1场", "A", 0),
        ("B组第2场（卡塔尔vs瑞士）", "B", 1),
        ("C组第1场", "C", 0),
    ]
    
    for name, group, idx in test_cases:
        url = f"{BASE_URL}/api/calculation/match/{group}/{idx}"
        
        try:
            start = time.time()
            resp = requests.get(url, timeout=10)
            elapsed = (time.time() - start) * 1000
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ {name}: {elapsed:.0f}ms")
                print(f"   预测: {data.get('prediction', 'N/A')}")
                print(f"   置信度: {data.get('confidence', 'N/A')}")
            else:
                print(f"❌ {name}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
    
    print()


def test_models_api():
    """测试三模型对比API"""
    print("=" * 60)
    print("🎯 测试三模型对比API")
    print("=" * 60)
    
    test_cases = [
        ("A组第1场", "A", 0),
        ("B组第2场（卡塔尔vs瑞士）", "B", 1),
        ("C组第1场", "C", 0),
    ]
    
    for name, group, idx in test_cases:
        url = f"{BASE_URL}/api/models/predict/group/{group}/{idx}"
        
        try:
            start = time.time()
            resp = requests.get(url, timeout=10)
            elapsed = (time.time() - start) * 1000
            
            if resp.status_code == 200:
                data = resp.json()
                print(f"✅ {name}: {elapsed:.0f}ms")
                
                preds = data.get('predictions', {})
                bayesian = preds.get('bayesian', {})
                nn = preds.get('neural_network', {})
                rf = preds.get('random_forest', {})
                ensemble = data.get('ensemble', {})
                
                print(f"   贝叶斯: 主{bayesian.get('home_win', 0)*100:.1f}% | 客{bayesian.get('away_win', 0)*100:.1f}%")
                print(f"   神经网络: 主{nn.get('home_win', 0)*100:.1f}% | 客{nn.get('away_win', 0)*100:.1f}%")
                print(f"   随机森林: 主{rf.get('home_win', 0)*100:.1f}% | 客{rf.get('away_win', 0)*100:.1f}%")
                print(f"   集成: 主{ensemble.get('home_win', 0)*100:.1f}% | 客{ensemble.get('away_win', 0)*100:.1f}%")
            else:
                print(f"❌ {name}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"❌ {name}: {str(e)}")
    
    print()


def test_frontend_api_proxy():
    """测试前端API代理"""
    print("=" * 60)
    print("🌐 测试前端API代理（通过nginx）")
    print("=" * 60)
    
    # 测试通过nginx访问
    test_cases = [
        "/worldcup/api/calculation/match/B/1",
        "/worldcup/api/models/predict/group/B/1",
    ]
    
    for path in test_cases:
        try:
            resp = requests.get(f"http://127.0.0.1{path}", timeout=10)
            
            if resp.status_code == 200:
                print(f"✅ {path}: OK")
            else:
                print(f"❌ {path}: HTTP {resp.status_code}")
        except Exception as e:
            print(f"❌ {path}: {str(e)}")
    
    print()


if __name__ == "__main__":
    test_calculation_api()
    test_models_api()
    test_frontend_api_proxy()
    
    print("=" * 60)
    print("✅ 测试完成")
    print("=" * 60)
