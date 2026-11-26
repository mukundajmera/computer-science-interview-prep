class Solution {
    public boolean containsNearbyDuplicate(int[] nums, int k) {
        for (int left = 0; left < nums.length; left++) {
            int rightLimit = Math.min(nums.length - 1, left + k);
            for (int right = left + 1; right <= rightLimit; right++) {
                if (nums[left] == nums[right]) {
                    return true;
                }
            }
        }
        return false;
    }
}
