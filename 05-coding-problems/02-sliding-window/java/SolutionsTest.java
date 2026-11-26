import java.util.Arrays;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        
        // maximumSumSubarray
        assert sol.maximumSumSubarray(new int[]{2, 1, 5, 1, 3, 2}, 3) == 9;
        assert sol.maximumSumSubarray(new int[]{-1, -2, -3, -4}, 2) == -3;
        assert sol.maximumSumSubarray(new int[]{1, 2}, 2) == 3;
        assert sol.maximumSumSubarray(new int[]{1}, 1) == 1;
        assert sol.maximumSumSubarray(new int[]{1, 2, 3}, 1) == 3;
        assert sol.maximumSumSubarray(new int[]{4, 2, 1, 7, 8, 1, 2, 8, 1, 0}, 3) == 16;
        
        // minSubArrayLen
        assert sol.minSubArrayLen(7, new int[]{2,3,1,2,4,3}) == 2;
        assert sol.minSubArrayLen(4, new int[]{1,4,4}) == 1;
        assert sol.minSubArrayLen(11, new int[]{1,1,1,1,1,1,1,1}) == 0;
        assert sol.minSubArrayLen(100, new int[]{}) == 0;
        assert sol.minSubArrayLen(3, new int[]{1,1}) == 0;
        assert sol.minSubArrayLen(7, new int[]{2,3,1,2,4,3,7}) == 1;
        
        // lengthOfLongestSubstring
        assert sol.lengthOfLongestSubstring("abcabcbb") == 3;
        assert sol.lengthOfLongestSubstring("bbbbb") == 1;
        assert sol.lengthOfLongestSubstring("pwwkew") == 3;
        assert sol.lengthOfLongestSubstring("") == 0;
        assert sol.lengthOfLongestSubstring("a") == 1;
        assert sol.lengthOfLongestSubstring("au") == 2;
        
        // lengthOfLongestSubstringKDistinct
        assert sol.lengthOfLongestSubstringKDistinct("eceba", 2) == 3;
        assert sol.lengthOfLongestSubstringKDistinct("aa", 1) == 2;
        assert sol.lengthOfLongestSubstringKDistinct("abaccc", 2) == 4;
        assert sol.lengthOfLongestSubstringKDistinct("", 2) == 0;
        assert sol.lengthOfLongestSubstringKDistinct("a", 0) == 0;
        assert sol.lengthOfLongestSubstringKDistinct("abc", 3) == 3;
        
        // subarraysWithKDistinct
        assert sol.subarraysWithKDistinct(new int[]{1,2,1,2,3}, 2) == 7;
        assert sol.subarraysWithKDistinct(new int[]{1,2,1,3,4}, 3) == 3;
        assert sol.subarraysWithKDistinct(new int[]{1,1,1}, 1) == 6;
        assert sol.subarraysWithKDistinct(new int[]{1,2,3}, 1) == 3;
        assert sol.subarraysWithKDistinct(new int[]{1,2}, 2) == 1;
        assert sol.subarraysWithKDistinct(new int[]{1}, 1) == 1;
        
        // checkInclusion
        assert sol.checkInclusion("ab", "eidbaooo") == true;
        assert sol.checkInclusion("ab", "eidboaoo") == false;
        assert sol.checkInclusion("a", "a") == true;
        assert sol.checkInclusion("abc", "ab") == false;
        assert sol.checkInclusion("abc", "bca") == true;
        assert sol.checkInclusion("hello", "ooolleoooleh") == false;
        
        // maxSlidingWindow
        assert Arrays.equals(sol.maxSlidingWindow(new int[]{1,3,-1,-3,5,3,6,7}, 3), new int[]{3,3,5,5,6,7});
        assert Arrays.equals(sol.maxSlidingWindow(new int[]{1}, 1), new int[]{1});
        assert Arrays.equals(sol.maxSlidingWindow(new int[]{1,-1}, 1), new int[]{1, -1});
        assert Arrays.equals(sol.maxSlidingWindow(new int[]{9,11}, 2), new int[]{11});
        assert Arrays.equals(sol.maxSlidingWindow(new int[]{4,-2}, 2), new int[]{4});
        assert Arrays.equals(sol.maxSlidingWindow(new int[]{}, 0), new int[]{});
        
        System.out.println("All Java tests passed!");
    }
}
