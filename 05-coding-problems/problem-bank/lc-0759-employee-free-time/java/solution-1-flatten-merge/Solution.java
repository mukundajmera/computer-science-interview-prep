import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;

class Solution {
    public int[][] employeeFreeTime(int[][][] schedule) {
        List<int[]> intervals = new ArrayList<>();
        for (int[][] employee : schedule) {
            intervals.addAll(Arrays.asList(employee));
        }
        intervals.sort(Comparator.comparingInt(a -> a[0]));
        List<int[]> free = new ArrayList<>();
        int end = intervals.get(0)[1];
        for (int i = 1; i < intervals.size(); i++) {
            int[] interval = intervals.get(i);
            if (interval[0] > end) {
                free.add(new int[] {end, interval[0]});
                end = interval[1];
            } else {
                end = Math.max(end, interval[1]);
            }
        }
        return free.toArray(new int[free.size()][]);
    }
}
