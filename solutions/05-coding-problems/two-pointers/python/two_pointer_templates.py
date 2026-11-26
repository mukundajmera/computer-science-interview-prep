"""Minimal interview-grade two-pointer templates."""

from __future__ import annotations

from typing import List


def has_pair_sum_sorted(nums: List[int], target: int) -> bool:
    """Return True if a sorted array has any pair summing to target.

    Time: O(n)
    Space: O(1)
    """
    left, right = 0, len(nums) - 1
    while left < right:
        total = nums[left] + nums[right]
        if total == target:
            return True
        if total < target:
            left += 1
        else:
            right -= 1
    return False


def max_container_area(heights: List[int]) -> int:
    """Return the maximum container area.

    Time: O(n)
    Space: O(1)
    """
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        width = right - left
        best = max(best, width * min(heights[left], heights[right]))
        if heights[left] <= heights[right]:
            left += 1
        else:
            right -= 1
    return best


def three_sum(nums: List[int]) -> List[List[int]]:
    """Return unique triplets that sum to zero.

    Time: O(n^2) after sort
    Space: O(1) auxiliary (excluding output)
    """
    nums.sort()
    result: List[List[int]] = []

    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i - 1]:
            continue

        left, right = i + 1, len(nums) - 1
        while left < right:
            total = nums[i] + nums[left] + nums[right]
            if total == 0:
                result.append([nums[i], nums[left], nums[right]])
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
                while left < right and nums[right] == nums[right + 1]:
                    right -= 1
            elif total < 0:
                left += 1
            else:
                right -= 1

    return result


def count_valid_triangles(nums: List[int]) -> int:
    """Count index triplets that can form valid triangles.

    Time: O(n^2) after sort
    Space: O(1)
    """
    nums.sort()
    count = 0
    for i in range(len(nums) - 1, 1, -1):
        left, right = 0, i - 1
        while left < right:
            if nums[left] + nums[right] > nums[i]:
                count += right - left
                right -= 1
            else:
                left += 1
    return count


def move_zeroes(nums: List[int]) -> None:
    """Move zeros to the end in-place, preserving non-zero order.

    Time: O(n)
    Space: O(1)
    """
    write = 0
    for scan in range(len(nums)):
        if nums[scan] != 0:
            nums[write], nums[scan] = nums[scan], nums[write]
            write += 1


def sort_colors(nums: List[int]) -> None:
    """Sort values 0/1/2 in-place via Dutch National Flag partitioning.

    Time: O(n)
    Space: O(1)
    """
    left, scan, right = 0, 0, len(nums) - 1
    while scan <= right:
        if nums[scan] == 0:
            nums[left], nums[scan] = nums[scan], nums[left]
            left += 1
            scan += 1
        elif nums[scan] == 1:
            scan += 1
        else:
            nums[scan], nums[right] = nums[right], nums[scan]
            right -= 1


def trap_rain_water(heights: List[int]) -> int:
    """Return trapped rain water volume.

    Time: O(n)
    Space: O(1)
    """
    if not heights:
        return 0

    left, right = 0, len(heights) - 1
    left_max = 0
    right_max = 0
    trapped = 0

    while left <= right:
        if heights[left] <= heights[right]:
            left_max = max(left_max, heights[left])
            trapped += left_max - heights[left]
            left += 1
        else:
            right_max = max(right_max, heights[right])
            trapped += right_max - heights[right]
            right -= 1

    return trapped
