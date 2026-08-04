# Atlas Quant Platform Changelog

## [v4.6.0] - 2026-08-04
### 真实用户运营验证阶段
### Added
- engine/user_analytics: AnalyticsTracker（8类事件+premium事件）、FunnelBuilder（漏斗）、RetentionBuilder（D1/D3/D7）
- engine/draw_monitor/reminder_schedule: ReminderScheduler（开奖前24h/3h + 开奖后提醒，Task Scheduler 唤起）
- 首次引导价值导向升级（欢迎文案 + onboarding start/complete/drop 事件）
- 首页兑奖汇总卡片（待开奖/已中奖/待领取金额）
- engine/asset_center/monthly: MonthlyReportBuilder（月度购买/中奖/净收益 + 诚实负期望）
- engine/premium/feature_test: PremiumFeatureTest（4高级功能 + premium_view/click 埋点，不开发支付）
### Changed
- Version 4.6.0 (window title)
### Tests
- tests/v460 新增 1076 场景（≥1000），覆盖用户事件/后台提醒/首次启动/兑奖/资产/商业化

## [v4.5.0] - 2026-08-04
### 可信开奖数据与用户留存系统
### Added
- engine/data_center: DataProvider 链（官方/备用/本地缓存）+ DrawValidator 校验（期号递增/日期/前后区/范围）+ DataHealthReport
- engine/draw_monitor: DrawMonitor（开奖日监控：大乐透一/三/六、双色球二/四/日）+ WindowsNotifier（Toast→msg→日志 后台提醒）
- 兑奖信任升级：AutoClaimReport 增加 issue/data_source/updated_at/verified + trust_text
- 用户行为埋点：draw_reminder_received/draw_opened/claim_completed + UserBehaviorReport
- tools/atlas_worker.py: 同步后自动发后台提醒
### Changed
- Version 4.5.0 (window title)
### Tests
- tests/v450 新增 279 场景（数据可信/监控/提醒/兑奖信任/埋点）

## [v4.4.0] - 2026-08-04
### Data Reliability & Live Draw System
### Added
- engine/live_draw: LiveDrawService（后台开奖同步：大乐透一/三/六、双色球二/四/日 + DrawUpdated/NewIssue/UpdateFailed/Skipped 事件）
- engine/live_draw/background: BackgroundServiceManager（Windows 计划任务后台服务：安装/卸载/状态 + 开机启动）
- engine/live_draw/health: DataHealthCenter（数据可信等级 A<12h/B 12-24h/C>24h/D 异常）
- engine/live_draw/claim_link: AutoClaimLink（live_draw→claim_center→notification 自动兑奖联动）
- tools/atlas_worker.py: 升级为后台同步 worker（sync_once/run_loop）
- 首页开奖状态卡片（距离下一开奖/最新开奖/数据可信/待兑奖）
### Changed
- 启动后台线程静默同步（保留）；新增计划任务后台服务（软件关闭仍同步）
- Version 4.4.0 (window title)
### Tests
- tests/v440 新增 859 场景（≥800），覆盖数据更新/API失败/网络异常/新期发现/防旧覆盖/后台服务/自动兑奖

## [v4.3.1] - 2026-08-03
### Hotfix: 开奖数据实时更新
### Fixed
- 开奖信息不再停留在打包时刻：新增 engine/data_center_v2/updater（IncrementalUpdater）
- 启动时后台静默拉取官方 API 最新开奖，按期号合并去重，写回 ~/.atlas/raw/{lottery}_history.csv
- data_loader 用户缓存优先（~/.atlas/raw > 项目 > 内置），来源标注「实时更新数据」
- 首次更新以内置 1200 期为 base 合并（不丢历史）
- 24h 限频 / 无网静默降级 / 不阻塞 UI
- 实测：更新后最新期 26087（2026-08-03）· 共 1201 期 · 可信等级 A
### Tests
- tests/v43/test_updater_v431.py 新增 32 场景（合并/去重/限频/写缓存/静默降级/用户缓存优先）

