# Marketplace Guide

## 概述

Atlas Marketplace 面向策略/数据/插件的交易市场（企业版功能）。

## 发布内容

| 类型 | 说明 |
|------|------|
| 策略 | 经过回测验证的策略包 |
| 数据 | 彩种历史数据 |
| 插件 | 新彩种插件 |

## 发布流程

1. 准备发布包（策略 JSON / 数据 CSV / 插件目录）
2. 通过 CLI：`atlas publish <package>`
3. 平台审核后上架

## 入口

- Web：Marketplace 页面
- CLI：`atlas publish`
- API：`POST /api/v1/marketplace/items`

## 当前状态

Marketplace 模块为骨架实现，完整交易功能属于企业版后续 Sprint。
