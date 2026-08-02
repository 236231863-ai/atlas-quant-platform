# Atlas Quant Platform v3.9.0 架构报告

> Lottery Quant Intelligence Layer 架构设计
> 日期：2026-08-02

---

## 1. 分层架构

```
engine/lottery_quant/          # v3.9.0 新增量化层
├── probability/               # 概率计算引擎（组合数学）
│   └── model.py               # ProbabilityModel / ProbabilityReport
├── structure/                 # 号码结构分析
│   └── analyzer.py            # StructureAnalyzer / CombinationScore
├── simulation/                # 蒙特卡洛模拟
│   └── monte_carlo.py         # SimulationEngine / SimulationReport
├── risk/                      # 资金风险分析
│   └── engine.py              # RiskEngine / RiskReport
├── portfolio/                 # 投注组合分析
│   └── analyzer.py            # PortfolioAnalyzer / PortfolioReport
├── backtest/                  # 策略回测
│   └── strategy.py            # StrategyBacktester（复用 evaluation_v2）
├── report/                    # 量化报告生成
│   └── generator.py           # QuantReportGenerator（复用 export）
└── quant_director.py          # 量化分析总控制器
```

## 2. 复用已有模块（原则3）

| 新模块 | 复用 | 说明 |
|--------|------|------|
| backtest | `engine/evaluation_v2` | run_backtest_with_evaluation + RandomBaseline |
| report | `engine/export` | MarkdownExporter / PDFExporter / PNGExporter |
| structure | `desktop/stats.py` | 奇偶/大小/和值/跨度统计口径 |
| quant_analyze | `engine/ticket_system` | TicketManager 读取票据 |
| quant_analyze | `engine/lottery_intent` | TicketParser 号码解析 |

## 3. AI 助手路由优先级（v3.9.0 Phase 7）

```
用户输入
  ↓
① PendingTask 确认（是/好的/确认/按这个算）→ 恢复兑奖任务
  ↓
② 兑奖工具（prize：中奖/奖金/兑奖）
  ↓
③ 量化工具（quant_analyze：分析/风险/模拟/覆盖/评分 + 强意图词加权）
  ↓
④ 普通 LLM（闲聊兜底）
```

量化强意图词（风险/模拟/结构/重复率/覆盖/组合评分/概率分析/分析）使量化请求优先于兑奖小词，避免「模拟一下中奖情况」误走兑奖。

## 4. 数据流

```
用户号码（自然语言/连续串）
  ↓ TicketParser
tickets [{front, back}]
  ↓ QuantDirector
  ├── StructureAnalyzer → 组合评分
  ├── dlt/ssq_probabilities → 概率模型
  ├── SimulationEngine → 模拟覆盖率
  ├── PortfolioAnalyzer → 组合风险
  ├── RiskEngine → 资金风险
  └── StrategyBacktester → 策略回测
  ↓ QuantReportGenerator
Lottery Quant Report（MD/PDF/PNG）
```

## 5. 关键设计决策

1. **组合数学概率**：用 `math.comb` 精确计算各奖级组合数（大乐透 21,425,712 总组合）
2. **确定性模拟**：`random.Random(seed)` 保证同 seed 结果可复现（测试确定性）
3. **随机基准对照**：复用 evaluation_v2 的 RandomBaseline，策略 ROI vs 随机基准 90% 区间
4. **免责声明贯穿**：每个 Report 内置 DISCLAIMER，禁止预测表达
5. **性能**：20,000 次模拟 0.2s；风险引擎 60 年模拟 <0.3s

## 6. 页面架构

```
MainWindow（8 页面）
  ├── 数据看板 / 数据分析 / 策略实验室 / 回测中心
  ├── AI 助手（quant_analyze 工具）
  ├── 研究报告 / 工作台（🎯 入口 → 量化中心）
  └── 量化中心（QuantPage：5 功能区）
```

## 7. 依赖

- 复用：evaluation_v2 / export / ticket_system / lottery_intent / data_center_v2
- 新增独立：lottery_quant（无循环依赖）
- 打包：atlas_desktop.spec 已加入 lottery_quant 全模块
