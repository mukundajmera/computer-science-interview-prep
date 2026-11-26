class Solution {
    private static final int[][] DIRECTIONS = {
        {-1, -1}, {-1, 0}, {-1, 1},
        {0, -1},           {0, 1},
        {1, -1},  {1, 0},  {1, 1}
    };

    public void gameOfLife(int[][] board) {
        int[][] snapshot = new int[board.length][board[0].length];
        for (int row = 0; row < board.length; row++) {
            for (int col = 0; col < board[row].length; col++) {
                snapshot[row][col] = board[row][col];
            }
        }
        for (int row = 0; row < board.length; row++) {
            for (int col = 0; col < board[row].length; col++) {
                int live = liveNeighbors(snapshot, row, col);
                if (snapshot[row][col] == 1) {
                    board[row][col] = (live == 2 || live == 3) ? 1 : 0;
                } else {
                    board[row][col] = live == 3 ? 1 : 0;
                }
            }
        }
    }

    private int liveNeighbors(int[][] board, int row, int col) {
        int count = 0;
        for (int[] direction : DIRECTIONS) {
            int nextRow = row + direction[0];
            int nextCol = col + direction[1];
            if (nextRow >= 0 && nextRow < board.length && nextCol >= 0 && nextCol < board[0].length) {
                count += board[nextRow][nextCol];
            }
        }
        return count;
    }
}
