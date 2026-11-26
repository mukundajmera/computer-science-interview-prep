import java.util.ArrayDeque;
import java.util.Queue;

class Solution {
    public int[][] updateMatrix(int[][] mat) {
        int rows = mat.length;
        int cols = mat[0].length;
        int[][] answer = new int[rows][cols];
        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                answer[row][col] = nearestZero(mat, row, col);
            }
        }
        return answer;
    }

    private int nearestZero(int[][] mat, int startRow, int startCol) {
        if (mat[startRow][startCol] == 0) {
            return 0;
        }
        int rows = mat.length;
        int cols = mat[0].length;
        boolean[][] seen = new boolean[rows][cols];
        Queue<int[]> queue = new ArrayDeque<>();
        queue.add(new int[] {startRow, startCol, 0});
        seen[startRow][startCol] = true;
        int[][] directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (!queue.isEmpty()) {
            int[] current = queue.remove();
            for (int[] direction : directions) {
                int nextRow = current[0] + direction[0];
                int nextCol = current[1] + direction[1];
                if (nextRow < 0 || nextRow >= rows || nextCol < 0 || nextCol >= cols || seen[nextRow][nextCol]) {
                    continue;
                }
                if (mat[nextRow][nextCol] == 0) {
                    return current[2] + 1;
                }
                seen[nextRow][nextCol] = true;
                queue.add(new int[] {nextRow, nextCol, current[2] + 1});
            }
        }
        return 0;
    }
}
