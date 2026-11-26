import java.util.Arrays;

class Solution {
    public int eraseOverlapIntervals(int[][] intervals) {
        if (intervals.length == 0) {
            return 0;
        }
        Arrays.sort(intervals, (left, right) -> {
            if (left[0] != right[0]) {
                return Integer.compare(left[0], right[0]);
            }
            return Integer.compare(left[1], right[1]);
        });
        int[] dp = new int[intervals.length];
        int best = 1;
        Arrays.fill(dp, 1);
        for (int i = 0; i < intervals.length; i++) {
            for (int j = 0; j < i; j++) {
                if (intervals[j][1] <= intervals[i][0]) {
                    dp[i] = Math.max(dp[i], dp[j] + 1);
                }
            }
            best = Math.max(best, dp[i]);
        }
        return intervals.length - best;
    }
}
