class Solution {
    public Node construct(int[][] grid) {
        int n = grid.length;
        int[][] prefix = new int[n + 1][n + 1];
        for (int row = 0; row < n; row++) {
            for (int col = 0; col < n; col++) {
                prefix[row + 1][col + 1] = grid[row][col]
                    + prefix[row][col + 1]
                    + prefix[row + 1][col]
                    - prefix[row][col];
            }
        }
        return build(prefix, 0, 0, n);
    }

    private Node build(int[][] prefix, int row, int col, int size) {
        int total = sum(prefix, row, col, size);
        if (total == 0 || total == size * size) {
            return new Node(total > 0, true);
        }
        int half = size / 2;
        return new Node(
            true,
            false,
            build(prefix, row, col, half),
            build(prefix, row, col + half, half),
            build(prefix, row + half, col, half),
            build(prefix, row + half, col + half, half)
        );
    }

    private int sum(int[][] prefix, int row, int col, int size) {
        return prefix[row + size][col + size]
            - prefix[row][col + size]
            - prefix[row + size][col]
            + prefix[row][col];
    }
}
