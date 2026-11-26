import java.util.HashMap;
import java.util.Map;

class Solution {
    public int majorityElement(int[] nums) {
        Map<Integer, Integer> counts = new HashMap<>();
        int threshold = nums.length / 2;
        for (int value : nums) {
            int count = counts.getOrDefault(value, 0) + 1;
            if (count > threshold) {
                return value;
            }
            counts.put(value, count);
        }
        return nums[0];
    }
}
