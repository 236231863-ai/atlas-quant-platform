# Sprint 13 Architecture Plan - Autonomous Research Laboratory

## Phase 0: Architecture Review

### Existing Reusable Modules
- engine/knowledge/ - KnowledgeBase, ResearchMemory, ExperimentArchive
- engine/research/ - ResearchLoopEngine
- engine/execution/ - ExperimentRunner
- engine/scheduler/ - ExperimentScheduler
- engine/strategy_generator/ - StrategyGenerator
- engine/intelligence/ - ResearchDirector, ResearchAdvisor, AgentSystem
- engine/evolution/ - StrategyEvolutionEngine

### New Modules (Sprint 13)
- engine/discovery/ - ResearchDiscoveryEngine (Phase 1)
- engine/patterns/ - PatternMiningEngine (Phase 2)
- engine/strategy_generator/ - StrategyFactory upgrade (Phase 3)
- engine/distributed/ - ExperimentBatchEngine (Phase 4)
- engine/benchmark/ - ResearchBenchmarkEngine (Phase 5)
- engine/research/ - ContinuousResearchLoop (Phase 6)
- engine/intelligence/ - ResearchDirectorV3 (Phase 7)
- engine/dashboard/ - ResearchDashboardService (Phase 8)

### Dependency Graph
- Phase 1 (Discovery) -> No deps
- Phase 2 (Patterns) -> Phase 1 (uses discoveries)
- Phase 3 (Factory) -> Phase 2 (uses patterns), evolution/, knowledge/
- Phase 4 (Distributed) -> scheduler/, execution/
- Phase 5 (Benchmark) -> backtest/, scoring/
- Phase 6 (Loop) -> Phase 1,2,3,4,5, knowledge/
- Phase 7 (Director) -> Phase 6, knowledge/, graph/
- Phase 8 (Dashboard) -> All phases

### Risk Analysis
- Risk 1: Phase 3 depends on Phase 2 - sequential required
- Risk 2: Phase 6 depends on all previous phases - integration complexity
- Risk 3: 500 tests across 8 phases - test capacity
