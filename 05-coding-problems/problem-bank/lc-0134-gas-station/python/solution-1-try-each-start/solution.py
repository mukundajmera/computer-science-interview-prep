from typing import List


class Solution:
    def canCompleteCircuit(self, gas: List[int], cost: List[int]) -> int:
        n = len(gas)
        for start in range(n):
            tank = 0
            completed = True
            for step in range(n):
                index = (start + step) % n
                tank += gas[index] - cost[index]
                if tank < 0:
                    completed = False
                    break
            if completed:
                return start
        return -1
