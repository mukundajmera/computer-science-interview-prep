from typing import List
from collections import deque, Counter

class Solutions:
    def maximumSumSubarray(self, nums: List[int], k: int) -> int:
        if not nums or k == 0 or len(nums) < k:
            return 0
        window_sum = sum(nums[:k])
        best = window_sum
        for right in range(k, len(nums)):
            window_sum += nums[right]
            window_sum -= nums[right - k]
            best = max(best, window_sum)
        return best

    def minSubArrayLen(self, target: int, nums: List[int]) -> int:
        left = 0
        window_sum = 0
        best = float('inf')
        for right in range(len(nums)):
            window_sum += nums[right]
            while window_sum >= target:
                best = min(best, right - left + 1)
                window_sum -= nums[left]
                left += 1
        return 0 if best == float('inf') else best

    def lengthOfLongestSubstring(self, s: str) -> int:
        left = 0
        counts = Counter()
        best = 0
        for right, ch in enumerate(s):
            counts[ch] += 1
            while counts[ch] > 1:
                counts[s[left]] -= 1
                left += 1
            best = max(best, right - left + 1)
        return best

    def lengthOfLongestSubstringKDistinct(self, s: str, k: int) -> int:
        if k == 0 or not s:
            return 0
        left = 0
        freq = Counter()
        best = 0
        for right, ch in enumerate(s):
            freq[ch] += 1
            while len(freq) > k:
                freq[s[left]] -= 1
                if freq[s[left]] == 0:
                    del freq[s[left]]
                left += 1
            best = max(best, right - left + 1)
        return best

    def subarraysWithKDistinct(self, A: List[int], K: int) -> int:
        def atMost(k: int) -> int:
            if k < 0: return 0
            left = 0
            freq = Counter()
            count = 0
            for right in range(len(A)):
                freq[A[right]] += 1
                while len(freq) > k:
                    freq[A[left]] -= 1
                    if freq[A[left]] == 0:
                        del freq[A[left]]
                    left += 1
                count += right - left + 1
            return count
        return atMost(K) - atMost(K - 1)

    def checkInclusion(self, s1: str, s2: str) -> bool:
        if len(s1) > len(s2):
            return False
        need = Counter(s1)
        window = Counter()
        left = 0
        for right, ch in enumerate(s2):
            window[ch] += 1
            if right - left + 1 > len(s1):
                window[s2[left]] -= 1
                if window[s2[left]] == 0:
                    del window[s2[left]]
                left += 1
            if right - left + 1 == len(s1) and window == need:
                return True
        return False

    def maxSlidingWindow(self, nums: List[int], k: int) -> List[int]:
        if not nums or k == 0:
            return []
        deque_idx = deque()
        res = []
        for i in range(len(nums)):
            while deque_idx and deque_idx[0] < i - k + 1:
                deque_idx.popleft()
            while deque_idx and nums[deque_idx[-1]] < nums[i]:
                deque_idx.pop()
            deque_idx.append(i)
            if i >= k - 1:
                res.append(nums[deque_idx[0]])
        return res
