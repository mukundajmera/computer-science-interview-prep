class Solution {
    public void solve(char[][] board) {
        int rows = board.length;
        int cols = board[0].length;
        boolean[][] safe = new boolean[rows][cols];
        for (int row = 0; row < rows; row++) {
            mark(board, safe, row, 0);
            mark(board, safe, row, cols - 1);
        }
        for (int col = 0; col < cols; col++) {
            mark(board, safe, 0, col);
            mark(board, safe, rows - 1, col);
        }
        for (int row = 0; row < rows; row++) {
            for (int col = 0; col < cols; col++) {
                if (board[row][col] == 'O' && !safe[row][col]) {
                    board[row][col] = 'X';
                }
            }
        }
    }

    private void mark(char[][] board, boolean[][] safe, int row, int col) {
        if (row < 0 || row == board.length || col < 0 || col == board[0].length) {
            return;
        }
        if (safe[row][col] || board[row][col] != 'O') {
            return;
        }
        safe[row][col] = true;
        mark(board, safe, row + 1, col);
        mark(board, safe, row - 1, col);
        mark(board, safe, row, col + 1);
        mark(board, safe, row, col - 1);
    }
}
