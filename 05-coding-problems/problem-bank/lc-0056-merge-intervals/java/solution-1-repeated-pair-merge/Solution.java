import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;

class Solution {
    public int[][] merge(int[][] intervals) {
        List<int[]> work = new ArrayList<>();
        for (int[] interval : intervals) {
            work.add(new int[] {interval[0], interval[1]});
        }
        boolean changed = true;
        while (changed) {
            changed = false;
            outer:
            for (int i = 0; i < work.size(); i++) {
                for (int j = i + 1; j < work.size(); j++) {
                    int[] a = work.get(i);
                    int[] b = work.get(j);
                    if (a[0] <= b[1] && b[0] <= a[1]) {
                        work.set(i, new int[] {Math.min(a[0], b[0]), Math.max(a[1], b[1])});
                        work.remove(j);
                        changed = true;
                        break outer;
                    }
                }
            }
        }
        work.sort(Comparator.comparingInt(interval -> interval[0]));
        return work.toArray(new int[work.size()][]);
    }
}
