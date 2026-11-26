from typing import List


class Solution:
    def largestNumber(self, nums: List[int]) -> str:
        values = [str(value) for value in nums]
        best = ""
        used = [False] * len(values)

        def permute(path: List[str]) -> None:
            nonlocal best
            if len(path) == len(values):
                candidate = "".join(path)
                if candidate > best:
                    best = candidate
                return
            for index, value in enumerate(values):
                if used[index]:
                    continue
                used[index] = True
                path.append(value)
                permute(path)
                path.pop()
                used[index] = False

        permute([])
        return "0" if best[0] == "0" else best
