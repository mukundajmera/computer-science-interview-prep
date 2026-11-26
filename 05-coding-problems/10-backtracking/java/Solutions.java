import java.util.*;

public class Solutions {
    public List<List<Integer>> subsets(int[] nums) {
        List<List<Integer>> res = new ArrayList<>();
        backtrackSubsets(0, nums, new ArrayList<>(), res);
        return res;
    }
    
    private void backtrackSubsets(int i, int[] nums, List<Integer> path, List<List<Integer>> res) {
        if (i == nums.length) {
            res.add(new ArrayList<>(path));
            return;
        }
        path.add(nums[i]);
        backtrackSubsets(i + 1, nums, path, res);
        path.remove(path.size() - 1);
        backtrackSubsets(i + 1, nums, path, res);
    }

    public List<List<Integer>> combinationSum(int[] candidates, int target) {
        List<List<Integer>> res = new ArrayList<>();
        Arrays.sort(candidates);
        backtrackCombSum(0, candidates, target, 0, new ArrayList<>(), res);
        return res;
    }
    
    private void backtrackCombSum(int i, int[] candidates, int target, int curSum, List<Integer> path, List<List<Integer>> res) {
        if (curSum == target) {
            res.add(new ArrayList<>(path));
            return;
        }
        if (curSum > target || i == candidates.length) {
            return;
        }
        path.add(candidates[i]);
        backtrackCombSum(i, candidates, target, curSum + candidates[i], path, res);
        path.remove(path.size() - 1);
        backtrackCombSum(i + 1, candidates, target, curSum, path, res);
    }

    public List<List<Integer>> combine(int n, int k) {
        List<List<Integer>> res = new ArrayList<>();
        backtrackCombine(1, n, k, new ArrayList<>(), res);
        return res;
    }
    
    private void backtrackCombine(int start, int n, int k, List<Integer> path, List<List<Integer>> res) {
        if (path.size() == k) {
            res.add(new ArrayList<>(path));
            return;
        }
        for (int i = start; i <= n; i++) {
            path.add(i);
            backtrackCombine(i + 1, n, k, path, res);
            path.remove(path.size() - 1);
        }
    }

    public List<List<Integer>> permute(int[] nums) {
        List<List<Integer>> res = new ArrayList<>();
        boolean[] used = new boolean[nums.length];
        backtrackPermute(nums, used, new ArrayList<>(), res);
        return res;
    }
    
    private void backtrackPermute(int[] nums, boolean[] used, List<Integer> path, List<List<Integer>> res) {
        if (path.size() == nums.length) {
            res.add(new ArrayList<>(path));
            return;
        }
        for (int i = 0; i < nums.length; i++) {
            if (!used[i]) {
                used[i] = true;
                path.add(nums[i]);
                backtrackPermute(nums, used, path, res);
                path.remove(path.size() - 1);
                used[i] = false;
            }
        }
    }

    public List<String> generateParenthesis(int n) {
        List<String> res = new ArrayList<>();
        backtrackParen(0, 0, n, new StringBuilder(), res);
        return res;
    }
    
    private void backtrackParen(int open, int close, int n, StringBuilder path, List<String> res) {
        if (open == n && close == n) {
            res.add(path.toString());
            return;
        }
        if (open < n) {
            path.append('(');
            backtrackParen(open + 1, close, n, path, res);
            path.deleteCharAt(path.length() - 1);
        }
        if (close < open) {
            path.append(')');
            backtrackParen(open, close + 1, n, path, res);
            path.deleteCharAt(path.length() - 1);
        }
    }

    public boolean exist(char[][] board, String word) {
        int m = board.length;
        int n = board[0].length;
        for (int i = 0; i < m; i++) {
            for (int j = 0; j < n; j++) {
                if (backtrackExist(board, word, i, j, 0)) {
                    return true;
                }
            }
        }
        return false;
    }
    
    private boolean backtrackExist(char[][] board, String word, int r, int c, int i) {
        if (i == word.length()) return true;
        if (r < 0 || c < 0 || r >= board.length || c >= board[0].length || board[r][c] != word.charAt(i)) {
            return false;
        }
        char temp = board[r][c];
        board[r][c] = '#';
        boolean found = backtrackExist(board, word, r + 1, c, i + 1) ||
                        backtrackExist(board, word, r - 1, c, i + 1) ||
                        backtrackExist(board, word, r, c + 1, i + 1) ||
                        backtrackExist(board, word, r, c - 1, i + 1);
        board[r][c] = temp;
        return found;
    }

    public List<List<String>> solveNQueens(int n) {
        List<List<String>> res = new ArrayList<>();
        char[][] board = new char[n][n];
        for (int i = 0; i < n; i++) Arrays.fill(board[i], '.');
        
        Set<Integer> cols = new HashSet<>();
        Set<Integer> posDiag = new HashSet<>();
        Set<Integer> negDiag = new HashSet<>();
        
        backtrackNQueens(0, n, board, cols, posDiag, negDiag, res);
        return res;
    }
    
    private void backtrackNQueens(int r, int n, char[][] board, Set<Integer> cols, Set<Integer> posDiag, Set<Integer> negDiag, List<List<String>> res) {
        if (r == n) {
            List<String> list = new ArrayList<>();
            for (int i = 0; i < n; i++) list.add(new String(board[i]));
            res.add(list);
            return;
        }
        for (int c = 0; c < n; c++) {
            if (cols.contains(c) || posDiag.contains(r + c) || negDiag.contains(r - c)) continue;
            
            cols.add(c);
            posDiag.add(r + c);
            negDiag.add(r - c);
            board[r][c] = 'Q';
            
            backtrackNQueens(r + 1, n, board, cols, posDiag, negDiag, res);
            
            cols.remove(c);
            posDiag.remove(r + c);
            negDiag.remove(r - c);
            board[r][c] = '.';
        }
    }

    public List<String> letterCombinations(String digits) {
        if (digits == null || digits.isEmpty()) return new ArrayList<>();
        
        Map<Character, String> map = Map.of(
            '2', "abc", '3', "def", '4', "ghi", '5', "jkl",
            '6', "mno", '7', "pqrs", '8', "tuv", '9', "wxyz"
        );
        List<String> res = new ArrayList<>();
        backtrackLetters(0, digits, map, new StringBuilder(), res);
        return res;
    }
    
    private void backtrackLetters(int i, String digits, Map<Character, String> map, StringBuilder path, List<String> res) {
        if (i == digits.length()) {
            res.add(path.toString());
            return;
        }
        String letters = map.get(digits.charAt(i));
        for (char c : letters.toCharArray()) {
            path.append(c);
            backtrackLetters(i + 1, digits, map, path, res);
            path.deleteCharAt(path.length() - 1);
        }
    }
}
