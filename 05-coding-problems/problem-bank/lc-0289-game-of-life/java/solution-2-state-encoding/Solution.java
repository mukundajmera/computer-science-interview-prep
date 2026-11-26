class Solution {
    private static final int[][] DIRECTIONS = {
        {-1, -1}, {-1, 0}, {-1, 1},
        {0, -1},           {0, 1},
        {1, -1},  {1, 0},  {1, 1}
    };

    public void gameOfLife(int[][] board) {
        for (int row = 0; row < board.length; row++) {
            for (int col = 0; col < board[row].length; col++) {
                int live = liveNeighbors(board, row, col);
                if (board[row][col] == 1 && (live < 2 || live > 3)) {
                    board[row][col] = -1;
                } else if (board[row][col] == 0 && live == 3) {
                    board[row][col] = 2;
                }
            }
        }
        for (int row = 0; row < board.length; row++) {
            for (int col = 0; col < board[row].length; col++) {
                board[row][col] = board[row][col] > 0 ? 1 : 0;
            }
        }
    }

    private int liveNeighbors(int[][] board, int row, int col) {
        int count = 0;
        for (int[] direction : DIRECTIONS) {
            int nextRow = row + direction[0];
            int nextCol = col + direction[1];
            if (nextRow >= 0 && nextRow < board.length && nextCol >= 0 && nextCol < board[0].length) {
                count += Math.abs(board[nextRow][nextCol]) == 1 ? 1 : 0;
            }
        }
        return count;
    }
}
