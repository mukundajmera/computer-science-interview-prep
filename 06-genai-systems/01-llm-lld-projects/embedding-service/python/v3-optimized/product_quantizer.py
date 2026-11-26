"""
Product Quantization simulator for embedding-service v3-optimized.

Compresses float32 vector embeddings into quantized sub-vector byte representations.
"""

from typing import List
import math
import random

class ProductQuantizer:
    """
    A simulator for Product Quantization (PQ).
    Splits an embedding vector into `num_subvectors` parts, and maps each
    sub-vector to the index of its nearest centroid in a codebook.
    """
    def __init__(self, dimensions: int, num_subvectors: int, codebook_size: int = 256):
        if dimensions % num_subvectors != 0:
            raise ValueError(f"dimensions ({dimensions}) must be divisible by num_subvectors ({num_subvectors})")
        if codebook_size <= 0 or codebook_size > 256:
            raise ValueError(f"codebook_size must be in (0, 256], got {codebook_size}")

        self.dimensions = dimensions
        self.num_subvectors = num_subvectors
        self.subvector_dim = dimensions // num_subvectors
        self.codebook_size = codebook_size

        # Simulate a codebook for each subvector position.
        # Shape: num_subvectors x codebook_size x subvector_dim
        # Using simple random centroids in range [-1.0, 1.0]
        # Seed it to be deterministic for tests
        rng = random.Random(42)

        self.codebooks: List[List[List[float]]] = []
        for _ in range(num_subvectors):
            subbook = []
            for _ in range(codebook_size):
                centroid = [rng.uniform(-1.0, 1.0) for _ in range(self.subvector_dim)]
                subbook.append(centroid)
            self.codebooks.append(subbook)

    def _euclidean_distance_sq(self, v1: List[float], v2: List[float]) -> float:
        return sum((x - y) ** 2 for x, y in zip(v1, v2))

    def encode(self, vector: List[float]) -> bytes:
        """
        Encodes a high-dimensional float vector into a compact byte representation.
        """
        if len(vector) != self.dimensions:
            raise ValueError(f"Expected vector of dimension {self.dimensions}, got {len(vector)}")

        codes = bytearray()
        for i in range(self.num_subvectors):
            start = i * self.subvector_dim
            end = start + self.subvector_dim
            subvec = vector[start:end]

            # Find closest centroid
            best_idx = 0
            best_dist = float('inf')

            for j, centroid in enumerate(self.codebooks[i]):
                dist = self._euclidean_distance_sq(subvec, centroid)
                if dist < best_dist:
                    best_dist = dist
                    best_idx = j

            codes.append(best_idx)

        return bytes(codes)

    def decode(self, codes: bytes) -> List[float]:
        """
        Decodes a byte representation back into an approximate float vector.
        """
        if len(codes) != self.num_subvectors:
            raise ValueError(f"Expected {self.num_subvectors} bytes, got {len(codes)}")

        vector = []
        for i, code in enumerate(codes):
            if code >= self.codebook_size:
                raise ValueError(f"Code {code} is out of bounds for codebook_size {self.codebook_size}")
            centroid = self.codebooks[i][code]
            vector.extend(centroid)

        return vector
