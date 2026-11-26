import java.util.ArrayDeque;
import java.util.Deque;

class Solution {
    public int[][] floodFill(int[][] image, int sr, int sc, int color) {
        int original = image[sr][sc];
        if (original == color) {
            return image;
        }
        int[][] directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        Deque<int[]> stack = new ArrayDeque<>();
        stack.push(new int[] {sr, sc});
        image[sr][sc] = color;
        while (!stack.isEmpty()) {
            int[] current = stack.pop();
            for (int[] direction : directions) {
                int nextRow = current[0] + direction[0];
                int nextCol = current[1] + direction[1];
                if (nextRow < 0 || nextRow >= image.length || nextCol < 0 || nextCol >= image[0].length) {
                    continue;
                }
                if (image[nextRow][nextCol] == original) {
                    image[nextRow][nextCol] = color;
                    stack.push(new int[] {nextRow, nextCol});
                }
            }
        }
        return image;
    }
}
