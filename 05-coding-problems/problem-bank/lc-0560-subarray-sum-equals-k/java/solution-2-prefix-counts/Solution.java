import java.util.HashMap;
import java.util.Map;

class Solution {
    public int subarraySum(int[] nums, int k) {
        Map<Integer, Integer> prefixCounts = new HashMap<>();
        prefixCounts.put(0, 1);
        int prefix = 0;
        int count = 0;
        for (int value : nums) {
            prefix += value;
            count += prefixCounts.getOrDefault(prefix - k, 0);
            prefixCounts.put(prefix, prefixCounts.getOrDefault(prefix, 0) + 1);
        }
        return count;
    }
}
