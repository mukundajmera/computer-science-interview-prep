import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    public int[] smallestRange(List<List<Integer>> nums) {
        List<int[]> values = new ArrayList<>();
        for (int list = 0; list < nums.size(); list++) {
            for (int value : nums.get(list)) {
                values.add(new int[] {value, list});
            }
        }
        Collections.sort(values, (a, b) -> Integer.compare(a[0], b[0]));
        Map<Integer, Integer> counts = new HashMap<>();
        int covered = 0;
        int left = 0;
        int[] best = {values.get(0)[0], values.get(values.size() - 1)[0]};
        for (int right = 0; right < values.size(); right++) {
            int list = values.get(right)[1];
            counts.put(list, counts.getOrDefault(list, 0) + 1);
            if (counts.get(list) == 1) {
                covered++;
            }
            while (covered == nums.size()) {
                int start = values.get(left)[0];
                int end = values.get(right)[0];
                if (end - start < best[1] - best[0] || (end - start == best[1] - best[0] && start < best[0])) {
                    best = new int[] {start, end};
                }
                int leftList = values.get(left)[1];
                counts.put(leftList, counts.get(leftList) - 1);
                if (counts.get(leftList) == 0) {
                    covered--;
                }
                left++;
            }
        }
        return best;
    }
}
