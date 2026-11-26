class Solution {
    public int firstMissingPositive(int[] nums) {
        int index = 0;
        while (index < nums.length) {
            int value = nums[index];
            if (value >= 1 && value <= nums.length && nums[value - 1] != value) {
                int target = value - 1;
                int temp = nums[target];
                nums[target] = nums[index];
                nums[index] = temp;
            } else {
                index++;
            }
        }
        for (int i = 0; i < nums.length; i++) {
            if (nums[i] != i + 1) {
                return i + 1;
            }
        }
        return nums.length + 1;
    }
}
