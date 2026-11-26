from __future__ import annotations

from typing import List


class Solution:
    def calcEquation(
        self,
        equations: List[List[str]],
        values: List[float],
        queries: List[List[str]],
    ) -> List[float]:
        graph: dict[str, list[tuple[str, float]]] = {}
        for (left, right), ratio in zip(equations, values):
            graph.setdefault(left, []).append((right, ratio))
            graph.setdefault(right, []).append((left, 1.0 / ratio))

        def search(node: str, target: str, seen: set[str], product: float) -> float:
            if node == target:
                return product
            seen.add(node)
            for neighbor, ratio in graph.get(node, []):
                if neighbor in seen:
                    continue
                result = search(neighbor, target, seen, product * ratio)
                if result != -1.0:
                    return result
            return -1.0

        answers: list[float] = []
        for start, end in queries:
            if start not in graph or end not in graph:
                answers.append(-1.0)
            else:
                answers.append(search(start, end, set(), 1.0))
        return answers
