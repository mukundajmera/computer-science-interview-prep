import java.util.Arrays;

class Solution {
    public int combinationSum4(int[] nums, int target) {
        int[] memo = new int[target + 1];
        Arrays.fill(memo, -1);
        memo[0] = 1;
        return count(target, nums, memo);
    }

    private int count(int remaining, int[] nums, int[] memo) {
        if (remaining < 0) {
            return 0;
        }
        if (memo[remaining] != -1) {
            return memo[remaining];
        }
        int total = 0;
        for (int value : nums) {
            total += count(remaining - value, nums, memo);
        }
        memo[remaining] = total;
        return total;
    }
}
