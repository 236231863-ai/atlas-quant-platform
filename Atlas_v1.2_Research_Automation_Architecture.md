# Atlas Quant Platform v1.2 - Research Automation Architecture

## Overview

Upgrade from research platform to automated quant research system.
All modules maintain clean architecture: Engine pure, AI consumes Engine only.

## Architecture

```
Automation Layer (new)
  Bayesian Optimization Engine
  Genetic Portfolio Optimizer
  Hidden Markov Model Engine
  Dataset Versioning System
  Model Training Pipeline
  Automated Research Loop
  AI Research Agent v3

Data Flow
  Historical Draws -> DatasetRegistry -> TrainingPipeline -> ModelRegistry
  Parameters -> BayesianOptimizer -> Optimal Parameters
  Combinations -> GeneticPortfolioOptimizer -> Optimal Portfolio
  Observations -> HMMEngine -> State Analysis
  Experiments -> ResearchLoopEngine -> Hypotheses + Recommendations
  All Results -> AutonomousResearchAdvisor -> Research Questions + Analysis
```

## Key Features

- Bayesian optimization with Expected Improvement
- Genetic algorithm for portfolio optimization
- Hidden Markov Model for state analysis
- Dataset versioning with hash validation
- Training pipeline with pluggable components
- Automated research hypothesis generation
- AI-powered research question generation and experiment analysis
