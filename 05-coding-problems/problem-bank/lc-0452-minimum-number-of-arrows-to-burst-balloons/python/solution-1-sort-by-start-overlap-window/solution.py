from typing import List


class Solution:
    def findMinArrowShots(self, points: List[List[int]]) -> int:
        if not points:
            return 0
        points.sort(key=lambda interval: interval[0])
        arrows = 1
        current_end = points[0][1]
        for start, end in points[1:]:
            if start <= current_end:
                current_end = min(current_end, end)
            else:
                arrows += 1
                current_end = end
        return arrows
