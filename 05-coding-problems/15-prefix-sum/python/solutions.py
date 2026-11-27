from __future__ import annotations

class NumArray:
    def __init__(self, nums: list[int]):
        self.prefix = [0] * (len(nums) + 1)
        for i in range(len(nums)):
            self.prefix[i + 1] = self.prefix[i] + nums[i]

    def sumRange(self, left: int, right: int) -> int:
        return self.prefix[right + 1] - self.prefix[left]


def subarraySum(nums: list[int], k: int) -> int:
    count = 0
    curr_sum = 0
    prefix_sums = {0: 1}
    for num in nums:
        curr_sum += num
        if curr_sum - k in prefix_sums:
            count += prefix_sums[curr_sum - k]
        prefix_sums[curr_sum] = prefix_sums.get(curr_sum, 0) + 1
    return count


def checkSubarraySum(nums: list[int], k: int) -> bool:
    remainder_map = {0: -1}
    curr_sum = 0
    for i, num in enumerate(nums):
        curr_sum += num
        remainder = curr_sum % k
        if remainder in remainder_map:
            if i - remainder_map[remainder] > 1:
                return True
        else:
            remainder_map[remainder] = i
    return False


class NumMatrix:
    def __init__(self, matrix: list[list[int]]):
        if not matrix or not matrix[0]:
            self.prefix = []
            return
        m, n = len(matrix), len(matrix[0])
        self.prefix = [[0] * (n + 1) for _ in range(m + 1)]
        for r in range(m):
            for c in range(n):
                self.prefix[r + 1][c + 1] = (
                    matrix[r][c]
                    + self.prefix[r][c + 1]
                    + self.prefix[r + 1][c]
                    - self.prefix[r][c]
                )

    def sumRegion(self, row1: int, col1: int, row2: int, col2: int) -> int:
        if not self.prefix:
            return 0
        return (
            self.prefix[row2 + 1][col2 + 1]
            - self.prefix[row1][col2 + 1]
            - self.prefix[row2 + 1][col1]
            + self.prefix[row1][col1]
        )


def pivotIndex(nums: list[int]) -> int:
    total_sum = sum(nums)
    left_sum = 0
    for i, num in enumerate(nums):
        if left_sum == total_sum - left_sum - num:
            return i
        left_sum += num
    return -1


def corpFlightBookings(bookings: list[list[int]], n: int) -> list[int]:
    diff = [0] * n
    for first, last, seats in bookings:
        diff[first - 1] += seats
        if last < n:
            diff[last] -= seats
            
    for i in range(1, n):
        diff[i] += diff[i - 1]
    return diff
