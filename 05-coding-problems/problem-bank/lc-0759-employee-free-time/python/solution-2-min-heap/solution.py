import heapq
from typing import List


class Solution:
    def employeeFreeTime(self, schedule: List[List[List[int]]]) -> List[List[int]]:
        heap = []
        for employee, intervals in enumerate(schedule):
            if intervals:
                heap.append((intervals[0][0], employee, 0))
        heapq.heapify(heap)
        _, employee, index = heapq.heappop(heap)
        end = schedule[employee][index][1]
        if index + 1 < len(schedule[employee]):
            nxt = schedule[employee][index + 1]
            heapq.heappush(heap, (nxt[0], employee, index + 1))
        free = []
        while heap:
            _, employee, index = heapq.heappop(heap)
            start, stop = schedule[employee][index]
            if start > end:
                free.append([end, start])
                end = stop
            else:
                end = max(end, stop)
            if index + 1 < len(schedule[employee]):
                nxt = schedule[employee][index + 1]
                heapq.heappush(heap, (nxt[0], employee, index + 1))
        return free
