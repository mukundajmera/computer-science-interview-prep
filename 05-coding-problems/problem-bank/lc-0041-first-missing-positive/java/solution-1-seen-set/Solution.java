import java.util.HashSet;
import java.util.Set;

class Solution {
    public int firstMissingPositive(int[] nums) {
        Set<Integer> seen = new HashSet<>();
        for (int num : nums) {
            if (num > 0) {
                seen.add(num);
            }
        }
        int candidate = 1;
        while (seen.contains(candidate)) {
            candidate++;
        }
        return candidate;
    }
}
