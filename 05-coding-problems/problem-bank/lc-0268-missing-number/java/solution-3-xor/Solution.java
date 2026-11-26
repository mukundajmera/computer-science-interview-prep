class Solution {
    public int missingNumber(int[] nums) {
        int missing = nums.length;
        for (int index = 0; index < nums.length; index++) {
            missing ^= index;
            missing ^= nums[index];
        }
        return missing;
    }
}
