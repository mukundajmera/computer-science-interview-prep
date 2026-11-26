class Solution {
    public int maxPoints(int[][] points) {
        if (points.length <= 2) {
            return points.length;
        }
        int best = 2;
        for (int i = 0; i < points.length; i++) {
            for (int j = i + 1; j < points.length; j++) {
                int count = 0;
                long x1 = points[i][0];
                long y1 = points[i][1];
                long x2 = points[j][0];
                long y2 = points[j][1];
                for (int[] point : points) {
                    long x3 = point[0];
                    long y3 = point[1];
                    if ((y2 - y1) * (x3 - x1) == (y3 - y1) * (x2 - x1)) {
                        count++;
                    }
                }
                best = Math.max(best, count);
            }
        }
        return best;
    }
}
