from collections import deque
from typing import List


class Solution:
    def minMutation(self, startGene: str, endGene: str, bank: List[str]) -> int:
        unused = set(bank)
        queue = deque([startGene])
        steps = 0
        while queue:
            for _ in range(len(queue)):
                gene = queue.popleft()
                if gene == endGene:
                    return steps
                next_layer = {candidate for candidate in unused if self._differs_by_one(gene, candidate)}
                queue.extend(next_layer)
                unused -= next_layer
            steps += 1
        return -1

    def _differs_by_one(self, a: str, b: str) -> bool:
        return sum(left != right for left, right in zip(a, b)) == 1
