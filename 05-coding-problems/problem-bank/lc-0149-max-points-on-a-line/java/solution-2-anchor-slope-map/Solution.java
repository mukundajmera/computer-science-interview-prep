import java.util.HashMap;
import java.util.Map;

class Solution {
    public int maxPoints(int[][] points) {
        if (points.length <= 2) {
            return points.length;
        }
        int best = 2;
        for (int i = 0; i < points.length; i++) {
            Map<String, Integer> slopes = new HashMap<>();
            for (int j = i + 1; j < points.length; j++) {
                int dx = points[j][0] - points[i][0];
                int dy = points[j][1] - points[i][1];
                String key;
                if (dx == 0) {
                    key = "0/1";
                } else if (dy == 0) {
                    key = "1/0";
                } else {
                    int factor = gcd(Math.abs(dx), Math.abs(dy));
                    dx /= factor;
                    dy /= factor;
                    if (dx < 0) {
                        dx = -dx;
                        dy = -dy;
                    }
                    key = dx + "/" + dy;
                }
                int count = slopes.getOrDefault(key, 1) + 1;
                slopes.put(key, count);
                best = Math.max(best, count);
            }
        }
        return best;
    }

    private int gcd(int a, int b) {
        while (b != 0) {
            int temp = a % b;
            a = b;
            b = temp;
        }
        return a;
    }
}
