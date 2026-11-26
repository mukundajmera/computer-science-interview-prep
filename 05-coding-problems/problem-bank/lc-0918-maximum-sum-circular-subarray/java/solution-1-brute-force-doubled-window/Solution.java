class Solution {
    public int maxSubarraySumCircular(int[] nums) {
        int n = nums.length;
        int best = nums[0];
        for (int start = 0; start < n; start++) {
            int total = 0;
            for (int length = 0; length < n; length++) {
                total += nums[(start + length) % n];
                best = Math.max(best, total);
            }
        }
        return best;
    }
}
