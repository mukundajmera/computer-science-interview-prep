class Solution {
    public int numIslands(char[][] grid) {
        int islands = 0;
        boolean[][] visited = new boolean[grid.length][grid[0].length];
        for (int row = 0; row < grid.length; row++) {
            for (int col = 0; col < grid[row].length; col++) {
                if (grid[row][col] == '1' && !visited[row][col]) {
                    islands++;
                    visit(grid, visited, row, col);
                }
            }
        }
        return islands;
    }

    private void visit(char[][] grid, boolean[][] visited, int row, int col) {
        if (row < 0 || row == grid.length || col < 0 || col == grid[0].length) {
            return;
        }
        if (visited[row][col] || grid[row][col] != '1') {
            return;
        }
        visited[row][col] = true;
        visit(grid, visited, row + 1, col);
        visit(grid, visited, row - 1, col);
        visit(grid, visited, row, col + 1);
        visit(grid, visited, row, col - 1);
    }
}
