import java.util.Arrays;
import java.util.PriorityQueue;

class Solution {
    public int minMeetingRooms(int[][] intervals) {
        if (intervals.length == 0) {
            return 0;
        }
        Arrays.sort(intervals, (left, right) -> Integer.compare(left[0], right[0]));
        PriorityQueue<Integer> ends = new PriorityQueue<>();
        for (int[] interval : intervals) {
            if (!ends.isEmpty() && ends.peek() <= interval[0]) {
                ends.poll();
            }
            ends.offer(interval[1]);
        }
        return ends.size();
    }
}
