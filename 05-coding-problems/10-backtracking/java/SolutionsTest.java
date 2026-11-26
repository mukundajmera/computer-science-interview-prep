import java.util.*;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        
        // 1. Subsets
        List<List<Integer>> subsetsRes = sol.subsets(new int[]{1, 2, 3});
        assert subsetsRes.size() == 8 : "Subsets size must be 8";
        
        // 2. Combination Sum
        List<List<Integer>> combSumRes = sol.combinationSum(new int[]{2, 3, 6, 7}, 7);
        assert combSumRes.size() == 2 : "CombinationSum size must be 2";
        
        // 3. Combinations
        List<List<Integer>> combineRes = sol.combine(4, 2);
        assert combineRes.size() == 6 : "Combine size must be 6";
        
        // 4. Permutations
        List<List<Integer>> permuteRes = sol.permute(new int[]{1, 2, 3});
        assert permuteRes.size() == 6 : "Permutations size must be 6";
        
        // 5. Generate Parentheses
        List<String> parenRes = sol.generateParenthesis(3);
        assert parenRes.size() == 5 : "Generate Parenthesis size must be 5";
        
        // 6. Word Search
        char[][] board = {
            {'A','B','C','E'},
            {'S','F','C','S'},
            {'A','D','E','E'}
        };
        boolean exist = sol.exist(board, "ABCCED");
        assert exist : "Word must exist";
        boolean notExist = sol.exist(board, "ABCB");
        assert !notExist : "Word must not exist";
        
        // 7. N-Queens
        List<List<String>> nQueensRes = sol.solveNQueens(4);
        assert nQueensRes.size() == 2 : "N-Queens size must be 2";
        
        // 8. Letter Combinations
        List<String> letterRes = sol.letterCombinations("23");
        assert letterRes.size() == 9 : "Letter Combinations size must be 9";
        
        System.out.println("All Java tests passed!");
    }
}
