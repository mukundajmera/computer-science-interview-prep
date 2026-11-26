import random
from typing import List


class Solution:
    def __init__(self, w: List[int]):
        self.random = random.Random(0)
        self.bag = [index for index, weight in enumerate(w) for _ in range(weight)]

    def pickIndex(self) -> int:
        return self.random.choice(self.bag)
