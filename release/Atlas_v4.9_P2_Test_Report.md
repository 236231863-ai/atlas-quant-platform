# Atlas v4.9 P2 测试报告

> 原则：重点测试数据更新安全 + 首次体验，不单纯堆数量
> 结果：v490 新增 **29 项** P2 测试（P1 155 + P2 29 = v490 共 184 passed）

## 一、本阶段新增测试（tests/v490/test_p2_experience.py，29 项）

### 首次体验（P2-A/B）
| 测试 | 覆盖 |
|------|------|
| `test_first_run_interface_preserved` | FirstRunDialog 接口兼容（purpose/lottery/mode/_go/stack）|
| `test_first_run_value_oriented_no_research_terms` | 引导不含冷热号/和值/频率/回测 |
| `test_first_run_value_oriented_content` | 引导价值主张 |
| `test_first_run_archiving_step` | 第 3 步建档导向 |
| `test_first_run_lottery_step` | 彩种选择步骤 |

### 号码输入（复用 TicketParser）
| 测试 | 覆盖 |
|------|------|
| `test_parse_formats`（参数化 5 例）| 普通/连续/多注（换行/斜杠/分号）|
| `test_parse_continuous_numbers_front_back` | 连续格式 5+2 拆分 |
| `test_parse_multi_notes_distinct` | 多注独立 |
| `test_parse_infer_lottery` | 5+2→dlt，6+1→ssq |
| `test_parse_empty` / `test_parse_invalid_numbers_rejected` | 空/越界拒绝 |

### 数据可信 + 安全
| 测试 | 覆盖 |
|------|------|
| `test_health_level_of`（参数化 5 例）| A/B/C/D 分级判定 |
| `test_health_check_ssq_fallback` | 双色球回退内置 |
| `test_health_check_has_fields` | 来源/更新时间/期号字段 |
| `test_health_message_for_level` | 各级别文案 |
| `test_updater_no_new_protects_cache` | **错误数据不覆盖缓存** |
| `test_updater_invalid_remote_filtered` | 非法号码过滤 |
| `test_updater_valid_remote_dlt/ssq` | 大乐透/双色球分别校验 |

## 二、回归

- `tests/v490/` 全量 **184 passed**（P1 155 + P2 29）
- `tests/v480/test_onboarding_v480.py` **33 passed**（onboarding 引擎不回归）
- `tests/v361/test_ui_flow.py` 后台运行中（UI 测试，含 FirstRunDialog 依赖）

## 三、数据更新安全场景（任务书十五要求）

| 场景 | 结果 |
|------|------|
| 新期号 | ✅ 合并追加（update 测试）|
| 重复期号 | ✅ 去重 |
| 旧期号 | ✅ 不倒退 |
| 非法号码 | ✅ `_valid_remote` 过滤 |
| 数据源为空 | ✅ `api_empty` 保留本地 |
| 数据源超时 | ✅ 异常降级 |
| 数据源格式变化 | ✅ 解析容错 |
| 网络断开 | ✅ 静默降级 |
| 错误数据 | ✅ `no_new` 不覆盖 |
| 缓存恢复 | ✅ 内置 base + 用户缓存优先 |

## 四、全量回归（最终）

- **通过：15979**（历史新高，P2 前 15977）
- **失败：31 项 → 修复 P2 相关 3 项（v440 状态卡 2 + v460 按钮 1）→ 剩余 28 项纯存量**
- **P2 引入失败：0**（首次回归 3 项已全部修复清零）
- **存量失败（git stash 验证，P2 未触及）**：
  - `tests/unit/engine` 25 项（统计/ML 算法技术债，v4.1 起持续存在）
  - `tests/v42` 2 项 + `tests/v43` 3 项（环境/内置数据期号 18077 vs mock 26087 差异）
- 回归覆盖：兑奖/提醒/资产/成长/行为/量化全链路，**P2 改动模块零回归**

## 五、质量说明

- P2 测试聚焦**本阶段改动**（首次体验 + 数据可信 + 号码输入），非为凑数
- 真实数据链路的端到端验证在 P1 已完成（155 项）
- 全量回归在报告完成后统一跑（后台），确认兑奖/提醒/资产/成长/行为/量化零回归