## [v4.3.0] - 2026-08-03
### User Retention Loop（留存闭环，不新增大量功能）
### Added
- engine/user_events: EventTracker 用户行为事件（ticket_saved/reminder_shown/claim_viewed/claim_confirmed/report_generated）, 验收「用户行为发生」
- engine/claim_center: 自动兑奖中心（4 状态机：等待开奖/已开奖待查看/已查看/已兑奖 + auto_claim 自动匹配通知）, 299 tests
- engine/asset_center: 彩票资产中心（累计购买/中奖/中奖率/净收益/最大单次中奖 + 风险等级 A-D + 年度报告）, 181 tests
- engine/growth_system: 用户成长系统（保存/兑奖/报告次数 + 连续使用周数 + 成长等级 + 年度 Atlas Report）, 101 tests
- 首页重构第二版（3 秒价值首屏，移除平均和值/奇偶/冷热研究指标）, 112 tests
- 真开奖提醒系统 P1（桌面通知 + 倒计时 + 提醒事件）, 153 tests
### Changed
- TicketRecord 新增 claimed 字段（修复重启丢失兑奖状态 bug）
- 首页每日智能摘要（研究指标）移至「数据分析」页
- Version 4.3.0 (window title)
### Tests
- tests/v43 新增 846 场景（≥800），全量回归待统计

## [v4.0.0] - 2026-08-03
### Personal Decision Intelligence Layer
### Added
- engine/user_behavior: BetBehaviorAnalyzer (投注/月年投入/追号/高频周期/停止率/风险等级), 256 tests
- engine/budget_manager: BudgetPlanner (月/年预算、占比、超额提醒、健康度), 239 tests
- engine/personal_review: PersonalReviewEngine (历史复盘/中奖/收益比/最高周期), 308 tests
- QuantReport 升级个人视角（号码/概率/资金/行为/改进建议 5 部分），禁止推荐号码, 232 tests
- AI 助手 personal_analyze 工具（PendingTask>兑奖>个人>量化>LLM）, 376 tests
- 个人中心页面（我的票据/投入/中奖/风险/报告/趋势）, 110 tests
- 真实用户流程验证（30 秒闭环）, 216 tests
### Changed
- Version 4.0.0 (window title), 9 navigation pages

## [v3.9.0] - 2026-08-02
### Lottery Quant Intelligence Layer
### Added
- engine/lottery_quant: probability / structure / simulation / risk / portfolio / backtest / report
- Probability engine: DLT/SSQ prize odds (1/21,425,712 / 1/17,721,088), 125 tests
- Structure analyzer: parity/size/zone/sum/span/consecutive/duplicate/historical deviation, 155 tests
- Monte Carlo simulation: 100k-draw coverage, 247 tests
- Risk engine: annual investment / max loss / expected return / loss probability / risk level A-D, 112 tests
- Portfolio analyzer: duplicate rate / correlation / coverage / concentration, 171 tests
- Strategy backtest: hot/cold/balanced/random vs random baseline, 210 tests
- AI assistant quant_analyze tool (priority: PendingTask > prize > quant > LLM), 253 tests
- Desktop quant center page (workbench 🎯 entry), 26 UI tests
- Quant report generator (Markdown/PDF/PNG), 83 tests
- All outputs carry randomness disclaimer; no prediction claims
### Changed
- Version 3.9.0 (window title), 8 navigation pages

## [v3.8.2-P1] - 2026-08-02
### AI Assistant Prize Task State Recovery
### Added
- engine/task_context: PendingTaskManager (user_id/task_type/lottery/tickets/dates/expiry)
- Confirm-reply recovery: 是/好的/确认/按这个算 -> auto-resume pending prize task
- Continuous-number ticket parsing: 13212326330112 -> 13 21 23 26 33 + 01 12 (15/30/100 notes)
- Prize report enhancement: purchase/draw date, issue, note count, won notes, per-note detail
- 476 tests (tests/v382_p1)
### Fixed
- Confirm reply ("是的") no longer lost to chat; auto-resumes pending task
- No more "请提供开奖结果/请输入更多信息/我无法计算" in the confirmed flow
### Changed
- Version 3.8.2 (window title)

## [v3.7.2] - 2026-08-02
### User Task Understanding Fix
### Added
- engine/lottery_intent: LotteryIntentRouter + TicketParser + DrawResultMatcher + PrizeCalculator
- AI assistant prize calculation flow (natural language -> prize report)
- 312 tests (tests/v372)
### Changed
- Version 3.8.0 (window title)

