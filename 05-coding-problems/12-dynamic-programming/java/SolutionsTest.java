import java.util.*;

public class SolutionsTest {
    public static void main(String[] args) {
        Solutions sol = new Solutions();
        
        // climbStairs
        assert sol.climbStairs(2) == 2;
        assert sol.climbStairs(3) == 3;
        assert sol.climbStairs(4) == 5;
        assert sol.climbStairs(1) == 1;
        assert sol.climbStairs(5) == 8;
        assert sol.climbStairs(10) == 89;
        
        // rob
        assert sol.rob(new int[]{1,2,3,1}) == 4;
        assert sol.rob(new int[]{2,7,9,3,1}) == 12;
        assert sol.rob(new int[]{0}) == 0;
        assert sol.rob(new int[]{2,1,1,2}) == 4;
        assert sol.rob(new int[]{10,0,0,10}) == 20;
        assert sol.rob(new int[]{5,1,1,5}) == 10;
        
        // wordBreak
        assert sol.wordBreak("leetcode", Arrays.asList("leet", "code")) == true;
        assert sol.wordBreak("applepenapple", Arrays.asList("apple", "pen")) == true;
        assert sol.wordBreak("catsandog", Arrays.asList("cats", "dog", "sand", "and", "cat")) == false;
        assert sol.wordBreak("a", Arrays.asList("a")) == true;
        assert sol.wordBreak("a", Arrays.asList("b")) == false;
        assert sol.wordBreak("aaaaaaa", Arrays.asList("aaaa", "aaa")) == true;
        
        // coinChange
        assert sol.coinChange(new int[]{1,2,5}, 11) == 3;
        assert sol.coinChange(new int[]{2}, 3) == -1;
        assert sol.coinChange(new int[]{1}, 0) == 0;
        assert sol.coinChange(new int[]{1}, 1) == 1;
        assert sol.coinChange(new int[]{1}, 2) == 2;
        assert sol.coinChange(new int[]{186,419,83,408}, 6249) == 20;
        
        // lengthOfLIS
        assert sol.lengthOfLIS(new int[]{10,9,2,5,3,7,101,18}) == 4;
        assert sol.lengthOfLIS(new int[]{0,1,0,3,2,3}) == 4;
        assert sol.lengthOfLIS(new int[]{7,7,7,7,7,7,7}) == 1;
        assert sol.lengthOfLIS(new int[]{1}) == 1;
        assert sol.lengthOfLIS(new int[]{1,2,3}) == 3;
        assert sol.lengthOfLIS(new int[]{3,2,1}) == 1;
        
        // minPathSum
        assert sol.minPathSum(new int[][]{{1,3,1},{1,5,1},{4,2,1}}) == 7;
        assert sol.minPathSum(new int[][]{{1,2,3},{4,5,6}}) == 12;
        assert sol.minPathSum(new int[][]{{1}}) == 1;
        assert sol.minPathSum(new int[][]{{1,2},{3,4}}) == 7;
        assert sol.minPathSum(new int[][]{{1,2,3}}) == 6;
        assert sol.minPathSum(new int[][]{{1},{2},{3}}) == 6;
        
        // minDistance
        assert sol.minDistance("horse", "ros") == 3;
        assert sol.minDistance("intention", "execution") == 5;
        assert sol.minDistance("", "") == 0;
        assert sol.minDistance("a", "") == 1;
        assert sol.minDistance("", "a") == 1;
        assert sol.minDistance("abc", "abc") == 0;
        
        // maximalSquare
        assert sol.maximalSquare(new char[][]{{'1','0','1','0','0'},{'1','0','1','1','1'},{'1','1','1','1','1'},{'1','0','0','1','0'}}) == 4;
        assert sol.maximalSquare(new char[][]{{'0','1'},{'1','0'}}) == 1;
        assert sol.maximalSquare(new char[][]{{'0'}}) == 0;
        assert sol.maximalSquare(new char[][]{{'1'}}) == 1;
        assert sol.maximalSquare(new char[][]{{'1','1'},{'1','1'}}) == 4;
        assert sol.maximalSquare(new char[][]{{'0','0'},{'0','0'}}) == 0;
        
        System.out.println("All tests passed!");
    }
}
