class Solution {
    public int maxProduct(int[] nums) {
        int best = nums[0];
        for (int left = 0; left < nums.length; left++) {
            int product = 1;
            for (int right = left; right < nums.length; right++) {
                product *= nums[right];
                best = Math.max(best, product);
            }
        }
        return best;
    }
}