## [v3.8.0] - 2026-08-02
### User Value Validation & Commercial Intelligence
### Added
- user_intelligence/v3, value_score, product_value, subscription/v2, feedback_intelligence, product_director_v2
- personal dashboard (value score/level/AI suggestions/history)
- docs/product 4 maps, docs/business 3 reports
- 1008 tests (tests/v380)

## [v3.7.1-beta] - 2026-08-02
### Beta Launch Infrastructure
### Added
- docs/beta: Beta_Test_Plan / Beta_User_Guide / Feedback_Process
- engine/beta: BetaUserManager (id/batch/version/feedback)
- engine/product_analytics_v2: app events + ProductUsageReport
- backend/feedback: Feedback/BugReport/FeatureRequest/Rating + status machine
- release_center: version info / release notes / install guide / FAQ
- desktop help center dialog + feedback entry
- 528 tests (tests/v371)
### Changed
- Version 3.7.0 -> 3.7.1-beta

## [v3.7.0] - 2026-08-02
### User Validation & Product Intelligence
### Added
- docs/product: positioning / personas / value proposition
- engine/onboarding: FirstSuccessFlow + UserAchievement
- engine/daily_intelligence: DailySummary (no prediction)
- data: 1200 DLT draws + 500 SSQ draws (official APIs), DataQualityReport updated_at
- engine/user_feedback_v2: behavior tracker + report
- backend/subscription: Community/Professional/Research editions + feature flags
- 742 tests (tests/v370), 5 delivery reports, screenshots, user testing report
### Changed
- Version 3.6.1 -> 3.7.0 (window title)

## [v3.6.1] - 2026-08-02
### Product Trust & Real Usage Upgrade
### Added
- engine/data_center_v2: DataSourceManager (CSV/Excel/API/Database) + DataQualityReport
- 520 real DLT draws from official sporttery API (2023-02 ~ 2026-08)
- engine/evaluation_v2: temporal sample split + random baseline + performance report + disclaimer
- engine/export: Markdown/CSV/PNG/PDF exporters
- desktop/health: global excepthook + crash recovery + log export + health check
- Onboarding 3-step wizard (purpose -> lottery -> mode)
- Dashboard data sufficiency warning + trust level
- 800+ engineering tests (tests/v361)
### Changed
- Version 3.6.0 -> 3.6.1

## [v3.5.2-E2] - 2026-08-02
### Engineering Sprint E2 - Test Technical Debt Fix
### Fixed
- 51 test failures resolved (76 -> 25, 67%)
- test_analyzers: correct TradeRecord bonus fields + volatility/sharpe test data
- test_desktop: matplotlib backend_qt5agg -> qtagg (PySide6 support)
- test_docker_release: utf-8 encoding + current version assertions + .dockerignore
- test_backtest_integration: complete setup (sim/agg/report)
- test_gap/frequency/distribution: out-of-range number fixes + correct expectations
- engine/scheduler: expose max_retries param (backward compatible)
- engine/ml/models: fix set_params for sklearn 1.9 estimator API
- test_frontend_api/gap: self-contradictory assertions fixed
### Known Debt
- 25 deep algorithm/ML assertion failures remain (sklearn 1.9 behavior, strategy/report/product_intelligence), deferred to E2b

﻿# Atlas Quant Platform Changelog

## [v3.5.2] - 2026-08-02
### Engineering Sprint E1 - Project Engineering Foundation
### Added
- Engineering: Sprint_E1_Architecture.md, Git_Workflow.md, Dependency_Report.md
- Git governance: LICENSE, CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md
- VSCode workspace: launch.json, tasks.json, extensions.json, settings.json
- Dependency management: requirements family (5 envs) + constraints.txt
- Unified build pipeline: build.ps1 / build.bat / build.sh
- Executable packaging: Atlas.exe / Atlas_CLI.exe / Atlas_Worker.exe + specs
- Installer: Atlas_Setup.exe (Inno Setup)
- Docker orchestration: backend/frontend/nginx/postgres/redis
- GitHub CI/CD: ci.yml + release.yml + PR template
- Release engineering: Portable/Debug zips + notes + checklists
- Documentation: 10 guides (QuickStart/Developer/User/Install/Deploy/API/Plugin/Architecture/FAQ/Marketplace)
- Official project structure: examples/ + assets/ completed
- Engineering tests: tests/engineering/ (55 tests)
### Changed
- README updated with engineering standards and badges
- Unified version to v3.5.2
### Note
- No engine, AI, research, or database business logic modified

