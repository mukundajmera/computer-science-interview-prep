from __future__ import annotations

from typing import List


class WeightedUnionFind:
    def __init__(self) -> None:
        self.parent: dict[str, str] = {}
        self.weight: dict[str, float] = {}

    def add(self, item: str) -> None:
        if item not in self.parent:
            self.parent[item] = item
            self.weight[item] = 1.0

    def find(self, item: str) -> tuple[str, float]:
        if self.parent[item] == item:
            return item, self.weight[item]
        root, ratio_to_root = self.find(self.parent[item])
        self.weight[item] *= ratio_to_root
        self.parent[item] = root
        return self.parent[item], self.weight[item]

    def union(self, numerator: str, denominator: str, ratio: float) -> None:
        self.add(numerator)
        self.add(denominator)
        numerator_root, numerator_weight = self.find(numerator)
        denominator_root, denominator_weight = self.find(denominator)
        if numerator_root == denominator_root:
            return
        self.parent[numerator_root] = denominator_root
        self.weight[numerator_root] = ratio * denominator_weight / numerator_weight

    def ratio(self, numerator: str, denominator: str) -> float:
        if numerator not in self.parent or denominator not in self.parent:
            return -1.0
        numerator_root, numerator_weight = self.find(numerator)
        denominator_root, denominator_weight = self.find(denominator)
        if numerator_root != denominator_root:
            return -1.0
        return numerator_weight / denominator_weight


class Solution:
    def calcEquation(
        self,
        equations: List[List[str]],
        values: List[float],
        queries: List[List[str]],
    ) -> List[float]:
        union_find = WeightedUnionFind()
        for (left, right), ratio in zip(equations, values):
            union_find.union(left, right, ratio)
        return [union_find.ratio(left, right) for left, right in queries]
