class Solution {
    public int missingNumber(int[] nums) {
        int expected = nums.length * (nums.length + 1) / 2;
        int actual = 0;
        for (int value : nums) {
            actual += value;
        }
        return expected - actual;
    }
}