## [v3.5.1] - 2026-07-30
### Added
- Branding & Product Identity (logos, version, editions)
- Desktop Application Launcher (env detect, crash recovery)
- Cross-Platform Installer (wizard, shortcuts, uninstall)
- First Run Experience (language, theme, workspace, account)
- Help Center (FAQ, diagnostics, support contact)
- Auto Updater (version check, download, install, rollback)
- 800 new packaging tests
### Changed
- Product name finalized as Atlas Quant Platform v3.5.1
### Note
- No engine, AI, research, or database modules modified

## [v3.5.0] - 2026-07-30
### Added
- Reliability Engine (platform scoring, module health, trend analysis)
- Observability v2 TraceEngine (API/Workflow/Agent/Research/Decision traces)
- Resilience RecoveryEngine (auto-detect, auto-recover, recovery records)
- Quality Gate Engine (code changes, API compatibility, test coverage)
- Release Intelligence Engine (canary, risk assessment, auto-rollback)
- Security Audit Engine (API abuse, permissions, plugins, datasets)
- Platform Director (unified health, version, risk, security management)
- Platform Dashboard v18 + API - Atlas Control Center (6 endpoints)
- 1000 new tests

## [v3.4.0] - 2026-07-30
### Added
- Ecosystem Operation Engine (health monitoring, issue detection)
- Autonomous Growth Intelligence (growth prediction, opportunity discovery)
- Ecosystem Strategy Planner (vision, goals, resource allocation)
- Creator Intelligence (engagement, revenue, growth potential)
- Enterprise Success Intelligence (adoption, ROI, churn prediction)
- Autonomous Governance (policies, compliance, enforcement)
- Ecosystem Director (unified ecosystem orchestration)
- Ecosystem Dashboard v17 + API (health, growth, strategy, creators, enterprises)
- 1000 new tests

## [v3.3.0] - 2026-07-30
### Added
- Solution Creator Studio (draft->testing->review->published lifecycle)
- AI Asset Marketplace v2 (6 asset types, search, category, recommend, install, upgrade)
- Ecosystem Reputation System (5-dimension scoring, 4 creator levels)
- Expert Certification Network (4 expert types, skills, cases, certification)
- Enterprise Procurement Flow (Search->Evaluate->Trial->Approve->Purchase->Deploy)
- Asset License Economy (4 license types, revenue, author earnings)
- Ecosystem Intelligence (hot solutions, trends, demands, asset values)
- Marketplace Dashboard v16 + API (5 marketplace endpoints)
- 1000 new tests

## [v3.2.0] - 2026-07-30
### Added
- Industry Template System (6 industries, template registry, version management)
- Industry Knowledge Base (domain entities, relationships, search)
- Industry Workflow Engine (Input->Analyze->Review->Decision->Report)
- Industry Agent System (Finance, Retail, Research, Business agents)
- Industry Report Center (industry, enterprise, research, decision reports)
- Solution Marketplace (publish, install, license, evaluate solutions)
- Industry Data Connector (CSV, Database, API, Enterprise data)
- Industry Dashboard v15 + API (5 industry endpoints)
- 1000 new tests

## [v3.1.0] - 2026-07-30
### Added
- Enterprise Identity Layer (Organization, EnterpriseUser, 5 roles, invite/remove)
- Access Control System (RBAC, 6 resource types, 5 permissions, audit log)
- Multi-Tenant SaaS Layer (tenant isolation, quotas, configuration)
- Enterprise Research Workspace (projects, team collaboration, sharing)
- Operation Center (user/task/load/AI metrics, anomaly detection)
- Commercial Service Layer (3 plans, subscription, usage metering)
- Deployment Automation (environment management, health check)
- Enterprise Dashboard v14 + Enterprise API (5 endpoints)
- 1000 new tests

