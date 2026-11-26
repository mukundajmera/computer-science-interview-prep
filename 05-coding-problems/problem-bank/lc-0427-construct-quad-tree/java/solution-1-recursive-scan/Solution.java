class Solution {
    public Node construct(int[][] grid) {
        return build(grid, 0, 0, grid.length);
    }

    private Node build(int[][] grid, int row, int col, int size) {
        int first = grid[row][col];
        boolean uniform = true;
        for (int r = row; r < row + size && uniform; r++) {
            for (int c = col; c < col + size; c++) {
                if (grid[r][c] != first) {
                    uniform = false;
                    break;
                }
            }
        }
        if (uniform) {
            return new Node(first == 1, true);
        }
        int half = size / 2;
        return new Node(
            true,
            false,
            build(grid, row, col, half),
            build(grid, row, col + half, half),
            build(grid, row + half, col, half),
            build(grid, row + half, col + half, half)
        );
    }
}
