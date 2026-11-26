from bisect import bisect_left
import random
from typing import List


class Solution:
    def __init__(self, w: List[int]):
        self.random = random.Random(0)
        self.prefix = []
        total = 0
        for weight in w:
            total += weight
            self.prefix.append(total)

    def pickIndex(self) -> int:
        target = self.random.randint(1, self.prefix[-1])
        return bisect_left(self.prefix, target)