## [v3.0.0] - 2026-07-30
### Added
- User Behavior Intelligence Layer (9 event types, interest analysis, churn prediction)
- User Digital Profile System (6 levels, profile evolution, next stage prediction)
- Product Feedback Learning System (FeatureValueScore, ProductKnowledgeBase)
- AI Product Manager (user needs analysis, roadmap generation, value scoring)
- Auto Product Experiment System (A/B testing, feature experiments)
- Product Evolution Engine (Keep/Improve/Replace/Remove analysis)
- Business Intelligence Engine (revenue analysis, retention, growth opportunities)
- Dashboard v13 + Product Intelligence API (6 endpoints)
- 1000 new tests

## [v2.9.0] - 2026-07-30
### Added
- System Observability Engine (health monitor, module usage, agent performance)
- Intelligence Evaluation Engine (prediction accuracy, decision quality, calibration)
- User Feedback Intelligence (user actions, preference learning, effective/failed analysis)
- Autonomous Maintenance Engine (health check, issue detection, optimization)
- Reality Learning Engine (prediction records, success/failure factors)
- Research Director v11 (system health, evaluation, maintenance orchestration)
- Production Intelligence Dashboard (health, AI performance, user value, modules)
- Production Operation API (/health, /intelligence-score, /modules, /improvements)
- 1000 new tests

## [v2.8.0] - 2026-07-30
### Added
- Action Planning Engine (goal decomposition, step sequencing, resource planning)
- Execution Simulation Engine (time/resource/risk/probability simulation)
- Feedback Intelligence (prediction/action/result analysis, lessons learned)
- Adaptive Strategy Engine (parameter adjustment, strategy mutation)
- Autonomous Workflow Engine (6-state lifecycle: Created->Planning->Executing->Reviewing->Learning->Completed)
- Research Director v10 (action planning, execution, feedback, adaptation, workflow)
- Autonomous Intelligence Dashboard (action timeline, execution status, learning curve)
- Action API (/plans, /create, /status, /history, /learning)
- 1000 new tests

## [v2.7.0] - 2026-07-30
### Added
- Causal Intelligence Engine (CausalGraph, CausalAnalyzer, CounterfactualEngine)
- Decision Simulation Engine (scenarios, simulation, comparison)
- Risk Intelligence Upgrade (prediction, propagation, risk radar)
- Opportunity Discovery Engine (market, technology, research opportunities)
- Decision Memory System (records, effective/failed analysis, lessons)
- Research Director v9 (causal analysis, scenario sim, risk, opportunity)
- Decision Intelligence Dashboard (timeline, risk map, opportunities)
- Decision API (/simulate, /latest, /history, /risk, /opportunities)
- 1000 new tests

## [v2.6.0] - 2026-07-30
### Added
- Data Intelligence Hub (source registry, lineage tracking, quality scoring)
- News & Information Intelligence (news collection, topic analysis, sentiment)
- Knowledge Fusion Engine (multi-source entity resolution, relation building)
- Real Time Signal Engine (trend, risk, opportunity, anomaly signals)
- Research Environment Simulator (scenarios, stress testing)
- Global Intelligence Dashboard (world view, research environment)
- Research Director v8 (world observation, change detection, goal generation)
- 1000 new tests

## [v2.5.0] - 2026-07-30
### Added
- User Intelligence Engine (6 user levels, behavior analysis, recommendations)
- Personal AI Research Assistant v2 (memory, recommendations, explainability)
- Community Platform v2 (strategy sharing, research publications, forking)
- Recommendation Marketplace (4 similarity algorithms, multi-asset)
- Growth Intelligence Engine (A/B testing, funnel, retention, churn)
- Product Dashboard (user home, research timeline, knowledge graph)
- Mobile Preparation (React Native, API layer, notifications)
- 1000 new tests

## [v2.4.0] - 2026-07-30
### Added
- Commercial Business Layer (License, Subscription, Revenue)
- Data Center Infrastructure (Ingestion, Quality, Repair, Version)
- Model Hub System (Registry, Version, Deployment, Monitor, Rollback)
- Atlas Python SDK (client library for developers)
- Atlas JavaScript SDK (client library for web)
- Atlas CLI (command-line platform management)
- Enterprise Admin Center (user management, audit, operations)
- Production Deployment (Docker, K8s, monitoring, backup)
- 1000 new tests

