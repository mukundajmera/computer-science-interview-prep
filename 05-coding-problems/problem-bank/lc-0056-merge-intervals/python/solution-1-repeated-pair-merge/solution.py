from typing import List


class Solution:
    def merge(self, intervals: List[List[int]]) -> List[List[int]]:
        work = [interval[:] for interval in intervals]
        changed = True
        while changed:
            changed = False
            for i in range(len(work)):
                if changed:
                    break
                for j in range(i + 1, len(work)):
                    a = work[i]
                    b = work[j]
                    if a[0] <= b[1] and b[0] <= a[1]:
                        work[i] = [min(a[0], b[0]), max(a[1], b[1])]
                        work.pop(j)
                        changed = True
                        break
        return sorted(work, key=lambda interval: interval[0])
