"""
Multi-Model Registry with dimensionality adapter.

Manages multiple embedding models and allows querying by name.
Supports dimensionality projection (e.g., Matryoshka embeddings) by truncating
the output to a desired lower dimensionality.
"""

from typing import Dict, List, Optional
import math


class EmbeddingModel:
    """Base model interface to allow typing in the registry."""
    @property
    def model_name(self) -> str:
        raise NotImplementedError

    @property
    def dimensions(self) -> int:
        raise NotImplementedError

    def embed(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]


class DimensionalityAdapter:
    """Adapts an embedding model to return truncated embeddings of lower dimensions."""
    def __init__(self, model: EmbeddingModel, target_dimensions: int):
        if target_dimensions <= 0 or target_dimensions > model.dimensions:
            raise ValueError(f"Target dimensions must be between 1 and {model.dimensions}")
        self._model = model
        self._target_dimensions = target_dimensions

    @property
    def model_name(self) -> str:
        return f"{self._model.model_name}-dim{self._target_dimensions}"

    @property
    def dimensions(self) -> int:
        return self._target_dimensions

    def _normalize(self, vector: List[float]) -> List[float]:
        magnitude = math.sqrt(sum(x * x for x in vector))
        if magnitude == 0:
            return vector
        return [x / magnitude for x in vector]

    def embed(self, text: str) -> List[float]:
        raw = self._model.embed(text)
        truncated = raw[:self._target_dimensions]
        return self._normalize(truncated)

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [self.embed(t) for t in texts]


class MultiModelRegistry:
    """Registry to manage multiple embedding models and handle routing."""
    def __init__(self):
        self._models: Dict[str, EmbeddingModel] = {}

    def register(self, model: EmbeddingModel) -> None:
        """Register a model by its name."""
        self._models[model.model_name] = model

    def get_model(self, model_name: str) -> Optional[EmbeddingModel]:
        """Retrieve a model by name."""
        return self._models.get(model_name)

    def route(self, text: str, model_name: str, target_dimensions: Optional[int] = None) -> List[float]:
        """Route request to the specified model, optionally truncating dimensions."""
        model = self.get_model(model_name)
        if not model:
            raise ValueError(f"Model '{model_name}' not found in registry.")

        if target_dimensions is not None:
            if target_dimensions < model.dimensions:
                adapter = DimensionalityAdapter(model, target_dimensions)
                return adapter.embed(text)
            elif target_dimensions > model.dimensions:
                raise ValueError(f"Target dimensions {target_dimensions} exceeds model dimensions {model.dimensions}.")

        return model.embed(text)
