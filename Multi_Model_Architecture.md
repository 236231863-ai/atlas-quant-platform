# Multi Model Architecture
## Components
- ModelNode: model_id, provider, capabilities, cost, speed, quality_score
- ModelRegistry: register, remove, evaluate, select_best
- ModelCapabilityProfile: analysis_depth, max_context, modalities
## Supported Providers
- OpenAI compatible API
- Local LLM
- Mock Model (testing)
