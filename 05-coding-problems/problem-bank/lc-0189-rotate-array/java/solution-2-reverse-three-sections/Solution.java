class Solution {
    public void rotate(int[] nums, int k) {
        if (nums.length == 0) {
            return;
        }

        int shift = k % nums.length;
        if (shift == 0) {
            return;
        }

        reverse(nums, 0, nums.length - 1);
        reverse(nums, 0, shift - 1);
        reverse(nums, shift, nums.length - 1);
    }

    private void reverse(int[] nums, int left, int right) {
        while (left < right) {
            int temp = nums[left];
            nums[left] = nums[right];
            nums[right] = temp;
            left++;
            right--;
        }
    }
}