## [v2.3.0] - 2026-07-29
### Added
- Open API Platform (API Gateway, DeveloperAPIKey, v3 endpoints)
- Plugin Marketplace (PluginRegistry, lifecycle, validation)
- Strategy Marketplace (assets, forking, rating, licensing)
- Data Marketplace (datasets, versioning, access control)
- Developer Center (dashboard, API management, docs)
- AI Agent Marketplace (custom agents, categories, sandbox)
- Enterprise Workspace (orgs, teams, members, permissions)
- Ecosystem Dashboard (developer/plugin/marketplace metrics)
- 1200 new tests

## [v2.2.0] - 2026-07-29
### Added
- Product Analytics System (EventTracker, ProductMetricsEngine)
- User Intelligence Profile (4 user types, behavior analysis)
- Personal AI Research Assistant (history memory, suggestions)
- Strategy Community (posts, comments, sharing)
- Research Ranking System (5-dimension leaderboard)
- Commercial Foundation (FREE/PRO/RESEARCH plans)
- Growth Experiment System (A/B testing framework)
- Dashboard Upgrade (User/Community/Admin dashboards)
- 1000 new tests

## [v2.0.0] - 2026-07-29
### Added
- Research Governance System (policies, compliance, approval)
- AI Research Department System (6 departments, agent assignment)
- Researcher Career System (5 career levels, promotion)
- AI Paper & Publication System (generate, review, publish, archive)
- Research Review Committee (5 specialized reviewers, peer review)
- Research Asset Management (6 asset types, lifecycle)
- Institution Director v1 (central coordination, institution summary)
- Institution Dashboard (departments, scientists, publications, assets)
- 1000 new tests

## [v1.9.0] - 2026-07-29
### Added
- Multi Model Intelligence Layer (ModelRegistry, ModelRouter)
- Research Personality System (PersonalityProfile, adaptation)
- Global Research Node Network (distributed nodes, aggregation)
- Long Horizon Research Mission System (missions, milestones)
- Research Knowledge Exchange (insight publishing, matching)
- Research Intelligence Router (routing, model/agent/node selection)
- Research Director v7 (global resource allocation, coordination)
- Global Intelligence Dashboard (model/node/agent/mission data)
- 900 new tests

## [v1.8.0] - 2026-07-29
### Added
- Autonomous Goal Discovery Engine (ResearchGoalGenerator)
- Research Strategy Planner v2 (roadmap, dependencies, milestones)
- Knowledge Transfer Engine (cross-domain insights)
- AI Expert Council (5 scientists, proposals, debates, decisions)
- Civilization Engine v2 (eras, breakthroughs)
- Self Improvement System (capability, weakness detection, improvement)
- Research Director v6 (goal selection, council, improvement)
- Civilization Dashboard (timeline, goals, knowledge, breakthroughs)
- 800 new tests

## [v1.7.0] - 2026-07-29
### Added
- Agent Economy Foundation (AgentScore, EconomyEngine)
- Agent Reputation System (5 metrics, 5 ranks)
- Agent Evolution Engine (skill mutation, version tracking)
- Research Competition System (tournament evaluation)
- Research Resource Allocation (budget, priority, workload)
- Research Marketplace (offers, bids, contracts)
- Civilization Memory (eras, discoveries, generations)
- Research Director v5 (economy, competition, promotion)
- Dashboard Ecosystem Layer (ranking, evolution, timeline)
- 700 new tests

## [v1.6.0] - 2026-07-29
### Added
- Agent Communication Protocol (ResearchTask/Message/Result/Feedback)
- Research Agent Expansion (6 specialized agents)
- Multi-Agent Collaboration System (ResearchTeamCoordinator)
- Research Debate Engine (arguments, voting, decisions)
- Research Memory Upgrade (reasoning, success/failure reasons)
- Distributed Research Node (register, assign, return)
- Research Director v4 (team formation, debate management)
- Research Dashboard v2 (agent status, team activity, debate history)
- 600 new tests

