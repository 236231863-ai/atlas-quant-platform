"""ModelAdapter interface - supports RandomForest, XGBoost, LightGBM."""
from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class ModelConfig:
    model_type: str = "random_forest"
    n_estimators: int = 100; max_depth: int = 10; random_seed: int = 42
    learning_rate: float = 0.1; n_jobs: int = -1
    def to_dict(self): return asdict(self)

class ModelAdapter(ABC):
    @abstractmethod
    def fit(self, X: List[List[float]], y: List[float]) -> None:
        ...

    @abstractmethod
    def predict(self, X: List[List[float]]) -> List[float]:
        ...

    @abstractmethod
    def predict_proba(self, X: List[List[float]]) -> List[List[float]]:
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def is_trained(self) -> bool:
        ...

    @abstractmethod
    def get_params(self) -> Dict[str, Any]:
        ...

    @abstractmethod
    def set_params(self, **kwargs) -> None:
        ...

class RandomForestAdapter(ModelAdapter):
    def __init__(self, config: Optional[ModelConfig] = None):
        self._config = config or ModelConfig()
        self._model = None; self._trained = False
        from sklearn.ensemble import RandomForestClassifier
        self._model = RandomForestClassifier(
            n_estimators=self._config.n_estimators, max_depth=self._config.max_depth,
            random_state=self._config.random_seed, n_jobs=self._config.n_jobs)
    @property
    def name(self): return "random_forest"
    @property
    def is_trained(self): return self._trained
    def fit(self, X, y):
        if self._model: self._model.fit(X, y); self._trained = True
    def predict(self, X):
        if not self._trained or not self._model: return []
        return [float(x) for x in self._model.predict(X)]
    def predict_proba(self, X):
        if not self._trained or not self._model: return []
        return self._model.predict_proba(X).tolist()
    def get_params(self):
        return {"model_type":"random_forest","n_estimators":self._config.n_estimators,
                "max_depth":self._config.max_depth,"random_seed":self._config.random_seed}
    def set_params(self, **kwargs):
        for k, v in kwargs.items():
            if hasattr(self._config, k): setattr(self._config, k, v)
        if self._model: self._model.set_params(**kwargs)
