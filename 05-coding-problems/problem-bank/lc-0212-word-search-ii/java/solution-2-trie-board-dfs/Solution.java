import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    public List<String> findWords(char[][] board, String[] words) {
        TrieNode root = new TrieNode();
        for (String word : words) {
            TrieNode node = root;
            for (char ch : word.toCharArray()) {
                node = node.children.computeIfAbsent(ch, key -> new TrieNode());
            }
            node.word = word;
        }
        List<String> result = new ArrayList<>();
        for (int r = 0; r < board.length; r++) {
            for (int c = 0; c < board[0].length; c++) {
                dfs(board, r, c, root, result);
            }
        }
        return result;
    }

    private void dfs(char[][] board, int row, int col, TrieNode node, List<String> result) {
        if (row < 0 || row >= board.length || col < 0 || col >= board[0].length || board[row][col] == '#') {
            return;
        }
        char ch = board[row][col];
        TrieNode next = node.children.get(ch);
        if (next == null) {
            return;
        }
        if (next.word != null) {
            result.add(next.word);
            next.word = null;
        }
        board[row][col] = '#';
        dfs(board, row + 1, col, next, result);
        dfs(board, row - 1, col, next, result);
        dfs(board, row, col + 1, next, result);
        dfs(board, row, col - 1, next, result);
        board[row][col] = ch;
    }

    private static class TrieNode {
        Map<Character, TrieNode> children = new HashMap<>();
        String word;
    }
}
