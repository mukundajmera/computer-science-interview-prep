class Solution {
    public int findPeakElement(int[] nums) {
        for (int i = 0; i < nums.length; i++) {
            boolean leftOk = i == 0 || nums[i - 1] < nums[i];
            boolean rightOk = i == nums.length - 1 || nums[i] > nums[i + 1];
            if (leftOk && rightOk) {
                return i;
            }
        }
        return 0;
    }
}
