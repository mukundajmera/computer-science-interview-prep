import java.util.*;

public class Solutions {
    public int maximumSumSubarray(int[] nums, int k) {
        if (nums == null || nums.length < k || k == 0) return 0;
        int windowSum = 0;
        for (int i = 0; i < k; i++) {
            windowSum += nums[i];
        }
        int best = windowSum;
        for (int right = k; right < nums.length; right++) {
            windowSum += nums[right];
            windowSum -= nums[right - k];
            best = Math.max(best, windowSum);
        }
        return best;
    }

    public int minSubArrayLen(int target, int[] nums) {
        int left = 0;
        int windowSum = 0;
        int best = Integer.MAX_VALUE;
        for (int right = 0; right < nums.length; right++) {
            windowSum += nums[right];
            while (windowSum >= target) {
                best = Math.min(best, right - left + 1);
                windowSum -= nums[left];
                left++;
            }
        }
        return best == Integer.MAX_VALUE ? 0 : best;
    }

    public int lengthOfLongestSubstring(String s) {
        int left = 0;
        Map<Character, Integer> counts = new HashMap<>();
        int best = 0;
        for (int right = 0; right < s.length(); right++) {
            char ch = s.charAt(right);
            counts.put(ch, counts.getOrDefault(ch, 0) + 1);
            while (counts.get(ch) > 1) {
                char leftCh = s.charAt(left);
                counts.put(leftCh, counts.get(leftCh) - 1);
                left++;
            }
            best = Math.max(best, right - left + 1);
        }
        return best;
    }

    public int lengthOfLongestSubstringKDistinct(String s, int k) {
        if (k == 0 || s == null || s.length() == 0) return 0;
        int left = 0;
        Map<Character, Integer> freq = new HashMap<>();
        int best = 0;
        for (int right = 0; right < s.length(); right++) {
            char ch = s.charAt(right);
            freq.put(ch, freq.getOrDefault(ch, 0) + 1);
            while (freq.size() > k) {
                char leftCh = s.charAt(left);
                freq.put(leftCh, freq.get(leftCh) - 1);
                if (freq.get(leftCh) == 0) {
                    freq.remove(leftCh);
                }
                left++;
            }
            best = Math.max(best, right - left + 1);
        }
        return best;
    }

    public int subarraysWithKDistinct(int[] nums, int k) {
        return atMost(nums, k) - atMost(nums, k - 1);
    }
    
    private int atMost(int[] nums, int k) {
        if (k < 0) return 0;
        int left = 0;
        Map<Integer, Integer> freq = new HashMap<>();
        int count = 0;
        for (int right = 0; right < nums.length; right++) {
            freq.put(nums[right], freq.getOrDefault(nums[right], 0) + 1);
            while (freq.size() > k) {
                freq.put(nums[left], freq.get(nums[left]) - 1);
                if (freq.get(nums[left]) == 0) {
                    freq.remove(nums[left]);
                }
                left++;
            }
            count += right - left + 1;
        }
        return count;
    }

    public boolean checkInclusion(String s1, String s2) {
        if (s1.length() > s2.length()) return false;
        Map<Character, Integer> need = new HashMap<>();
        for (char c : s1.toCharArray()) {
            need.put(c, need.getOrDefault(c, 0) + 1);
        }
        Map<Character, Integer> window = new HashMap<>();
        int left = 0;
        for (int right = 0; right < s2.length(); right++) {
            char ch = s2.charAt(right);
            window.put(ch, window.getOrDefault(ch, 0) + 1);
            if (right - left + 1 > s1.length()) {
                char leftCh = s2.charAt(left);
                window.put(leftCh, window.get(leftCh) - 1);
                if (window.get(leftCh) == 0) {
                    window.remove(leftCh);
                }
                left++;
            }
            if (right - left + 1 == s1.length() && window.equals(need)) {
                return true;
            }
        }
        return false;
    }

    public int[] maxSlidingWindow(int[] nums, int k) {
        if (nums == null || k == 0) return new int[0];
        Deque<Integer> deque = new LinkedList<>();
        int[] res = new int[nums.length - k + 1];
        int resIdx = 0;
        for (int i = 0; i < nums.length; i++) {
            while (!deque.isEmpty() && deque.peekFirst() < i - k + 1) {
                deque.pollFirst();
            }
            while (!deque.isEmpty() && nums[deque.peekLast()] < nums[i]) {
                deque.pollLast();
            }
            deque.offerLast(i);
            if (i >= k - 1) {
                res[resIdx++] = nums[deque.peekFirst()];
            }
        }
        return res;
    }
}
