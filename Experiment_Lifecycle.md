# Atlas Quant Platform - Experiment Lifecycle

## Complete Lifecycle

1. Research Idea / Hypothesis
2. Experiment Definition (JSON spec)
3. Sandbox Creation (isolated environment)
4. Experiment Queue (priority + dependencies)
5. Human Review (AI proposed -> Human approved)
6. Execution (runner with dataset/strategy/features/backtest)
7. Evaluation (scoring: performance + risk + quality)
8. Archive (knowledge base + graph update)
9. Strategy Generation (new candidates from results)

## States

Experiment Definition: DRAFT -> VALIDATED -> READY
Scheduler: CREATED -> QUEUED -> RUNNING -> SUCCESS/FAILED/CANCELLED
Review: AI_PROPOSED -> HUMAN_REVIEW -> APPROVED/REJECTED -> EXPERIMENT_RUNNING -> COMPLETED

## Key Principles

- Every experiment has unique ID, parameters, and random seed
- All experiments reproducible (complete spec + seed)
- Results feed back into knowledge base
- Human approval required for execution
- Multi-dimensional scoring (not just ROI)
