class Solution {
    public int maxSubArray(int[] nums) {
        int best = nums[0];
        for (int start = 0; start < nums.length; start++) {
            int sum = 0;
            for (int end = start; end < nums.length; end++) {
                sum += nums[end];
                best = Math.max(best, sum);
            }
        }
        return best;
    }
}
