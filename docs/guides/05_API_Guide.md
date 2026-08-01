# API Guide

## 基础信息

- Base URL：`http://localhost:8000/api/v1`
- 认证：Bearer Token（`Authorization: Bearer <token>`）
- 格式：JSON

## 端点

### 数据

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/dashboard/summary` | 数据看板摘要 |
| GET | `/{lottery}/draws?limit=50` | 开奖记录列表 |
| GET | `/{lottery}/statistics` | 统计数据 |

### 策略与研究

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/strategies` | 策略列表 |
| POST | `/strategies` | 创建策略 |
| GET | `/experiments` | 实验列表 |
| POST | `/experiments` | 运行实验 |

## 示例

```bash
curl http://localhost:8000/api/v1/dashboard/summary

curl "http://localhost:8000/api/v1/dlt/draws?limit=5"
```

## 桌面端本地数据

桌面版（Atlas.exe）内置数据层，直接读取打包的 CSV，**不依赖**此 API。API 面向 Web 与外部集成。
