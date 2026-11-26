import java.util.Arrays;

class Solution {
    public int[][] kClosest(int[][] points, int k) {
        int[][] ordered = Arrays.copyOf(points, points.length);
        Arrays.sort(ordered, (a, b) -> Integer.compare(distance(a), distance(b)));
        return Arrays.copyOf(ordered, k);
    }

    private int distance(int[] point) {
        return point[0] * point[0] + point[1] * point[1];
    }
}
