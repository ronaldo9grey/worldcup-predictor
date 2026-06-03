# 🌍 世界杯预测系统 (World Cup Predictor)

基于贝叶斯、神经网络和随机森林三模型集成的世界杯比赛预测系统。

## ✨ 功能特性

- **🏆 小组赛预测**: 12个小组的积分榜和比赛预测
- **🧠 三模型对比**: 贝叶斯、神经网络、随机森林预测对比
- **📊 贝叶斯分析**: 详细展示预测因子和计算过程
- **🤖 模型训练**: 可在线训练神经网络和随机森林模型
- **📈 准确率统计**: 实时追踪预测准确率
- **🔮 冠军之路**: 模拟世界杯淘汰赛对阵图

## 🛠️ 技术架构

### 后端
- Python 3.11
- FastAPI
- PyTorch (神经网络)
- Scikit-learn (随机森林)
- SQLite (数据库)

### 前端
- Vue 3
- Vite

### 预测模型
- **贝叶斯模型**: 基于历史先验概率推断，准确率约53%
- **神经网络**: 3层隐藏层深度学习，准确率约72%
- **随机森林**: 100棵决策树集成，准确率约70%
- **集成模型**: 加权融合三模型预测

## 📦 安装部署

### 1. 克隆仓库
```bash
git clone https://github.com/yourusername/worldcup-predictor.git
cd worldcup-predictor
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入你的 API keys（可选）
```

### 3. 后端安装
```bash
cd backend
pip install -r requirements.txt
```

### 4. 前端安装
```bash
cd frontend
npm install
npm run build
```

### 5. 启动服务
```bash
# 使用 systemd 服务
sudo systemctl start worldcup-predictor

# 或手动启动
cd backend
python3 -m uvicorn main_v2:app --host 0.0.0.0 --port 8011 --workers 2
```

### 6. Nginx 配置
```nginx
location /worldcup/ {
    alias /var/www/worldcup-predictor/frontend/dist/;
    try_files $uri $uri/ /worldcup/index.html;
}

location /worldcup/api/ {
    proxy_pass http://127.0.0.1:8011/api/;
    proxy_http_version 1.1;
}
```

## 🎯 API 接口

### 小组赛
- `GET /api/groups/{group}` - 获取小组详情
- `GET /api/groups/{group}/qualification` - 获取出线概率

### 预测
- `GET /api/calculation/match/{group}/{idx}` - 贝叶斯计算详情
- `GET /api/models/predict/group/{group}/{idx}` - 三模型对比

### 训练
- `GET /api/training/status` - 查看训练状态
- `POST /api/training/start` - 启动模型训练
- `GET /api/training/results` - 查看训练结果

## 📊 性能优化

系统采用**按需加载**策略：
- ✅ 页面加载 <1 秒
- ✅ 只在用户展开小组时才加载详细数据
- ✅ 避免批量预加载导致的性能问题

## 📝 待实现功能

- [ ] 比分预测（泊松回归模型）
- [ ] 大小球预测
- [ ] 预测验证机制（待揭晓/已命中/未命中）
- [ ] Agent风格化展示
- [ ] 详细分析文案生成

## 📄 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！