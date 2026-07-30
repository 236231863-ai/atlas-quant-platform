# Atlas Quant Platform - Knowledge System

## Overview

The Knowledge System provides long-term research memory for the Atlas Quant Platform.

## Components

### KnowledgeBase
- Store: Hypothesis, Experiment, Result, Failure reason, Conclusion
- Features: Tags, Confidence scores, Parent relationships
- Query: search(), similar_experiments(), retrieve_context(), cluster_by_topic(), by_tag(), by_type()

### ResearchMemory
- record_hypothesis(id, content, tags, confidence)
- record_experiment(id, content, tags, parent)
- record_conclusion(id, content, tags, confidence)

### ExperimentArchive
- Archive experiments for long-term storage
- find_by_tag() for retrieval

## Usage

```python
kb = KnowledgeBase()
kb.add(KnowledgeRecord(id="h1", type="hypothesis", content="Gap weight > 0.3 improves Sharpe",
       tags=["gap", "sharpe"], confidence=0.5))
similar = kb.similar_experiments("h1")  # Find related experiments
results = kb.search("gap")  # Search by content or tags
```

## Integration

- KnowledgeBase feeds into Research Graph
- ResearchMemory connects to Strategy Evolution Engine
- ExperimentArchive integrates with ModelRegistry
