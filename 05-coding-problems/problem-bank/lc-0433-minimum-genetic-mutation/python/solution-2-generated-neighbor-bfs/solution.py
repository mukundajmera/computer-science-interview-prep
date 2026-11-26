from collections import deque
from typing import List


class Solution:
    def minMutation(self, startGene: str, endGene: str, bank: List[str]) -> int:
        available = set(bank)
        queue = deque([startGene])
        letters = 'ACGT'
        steps = 0
        while queue:
            for _ in range(len(queue)):
                gene = queue.popleft()
                if gene == endGene:
                    return steps
                chars = list(gene)
                for i, original in enumerate(chars):
                    for letter in letters:
                        if letter == original:
                            continue
                        chars[i] = letter
                        candidate = ''.join(chars)
                        if candidate in available:
                            available.remove(candidate)
                            queue.append(candidate)
                    chars[i] = original
            steps += 1
        return -1
