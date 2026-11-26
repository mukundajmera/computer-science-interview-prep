import java.util.ArrayList;
import java.util.List;

class Solution {
    public int orangesRotting(int[][] grid) {
        int rows = grid.length;
        int cols = grid[0].length;
        int fresh = countFresh(grid);
        int minutes = 0;
        int[][] directions = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
        while (fresh > 0) {
            List<int[]> next = new ArrayList<>();
            for (int row = 0; row < rows; row++) {
                for (int col = 0; col < cols; col++) {
                    if (grid[row][col] != 1) {
                        continue;
                    }
                    for (int[] direction : directions) {
                        int nr = row + direction[0];
                        int nc = col + direction[1];
                        if (nr >= 0 && nr < rows && nc >= 0 && nc < cols && grid[nr][nc] == 2) {
                            next.add(new int[] {row, col});
                            break;
                        }
                    }
                }
            }
            if (next.isEmpty()) {
                return -1;
            }
            for (int[] cell : next) {
                if (grid[cell[0]][cell[1]] == 1) {
                    grid[cell[0]][cell[1]] = 2;
                    fresh--;
                }
            }
            minutes++;
        }
        return minutes;
    }

    private int countFresh(int[][] grid) {
        int fresh = 0;
        for (int[] row : grid) {
            for (int value : row) {
                if (value == 1) {
                    fresh++;
                }
            }
        }
        return fresh;
    }
}
