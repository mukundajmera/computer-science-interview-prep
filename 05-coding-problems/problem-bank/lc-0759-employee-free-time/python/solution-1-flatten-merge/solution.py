from typing import List


class Solution:
    def employeeFreeTime(self, schedule: List[List[List[int]]]) -> List[List[int]]:
        intervals = sorted(interval for employee in schedule for interval in employee)
        free = []
        end = intervals[0][1]
        for start, stop in intervals[1:]:
            if start > end:
                free.append([end, start])
                end = stop
            else:
                end = max(end, stop)
        return free
