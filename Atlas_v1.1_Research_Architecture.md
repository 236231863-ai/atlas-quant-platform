# Atlas Quant Platform v1.1 - Research Architecture

## Overview

Upgrade from quantitative analysis platform to advanced research platform.
All modules maintain clean architecture: Engine pure, AI consumes Engine only.

## Architecture

```
Research Layer (new)
  Probability Engine (Bayesian/Markov/Calibration)
  ML Research Layer (FeaturePipeline/ModelAdapter/Evaluation)
  Portfolio Optimizer (Generator/Diversity/Scoring)
  ModelRegistry (versioned experiment tracking)

Existing Layer
  Analysis Engine / Backtest Engine / Strategy Engine
  Feature Engine / Intelligence Engine

Data Flow
  DrawRecord[] -> FeaturePipeline -> FeatureVector
  FeatureVector -> ML ModelAdapter -> Evaluation
  Bayesian/Markov -> Analysis Results
  Combinations -> DiversityOptimizer -> PortfolioScore
  All Results -> ModelRegistry -> AI ResearchAgent
```

## Key Features

- Bayesian analysis with Beta-Binomial conjugate model
- Markov chain state transition analysis (HOT/NORMAL/COLD)
- Probability calibration with Brier score and confidence adjustment
- ML pipeline: 11-dim feature vectors from 5 feature calculators
- ModelAdapter abstract interface (RF/XGBoost/LightGBM)
- Portfolio combination optimization with diversity scoring
- ModelRegistry for experiment tracking
- AI-assisted research with natural language explanations
