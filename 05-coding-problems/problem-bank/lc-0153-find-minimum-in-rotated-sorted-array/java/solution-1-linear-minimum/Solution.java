class Solution {
    public int findMin(int[] nums) {
        int best = nums[0];
        for (int value : nums) {
            best = Math.min(best, value);
        }
        return best;
    }
}
