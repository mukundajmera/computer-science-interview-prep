from typing import List


class Solution:
    def findMaximizedCapital(self, k: int, w: int, profits: List[int], capital: List[int]) -> int:
        used = [False] * len(profits)
        current = w
        for _ in range(k):
            best_index = -1
            best_profit = -1
            for index, profit in enumerate(profits):
                if not used[index] and capital[index] <= current and profit > best_profit:
                    best_profit = profit
                    best_index = index
            if best_index == -1:
                break
            used[best_index] = True
            current += profits[best_index]
        return current
