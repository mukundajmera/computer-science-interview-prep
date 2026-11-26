import java.util.Arrays;

class Solution {
    public int jobScheduling(int[] startTime, int[] endTime, int[] profit) {
        int n = startTime.length;
        int[][] jobs = new int[n][3];
        for (int i = 0; i < n; i++) {
            jobs[i] = new int[] {startTime[i], endTime[i], profit[i]};
        }
        Arrays.sort(jobs, (a, b) -> Integer.compare(a[1], b[1]));
        int[] ends = new int[n];
        for (int i = 0; i < n; i++) {
            ends[i] = jobs[i][1];
        }
        int[] dp = new int[n + 1];
        for (int i = 1; i <= n; i++) {
            int[] job = jobs[i - 1];
            int previousCount = upperBound(ends, job[0], i - 1);
            dp[i] = Math.max(dp[i - 1], dp[previousCount] + job[2]);
        }
        return dp[n];
    }

    private int upperBound(int[] values, int target, int hi) {
        int lo = 0;
        while (lo < hi) {
            int mid = lo + (hi - lo) / 2;
            if (values[mid] <= target) {
                lo = mid + 1;
            } else {
                hi = mid;
            }
        }
        return lo;
    }
}
