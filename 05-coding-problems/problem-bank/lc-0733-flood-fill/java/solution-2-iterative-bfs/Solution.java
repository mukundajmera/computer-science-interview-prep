import java.util.ArrayDeque;
import java.util.Queue;

class Solution {
    public int[][] floodFill(int[][] image, int sr, int sc, int color) {
        int original = image[sr][sc];
        if (original == color) {
            return image;
        }
        int[][] directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        Queue<int[]> queue = new ArrayDeque<>();
        queue.add(new int[] {sr, sc});
        image[sr][sc] = color;
        while (!queue.isEmpty()) {
            int[] current = queue.remove();
            for (int[] direction : directions) {
                int nextRow = current[0] + direction[0];
                int nextCol = current[1] + direction[1];
                if (nextRow < 0 || nextRow >= image.length || nextCol < 0 || nextCol >= image[0].length) {
                    continue;
                }
                if (image[nextRow][nextCol] == original) {
                    image[nextRow][nextCol] = color;
                    queue.add(new int[] {nextRow, nextCol});
                }
            }
        }
        return image;
    }
}
