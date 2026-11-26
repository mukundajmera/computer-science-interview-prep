class Solution {
    public void rotate(int[] nums, int k) {
        int n = nums.length;
        if (n == 0) {
            return;
        }

        int shift = k % n;
        int[] rotated = new int[n];
        for (int index = 0; index < n; index++) {
            rotated[(index + shift) % n] = nums[index];
        }
        for (int index = 0; index < n; index++) {
            nums[index] = rotated[index];
        }
    }
}
