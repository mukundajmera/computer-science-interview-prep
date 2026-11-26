class Solution {
    public int climbStairs(int n) {
        if (n <= 2) {
            return n;
        }
        int twoBack = 1;
        int oneBack = 2;
        for (int step = 3; step <= n; step++) {
            int current = oneBack + twoBack;
            twoBack = oneBack;
            oneBack = current;
        }
        return oneBack;
    }
}
