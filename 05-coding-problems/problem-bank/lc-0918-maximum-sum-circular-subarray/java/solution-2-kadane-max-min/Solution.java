class Solution {
    public int maxSubarraySumCircular(int[] nums) {
        int total = 0;
        int maxEnding = nums[0];
        int minEnding = nums[0];
        int bestMax = nums[0];
        int bestMin = nums[0];
        for (int i = 0; i < nums.length; i++) {
            int value = nums[i];
            total += value;
            if (i == 0) {
                continue;
            }
            maxEnding = Math.max(value, maxEnding + value);
            bestMax = Math.max(bestMax, maxEnding);
            minEnding = Math.min(value, minEnding + value);
            bestMin = Math.min(bestMin, minEnding);
        }
        if (bestMax < 0) {
            return bestMax;
        }
        return Math.max(bestMax, total - bestMin);
    }
}
