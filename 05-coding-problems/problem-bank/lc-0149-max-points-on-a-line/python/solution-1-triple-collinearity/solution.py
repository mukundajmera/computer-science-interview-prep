from typing import List


class Solution:
    def maxPoints(self, points: List[List[int]]) -> int:
        if len(points) <= 2:
            return len(points)
        best = 2
        n = len(points)
        for i in range(n):
            for j in range(i + 1, n):
                count = 0
                x1, y1 = points[i]
                x2, y2 = points[j]
                for x3, y3 in points:
                    if (y2 - y1) * (x3 - x1) == (y3 - y1) * (x2 - x1):
                        count += 1
                best = max(best, count)
        return best
