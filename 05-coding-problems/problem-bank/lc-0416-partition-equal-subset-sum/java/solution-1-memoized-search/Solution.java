import java.util.HashSet;
import java.util.Set;

class Solution {
    public boolean canPartition(int[] nums) {
        int total = 0;
        for (int num : nums) {
            total += num;
        }
        if (total % 2 == 1) {
            return false;
        }
        return search(nums, 0, total / 2, new HashSet<>());
    }

    private boolean search(int[] nums, int index, int remaining, Set<String> memo) {
        if (remaining == 0) {
            return true;
        }
        if (remaining < 0 || index == nums.length) {
            return false;
        }
        String key = index + ":" + remaining;
        if (memo.contains(key)) {
            return false;
        }
        if (search(nums, index + 1, remaining - nums[index], memo) || search(nums, index + 1, remaining, memo)) {
            return true;
        }
        memo.add(key);
        return false;
    }
}
