"""
分享功能 - 第九轮迭代
生成分享链接、分享图片
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import HTMLResponse
from typing import Dict, Optional
import base64
import hashlib
from datetime import datetime

router = APIRouter(prefix="/api/share", tags=["分享"])


@router.get("/prediction/{match_id}")
async def generate_share_link(
    match_id: str,
    prediction: str,  # HOME_WIN, DRAW, AWAY_WIN
    confidence: str,  # HIGH, MEDIUM, LOW
    user_nickname: Optional[str] = None
) -> Dict:
    """
    生成预测分享链接
    
    match_id: 比赛ID（如 ARG-BRA）
    prediction: 预测结果
    confidence: 信心等级
    user_nickname: 用户昵称（可选）
    """
    # 生成唯一分享码
    share_code = generate_share_code(match_id, prediction, confidence)
    
    # 解析比赛信息
    teams = match_id.split("-")
    home_team = teams[0] if len(teams) > 0 else "UNKNOWN"
    away_team = teams[1] if len(teams) > 1 else "UNKNOWN"
    
    # 构建分享内容
    team_names = get_team_names()
    home_name = team_names.get(home_team, home_team)
    away_name = team_names.get(away_team, away_team)
    
    prediction_text = {
        "HOME_WIN": f"{home_name}胜",
        "DRAW": "平局",
        "AWAY_WIN": f"{away_name}胜"
    }.get(prediction, prediction)
    
    confidence_emoji = {
        "HIGH": "🔥 高信心",
        "MEDIUM": "⚡ 中信心",
        "LOW": "🎲 低信心"
    }.get(confidence, confidence)
    
    share_text = f"我预测{home_name} vs {away_name}：{prediction_text} {confidence_emoji}"
    
    if user_nickname:
        share_text = f"{user_nickname}预测：{prediction_text} {confidence_emoji}"
    
    # 分享链接
    base_url = "https://your-domain.com/worldcup"
    share_link = f"{base_url}/shared/{share_code}"
    
    return {
        "share_code": share_code,
        "share_link": share_link,
        "share_text": share_text,
        "match": f"{home_name} vs {away_name}",
        "prediction": prediction_text,
        "confidence": confidence_emoji,
        "user_nickname": user_nickname,
        "created_at": datetime.now().isoformat(),
    }


@router.get("/card/{share_code}", response_class=HTMLResponse)
async def get_share_card(share_code: str) -> str:
    """
    获取分享卡片（HTML页面）
    用于社交媒体分享展示
    """
    # 解析分享码（实际应用中需要查询数据库）
    # 这里简化处理
    
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta property="og:title" content="我的世界杯预测">
        <meta property="og:description" content="查看我的世界杯比赛预测">
        <meta property="og:type" content="website">
        <title>世界杯预测分享</title>
        <style>
            body {{
                margin: 0;
                padding: 20px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }}
            .share-card {{
                background: white;
                border-radius: 20px;
                padding: 40px;
                max-width: 400px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                text-align: center;
            }}
            .logo {{
                font-size: 48px;
                margin-bottom: 20px;
            }}
            .title {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
                margin-bottom: 30px;
            }}
            .match {{
                font-size: 20px;
                color: #666;
                margin-bottom: 20px;
            }}
            .prediction {{
                font-size: 28px;
                font-weight: bold;
                color: #667eea;
                margin-bottom: 15px;
            }}
            .confidence {{
                font-size: 16px;
                color: #999;
                margin-bottom: 30px;
            }}
            .footer {{
                font-size: 14px;
                color: #999;
                border-top: 1px solid #eee;
                padding-top: 20px;
            }}
            .qr-hint {{
                font-size: 12px;
                color: #999;
                margin-top: 15px;
            }}
        </style>
    </head>
    <body>
        <div class="share-card">
            <div class="logo">⚽</div>
            <div class="title">世界杯预测</div>
            <div class="match">阿根廷 vs 巴西</div>
            <div class="prediction">🔥 阿根廷胜</div>
            <div class="confidence">高信心预测</div>
            <div class="footer">
                分享自世界杯预测系统
            </div>
            <div class="qr-hint">扫码查看更多预测</div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)


@router.get("/image/{match_id}")
async def generate_share_image(
    match_id: str,
    prediction: str,
    confidence: str
) -> Dict:
    """
    生成分享图片（返回base64）
    实际应用中需要使用Pillow等库生成真实图片
    """
    # 这里返回模拟的图片数据
    # 实际应用中需要：
    # 1. 使用Pillow创建图片
    # 2. 绘制比赛信息、预测结果、二维码等
    # 3. 返回base64编码的图片
    
    return {
        "image_type": "png",
        "image_base64": "模拟图片数据",
        "width": 800,
        "height": 600,
        "message": "实际应用中将生成真实图片"
    }


@router.get("/qrcode")
async def generate_qrcode(text: str = Query(...)) -> Dict:
    """
    生成二维码
    实际应用中需要使用qrcode库
    """
    # 模拟二维码生成
    qr_data = base64.b64encode(text.encode()).decode()
    
    return {
        "text": text,
        "qr_data": qr_data,
        "size": "200x200",
        "message": "实际应用中将生成真实二维码"
    }


def generate_share_code(match_id: str, prediction: str, confidence: str) -> str:
    """生成唯一分享码"""
    data = f"{match_id}-{prediction}-{confidence}-{datetime.now().timestamp()}"
    hash_obj = hashlib.md5(data.encode())
    return hash_obj.hexdigest()[:8].upper()


def get_team_names() -> Dict[str, str]:
    """获取球队中文名"""
    return {
        "ARG": "阿根廷",
        "BRA": "巴西",
        "FRA": "法国",
        "GER": "德国",
        "ENG": "英格兰",
        "ESP": "西班牙",
        "POR": "葡萄牙",
        "NED": "荷兰",
        "URU": "乌拉圭",
        "BEL": "比利时",
        "CRO": "克罗地亚",
        "USA": "美国",
        "MEX": "墨西哥",
        "JPN": "日本",
        "KOR": "韩国",
        "SEN": "塞内加尔",
        "MAR": "摩洛哥",
    }
