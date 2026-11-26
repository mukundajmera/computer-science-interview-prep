import java.util.ArrayList;
import java.util.Collections;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

class Solution {
    public int[] intersection(int[] nums1, int[] nums2) {
        Set<Integer> first = new HashSet<>();
        for (int value : nums1) {
            first.add(value);
        }

        Set<Integer> shared = new HashSet<>();
        for (int value : nums2) {
            if (first.contains(value)) {
                shared.add(value);
            }
        }

        List<Integer> sorted = new ArrayList<>(shared);
        Collections.sort(sorted);
        int[] result = new int[sorted.size()];
        for (int index = 0; index < sorted.size(); index++) {
            result[index] = sorted.get(index);
        }
        return result;
    }
}
