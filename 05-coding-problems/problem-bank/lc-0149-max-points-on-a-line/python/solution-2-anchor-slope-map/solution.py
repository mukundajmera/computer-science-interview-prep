from math import gcd
from typing import Dict, List, Tuple


class Solution:
    def maxPoints(self, points: List[List[int]]) -> int:
        if len(points) <= 2:
            return len(points)
        best = 2
        for i, (x1, y1) in enumerate(points):
            slopes: Dict[Tuple[int, int], int] = {}
            for x2, y2 in points[i + 1:]:
                dx = x2 - x1
                dy = y2 - y1
                if dx == 0:
                    key = (0, 1)
                elif dy == 0:
                    key = (1, 0)
                else:
                    factor = gcd(abs(dx), abs(dy))
                    dx //= factor
                    dy //= factor
                    if dx < 0:
                        dx = -dx
                        dy = -dy
                    key = (dx, dy)
                slopes[key] = slopes.get(key, 1) + 1
                best = max(best, slopes[key])
        return best
