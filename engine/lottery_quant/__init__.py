"""lottery_quant - 彩票量化智能分析层（v3.9.0）。

将 Atlas 从「彩票兑奖工具」升级为「彩票量化分析助手」。

模块：
  probability/   概率计算引擎
  structure/     号码结构分析
  simulation/    蒙特卡洛模拟
  risk/          资金风险分析
  portfolio/     投注组合分析
  backtest/      策略回测（复用 evaluation_v2）
  report/        量化报告生成（复用 export）
  randomness/    随机性检验（v4.10：卡方/游程/自相关，证伪选号）
  quant_director 量化分析总控制器

原则：所有输出必须声明「彩票开奖结果具有随机性」，
     只提供统计分析、概率计算、历史研究、风险管理。
"""
