import heapq
from typing import List


class Solution:
    def smallestRange(self, nums: List[List[int]]) -> List[int]:
        heap = []
        current_max = -10**18
        for list_id, row in enumerate(nums):
            heap.append((row[0], list_id, 0))
            current_max = max(current_max, row[0])
        heapq.heapify(heap)
        best = [heap[0][0], current_max]
        while len(heap) == len(nums):
            current_min, list_id, index = heapq.heappop(heap)
            if current_max - current_min < best[1] - best[0] or (current_max - current_min == best[1] - best[0] and current_min < best[0]):
                best = [current_min, current_max]
            next_index = index + 1
            if next_index == len(nums[list_id]):
                break
            next_value = nums[list_id][next_index]
            current_max = max(current_max, next_value)
            heapq.heappush(heap, (next_value, list_id, next_index))
        return best
