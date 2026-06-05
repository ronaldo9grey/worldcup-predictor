# 数据源架构文档

## 概述

为世界杯预测系统创建了数据源抽象层，支持多种数据源的灵活切换。

## 文件结构

```
backend/
├── data/
│   ├── sources/               # 数据源模块
│   │   ├── __init__.py        # 模块入口
│   │   ├── base.py            # 基类定义
│   │   ├── mock_source.py     # 模拟数据源（现有静态数据）
│   │   ├── balldontlie_source.py  # BALLDONTLIE API 数据源
│   │   └── factory.py         # 数据源工厂
│   └── .env.example           # 配置示例
│
├── services/
│   └── data_service.py        # 统一数据服务
│
└── api/
    └── data_service_api.py    # 数据服务 API
```

## 使用方式

### 1. 环境变量配置

```bash
# 设置数据源类型
export DATA_SOURCE=mock  # 或 balldontlie

# BALLDONTLIE API Key（如果使用）
export BALLDONTLIE_API_KEY=your_api_key
```

### 2. API 接口

| 接口 | 说明 |
|------|------|
| `/api/data/source` | 获取当前数据源信息 |
| `/api/data/teams` | 获取所有球队 |
| `/api/data/teams/{code}` | 获取单个球队 |
| `/api/data/groups` | 获取所有小组球队 |
| `/api/data/groups/{group}` | 获取小组球队 |
| `/api/data/matches` | 获取比赛列表 |
| `/api/data/standings/{group}` | 获取积分榜 |
| `/api/data/rankings` | 获取FIFA排名 |
| `/api/data/refresh` | 刷新数据 |
| `/api/data/switch-source` | 切换数据源 |

### 3. 切换数据源

**方式一：环境变量**

```bash
export DATA_SOURCE=balldontlie
export BALLDONTLIE_API_KEY=your_api_key
systemctl restart worldcup-predictor
```

**方式二：API 调用**

```bash
curl -X POST "http://localhost:8011/api/data/switch-source?source_type=balldontlie&api_key=your_key"
```

## 数据源对比

| 数据源 | 实时数据 | API Key | 适用场景 |
|--------|----------|---------|----------|
| mock | ❌ | 不需要 | 开发测试、世界杯前 |
| balldontlie | ✅ | 需要（免费） | 世界杯期间 |

## 后续工作

1. **改造现有 API**：逐步将现有 API 改为使用 DataService
2. **添加更多数据源**：FIFA 官方 API、Sportmonks 等
3. **实现数据同步**：世界杯开始后启用自动刷新
4. **添加监控告警**：数据源健康检查、异常通知