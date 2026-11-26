import java.util.ArrayList;
import java.util.List;

class Solution {
    public int minMeetingRooms(int[][] intervals) {
        List<int[]> events = new ArrayList<>();
        for (int[] interval : intervals) {
            events.add(new int[] {interval[0], 1});
            events.add(new int[] {interval[1], -1});
        }
        events.sort((left, right) -> left[0] == right[0] ? Integer.compare(left[1], right[1]) : Integer.compare(left[0], right[0]));
        int active = 0;
        int best = 0;
        for (int[] event : events) {
            active += event[1];
            best = Math.max(best, active);
        }
        return best;
    }
}
