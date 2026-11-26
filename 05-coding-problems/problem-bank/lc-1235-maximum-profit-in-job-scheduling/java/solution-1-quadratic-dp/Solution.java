import java.util.Arrays;

class Solution {
    public int jobScheduling(int[] startTime, int[] endTime, int[] profit) {
        int n = startTime.length;
        int[][] jobs = new int[n][3];
        for (int i = 0; i < n; i++) {
            jobs[i] = new int[] {startTime[i], endTime[i], profit[i]};
        }
        Arrays.sort(jobs, (a, b) -> Integer.compare(a[1], b[1]));
        int[] dp = new int[n];
        int best = 0;
        for (int i = 0; i < n; i++) {
            int take = jobs[i][2];
            for (int j = 0; j < i; j++) {
                if (jobs[j][1] <= jobs[i][0]) {
                    take = Math.max(take, dp[j] + jobs[i][2]);
                }
            }
            best = Math.max(best, take);
            dp[i] = best;
        }
        return best;
    }
}
