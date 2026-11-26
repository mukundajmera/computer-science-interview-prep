class Solution {
    public int maxProduct(int[] nums) {
        int currentMax = nums[0];
        int currentMin = nums[0];
        int best = nums[0];
        for (int i = 1; i < nums.length; i++) {
            int value = nums[i];
            if (value < 0) {
                int temp = currentMax;
                currentMax = currentMin;
                currentMin = temp;
            }
            currentMax = Math.max(value, currentMax * value);
            currentMin = Math.min(value, currentMin * value);
            best = Math.max(best, currentMax);
        }
        return best;
    }
}
