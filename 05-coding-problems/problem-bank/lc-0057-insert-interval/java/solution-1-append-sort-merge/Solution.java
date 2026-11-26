import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

class Solution {
    public int[][] insert(int[][] intervals, int[] newInterval) {
        List<int[]> combined = new ArrayList<>();
        for (int[] interval : intervals) {
            combined.add(new int[] {interval[0], interval[1]});
        }
        combined.add(new int[] {newInterval[0], newInterval[1]});
        combined.sort(Comparator.comparingInt(interval -> interval[0]));
        List<int[]> merged = new ArrayList<>();
        for (int[] interval : combined) {
            if (merged.isEmpty() || merged.get(merged.size() - 1)[1] < interval[0]) {
                merged.add(new int[] {interval[0], interval[1]});
            } else {
                int[] last = merged.get(merged.size() - 1);
                last[1] = Math.max(last[1], interval[1]);
            }
        }
        return merged.toArray(new int[merged.size()][]);
    }
}
