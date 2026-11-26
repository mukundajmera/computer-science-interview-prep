class Solution {
    public int minSubArrayLen(int target, int[] nums) {
        int best = nums.length + 1;
        for (int start = 0; start < nums.length; start++) {
            int sum = 0;
            for (int end = start; end < nums.length; end++) {
                sum += nums[end];
                if (sum >= target) {
                    best = Math.min(best, end - start + 1);
                    break;
                }
            }
        }
        return best == nums.length + 1 ? 0 : best;
    }
}
