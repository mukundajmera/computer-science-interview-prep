import java.util.HashMap;
import java.util.Map;

class Solution {
    public boolean containsNearbyDuplicate(int[] nums, int k) {
        Map<Integer, Integer> lastSeen = new HashMap<>();
        for (int index = 0; index < nums.length; index++) {
            Integer previous = lastSeen.put(nums[index], index);
            if (previous != null && index - previous <= k) {
                return true;
            }
        }
        return false;
    }
}
