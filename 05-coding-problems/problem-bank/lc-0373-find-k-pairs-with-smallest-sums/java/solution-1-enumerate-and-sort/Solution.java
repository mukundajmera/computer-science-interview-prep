import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    public List<List<Integer>> kSmallestPairs(int[] nums1, int[] nums2, int k) {
        List<int[]> pairs = new ArrayList<>();
        for (int a : nums1) {
            for (int b : nums2) {
                pairs.add(new int[] {a, b});
            }
        }
        pairs.sort((x, y) -> {
            int sumCompare = Integer.compare(x[0] + x[1], y[0] + y[1]);
            if (sumCompare != 0) {
                return sumCompare;
            }
            int firstCompare = Integer.compare(x[0], y[0]);
            if (firstCompare != 0) {
                return firstCompare;
            }
            return Integer.compare(x[1], y[1]);
        });
        List<List<Integer>> result = new ArrayList<>();
        for (int i = 0; i < Math.min(k, pairs.size()); i++) {
            result.add(Arrays.asList(pairs.get(i)[0], pairs.get(i)[1]));
        }
        return result;
    }
}
