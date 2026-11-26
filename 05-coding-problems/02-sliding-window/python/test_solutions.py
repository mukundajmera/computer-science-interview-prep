import unittest
from solutions import Solutions

class TestSolutions(unittest.TestCase):
    def setUp(self):
        self.sol = Solutions()

    def test_maximumSumSubarray(self):
        self.assertEqual(self.sol.maximumSumSubarray([2, 1, 5, 1, 3, 2], 3), 9)
        self.assertEqual(self.sol.maximumSumSubarray([-1, -2, -3, -4], 2), -3)
        self.assertEqual(self.sol.maximumSumSubarray([1, 2], 2), 3)
        self.assertEqual(self.sol.maximumSumSubarray([1], 1), 1)
        self.assertEqual(self.sol.maximumSumSubarray([1, 2, 3], 1), 3)
        self.assertEqual(self.sol.maximumSumSubarray([4, 2, 1, 7, 8, 1, 2, 8, 1, 0], 3), 16)

    def test_minSubArrayLen(self):
        self.assertEqual(self.sol.minSubArrayLen(7, [2,3,1,2,4,3]), 2)
        self.assertEqual(self.sol.minSubArrayLen(4, [1,4,4]), 1)
        self.assertEqual(self.sol.minSubArrayLen(11, [1,1,1,1,1,1,1,1]), 0)
        self.assertEqual(self.sol.minSubArrayLen(100, []), 0)
        self.assertEqual(self.sol.minSubArrayLen(3, [1,1]), 0)
        self.assertEqual(self.sol.minSubArrayLen(7, [2,3,1,2,4,3,7]), 1)

    def test_lengthOfLongestSubstring(self):
        self.assertEqual(self.sol.lengthOfLongestSubstring("abcabcbb"), 3)
        self.assertEqual(self.sol.lengthOfLongestSubstring("bbbbb"), 1)
        self.assertEqual(self.sol.lengthOfLongestSubstring("pwwkew"), 3)
        self.assertEqual(self.sol.lengthOfLongestSubstring(""), 0)
        self.assertEqual(self.sol.lengthOfLongestSubstring("a"), 1)
        self.assertEqual(self.sol.lengthOfLongestSubstring("au"), 2)

    def test_lengthOfLongestSubstringKDistinct(self):
        self.assertEqual(self.sol.lengthOfLongestSubstringKDistinct("eceba", 2), 3)
        self.assertEqual(self.sol.lengthOfLongestSubstringKDistinct("aa", 1), 2)
        self.assertEqual(self.sol.lengthOfLongestSubstringKDistinct("abaccc", 2), 4)
        self.assertEqual(self.sol.lengthOfLongestSubstringKDistinct("", 2), 0)
        self.assertEqual(self.sol.lengthOfLongestSubstringKDistinct("a", 0), 0)
        self.assertEqual(self.sol.lengthOfLongestSubstringKDistinct("abc", 3), 3)

    def test_subarraysWithKDistinct(self):
        self.assertEqual(self.sol.subarraysWithKDistinct([1,2,1,2,3], 2), 7)
        self.assertEqual(self.sol.subarraysWithKDistinct([1,2,1,3,4], 3), 3)
        self.assertEqual(self.sol.subarraysWithKDistinct([1,1,1], 1), 6)
        self.assertEqual(self.sol.subarraysWithKDistinct([1,2,3], 1), 3)
        self.assertEqual(self.sol.subarraysWithKDistinct([1,2], 2), 1)
        self.assertEqual(self.sol.subarraysWithKDistinct([1], 1), 1)

    def test_checkInclusion(self):
        self.assertTrue(self.sol.checkInclusion("ab", "eidbaooo"))
        self.assertFalse(self.sol.checkInclusion("ab", "eidboaoo"))
        self.assertTrue(self.sol.checkInclusion("a", "a"))
        self.assertFalse(self.sol.checkInclusion("abc", "ab"))
        self.assertTrue(self.sol.checkInclusion("abc", "bca"))
        self.assertFalse(self.sol.checkInclusion("hello", "ooolleoooleh"))
        
    def test_maxSlidingWindow(self):
        self.assertEqual(self.sol.maxSlidingWindow([1,3,-1,-3,5,3,6,7], 3), [3,3,5,5,6,7])
        self.assertEqual(self.sol.maxSlidingWindow([1], 1), [1])
        self.assertEqual(self.sol.maxSlidingWindow([1,-1], 1), [1, -1])
        self.assertEqual(self.sol.maxSlidingWindow([9,11], 2), [11])
        self.assertEqual(self.sol.maxSlidingWindow([4,-2], 2), [4])
        self.assertEqual(self.sol.maxSlidingWindow([], 0), [])

if __name__ == '__main__':
    unittest.main()
