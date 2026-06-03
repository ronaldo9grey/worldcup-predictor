#!/bin/bash
# 世界杯预测系统 V6 启动脚本

echo "============================================================"
echo "世界杯预测系统 V6"
echo "============================================================"
echo ""
echo "功能特性:"
echo "  - 特征引擎V2: 13维特征 + h2h + venue + 交互"
echo "  - 在线学习V2: 阶段自适应学习率 + 动态窗口"
echo "  - 模型训练V2: 进度展示 + 持久化存储"
echo ""
echo "============================================================"
echo ""

# 切换到后端目录
cd /var/www/worldcup-predictor/backend

# 检查训练历史
echo "📊 检查训练历史..."
if [ -f "data/training_history.json" ]; then
    echo "  ✓ 发现历史训练记录"
else
    echo "  ⚠️  无历史训练记录"
    echo ""
    echo "💡 建议: 首次使用请先训练模型"
    echo "   访问 http://localhost:8012/api/training/start 启动训练"
fi

echo ""
echo "============================================================"
echo "启动服务..."
echo "============================================================"
echo ""
echo "API地址: http://localhost:8012"
echo ""
echo "主要接口:"
echo "  - 预测: http://localhost:8012/api/v6/predict"
echo "  - 训练: http://localhost:8012/api/training/start"
echo "  - 进度: http://localhost:8012/api/training/progress"
echo "  - 历史: http://localhost:8012/api/training/summary"
echo ""
echo "按 Ctrl+C 停止服务"
echo "============================================================"
echo ""

# 启动服务
python3 main_v6.py
