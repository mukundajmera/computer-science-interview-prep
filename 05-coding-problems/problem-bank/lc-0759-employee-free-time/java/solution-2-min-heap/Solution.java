import java.util.ArrayList;
import java.util.List;
import java.util.PriorityQueue;

class Solution {
    public int[][] employeeFreeTime(int[][][] schedule) {
        PriorityQueue<int[]> heap = new PriorityQueue<>((a, b) -> Integer.compare(schedule[a[0]][a[1]][0], schedule[b[0]][b[1]][0]));
        for (int employee = 0; employee < schedule.length; employee++) {
            if (schedule[employee].length > 0) {
                heap.add(new int[] {employee, 0});
            }
        }
        int[] first = heap.remove();
        int end = schedule[first[0]][first[1]][1];
        if (first[1] + 1 < schedule[first[0]].length) {
            heap.add(new int[] {first[0], first[1] + 1});
        }
        List<int[]> free = new ArrayList<>();
        while (!heap.isEmpty()) {
            int[] item = heap.remove();
            int[] interval = schedule[item[0]][item[1]];
            if (interval[0] > end) {
                free.add(new int[] {end, interval[0]});
                end = interval[1];
            } else {
                end = Math.max(end, interval[1]);
            }
            if (item[1] + 1 < schedule[item[0]].length) {
                heap.add(new int[] {item[0], item[1] + 1});
            }
        }
        return free.toArray(new int[free.size()][]);
    }
}
