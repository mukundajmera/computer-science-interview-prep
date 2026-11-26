import java.util.HashSet;
import java.util.Set;

class Solution {
    public int longestConsecutive(int[] nums) {
        Set<Integer> values = new HashSet<>();
        for (int num : nums) {
            values.add(num);
        }
        int best = 0;
        for (int num : values) {
            if (values.contains(num - 1)) {
                continue;
            }
            int length = 1;
            int next = num + 1;
            while (values.contains(next)) {
                length++;
                next++;
            }
            best = Math.max(best, length);
        }
        return best;
    }
}
