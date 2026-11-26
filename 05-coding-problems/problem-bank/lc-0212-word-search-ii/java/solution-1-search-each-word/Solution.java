import java.util.ArrayList;
import java.util.List;

class Solution {
    public List<String> findWords(char[][] board, String[] words) {
        List<String> result = new ArrayList<>();
        for (String word : words) {
            if (exists(board, word)) {
                result.add(word);
            }
        }
        return result;
    }

    private boolean exists(char[][] board, String word) {
        boolean[][] seen = new boolean[board.length][board[0].length];
        for (int r = 0; r < board.length; r++) {
            for (int c = 0; c < board[0].length; c++) {
                if (dfs(board, word, 0, r, c, seen)) {
                    return true;
                }
            }
        }
        return false;
    }

    private boolean dfs(char[][] board, String word, int index, int row, int col, boolean[][] seen) {
        if (index == word.length()) {
            return true;
        }
        if (row < 0 || row >= board.length || col < 0 || col >= board[0].length || seen[row][col] || board[row][col] != word.charAt(index)) {
            return false;
        }
        seen[row][col] = true;
        boolean found = dfs(board, word, index + 1, row + 1, col, seen)
            || dfs(board, word, index + 1, row - 1, col, seen)
            || dfs(board, word, index + 1, row, col + 1, seen)
            || dfs(board, word, index + 1, row, col - 1, seen);
        seen[row][col] = false;
        return found;
    }
}
