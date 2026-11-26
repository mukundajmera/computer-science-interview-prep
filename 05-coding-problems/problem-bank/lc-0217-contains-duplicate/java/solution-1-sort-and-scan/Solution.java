import java.util.Arrays;

class Solution {
    public boolean containsDuplicate(int[] nums) {
        int[] sorted = Arrays.copyOf(nums, nums.length);
        Arrays.sort(sorted);
        for (int index = 1; index < sorted.length; index++) {
            if (sorted[index] == sorted[index - 1]) {
                return true;
            }
        }
        return false;
    }
}
