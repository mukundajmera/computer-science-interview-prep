from typing import List


class Solution:
    def searchMatrix(self, matrix: List[List[int]], target: int) -> bool:
        if not matrix or not matrix[0]:
            return False
        candidate = -1
        for row, values in enumerate(matrix):
            if values[0] <= target <= values[-1]:
                candidate = row
                break
        if candidate == -1:
            return False
        left = 0
        right = len(matrix[candidate]) - 1
        while left <= right:
            mid = (left + right) // 2
            value = matrix[candidate][mid]
            if value == target:
                return True
            if value < target:
                left = mid + 1
            else:
                right = mid - 1
        return False
