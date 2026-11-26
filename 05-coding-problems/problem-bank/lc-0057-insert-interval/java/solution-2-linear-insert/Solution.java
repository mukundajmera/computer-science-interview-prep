import java.util.ArrayList;
import java.util.List;

class Solution {
    public int[][] insert(int[][] intervals, int[] newInterval) {
        List<int[]> result = new ArrayList<>();
        int index = 0;
        while (index < intervals.length && intervals[index][1] < newInterval[0]) {
            result.add(new int[] {intervals[index][0], intervals[index][1]});
            index++;
        }
        int start = newInterval[0];
        int end = newInterval[1];
        while (index < intervals.length && intervals[index][0] <= end) {
            start = Math.min(start, intervals[index][0]);
            end = Math.max(end, intervals[index][1]);
            index++;
        }
        result.add(new int[] {start, end});
        while (index < intervals.length) {
            result.add(new int[] {intervals[index][0], intervals[index][1]});
            index++;
        }
        return result.toArray(new int[result.size()][]);
    }
}
