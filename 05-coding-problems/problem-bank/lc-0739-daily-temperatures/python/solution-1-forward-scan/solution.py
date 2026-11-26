from typing import List


class Solution:
    def dailyTemperatures(self, temperatures: List[int]) -> List[int]:
        answer = [0] * len(temperatures)
        for index, temperature in enumerate(temperatures):
            for later in range(index + 1, len(temperatures)):
                if temperatures[later] > temperature:
                    answer[index] = later - index
                    break
        return answer
