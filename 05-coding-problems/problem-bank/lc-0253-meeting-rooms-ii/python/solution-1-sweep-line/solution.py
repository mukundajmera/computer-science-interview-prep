from typing import List


class Solution:
    def minMeetingRooms(self, intervals: List[List[int]]) -> int:
        events = []
        for start, end in intervals:
            events.append((start, 1))
            events.append((end, -1))
        events.sort(key=lambda event: (event[0], event[1]))
        active = 0
        best = 0
        for _, delta in events:
            active += delta
            best = max(best, active)
        return best