## [v1.5.0] - 2026-07-29
### Added
- Research Discovery Engine (anomaly detection, degradation detection, opportunity scoring)
- Pattern Mining Engine (correlations, success/failure patterns)
- Strategy Factory (template generation, mutation, crossover)
- Massive Experiment Engine (batch creation, grouping, aggregation)
- Research Benchmark System (4-dimension scoring, cross-validation)
- Continuous Research Loop (automated cycles, weekly summaries)
- Research Director v3 (mission planning, portfolio management, roadmap)
- Research Dashboard Data Layer (structured visualization data)
- Architecture Plan + Development Order Guide
- 500 new tests

## [v1.4.0] - 2026-07-29
### Added
- Experiment Sandbox System (isolated environments)
- Experiment Definition Language (JSON specs)
- Experiment Scheduler (queue, priority, deps, retry)
- Experiment Execution Engine (single/batch/parallel)
- Research Scoring System (Performance/Risk/Quality)
- Strategy Generator (KB/Graph/History derived)
- Human Review Workflow (6 states)
- Research Director v2 (full lifecycle management)
- 366 new tests

## [v1.3.0] - 2026-07-28
### Added
- Research Knowledge Base (KnowledgeBase, ResearchMemory, ExperimentArchive)
- Strategy Evolution Engine (generational strategy improvement)
- Multi-Agent Research System (5 specialized agents)
- Research Graph (knowledge graph with traversal)
- Meta Learning Layer (optimizer performance tracking)
- Autonomous Research Planner (roadmap, prioritization)
- AI Research Director (objectives, duplicate detection, milestones)
- 324 new tests

## [v1.2.0] - 2026-07-28
### Added
- Bayesian Optimization Engine (Expected Improvement)
- Genetic Algorithm Portfolio Optimizer
- Hidden Markov Model Engine
- Dataset Versioning System
- Model Training Pipeline
- Automated Research Loop
- AI Research Agent v3
- 250+ new tests

## [v1.1.0] - 2026-07-28
### Added
- Advanced Probability Engine (Bayesian, Markov, Calibration)
- Machine Learning Research Layer (FeaturePipeline, ModelAdapter, Evaluation)
- Portfolio Combination Optimizer (Generator, DiversityOptimizer, PortfolioScore)
- ModelRegistry for experiment tracking
- AI Research Upgrade (probability explanation, model comparison, risk assessment)
- 200+ new tests


## [v1.0.0] - 2026-07-28
### Added
- Production Docker configuration (backend, frontend, database)
- OpenAI LLM adapter integration
- Automated data ingestion pipeline
- Data validation and backup system
- User workspace system (User, Workspace, Project)
- Release engineering automation
- Production environment configuration

### Changed
- Version bumped from v0.7.0 to v1.0.0
- Complete project hardening for production

## [v0.7.0] - Sprint 7 - Product Layer
- Web Dashboard (React+Vite+ECharts)
- Desktop Client (PySide6)
- Visualization charts (5 types)
- 100 tests

## [v0.6.0] - Sprint 6 - AI Research Assistant
- ResearchAgent, ModelExplainer, StrategyAdvisor, AnomalyDetector
- MockLLMAdapter for testing
- 120 tests

## [v0.5.0] - Sprint 5 - Strategy Optimization
- Feature Engine (5 calculators)
- Grid/Random search optimizer
- Strategy Tournament
- Experiment tracking
- 120 tests

## [v0.4.0] - Sprint 4 - Backtest & Strategy Lab
- TradeSimulator (walk-forward, no leakage)
- ResultAggregator (ROI, Sharpe, drawdown)
- StrategyRegistry + Evaluator
- 102 tests

## [v0.3.0] - Sprint 3 - Quant Engine Alpha
- Frequency/Gap/Distribution analysis engines
- Statistics engine (correlation, entropy)
- Monte Carlo simulation
- 95 tests

## [v0.2.0] - Sprint 2 - Data Foundation
- SQLAlchemy ORM + Alembic
- REST API (draws, statistics)
- DLT plugin with CSV import
- 82 tests

## [v0.1.0] - Sprint 1 - Architecture
- Clean Architecture + DDD
- Management system (00-08)
- Prompt Library (10 templates)
- Project skeleton

























