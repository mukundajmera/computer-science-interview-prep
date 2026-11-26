import java.util.*;
class Solution {
    private String source;
    private String target;
    private Integer[][] memo;
    public int numDistinct(String s, String t) {
        source = s;
        target = t;
        memo = new Integer[s.length() + 1][t.length() + 1];
        return count(0, 0);
    }
    private int count(int i, int j) {
        if (j == target.length()) return 1;
        if (i == source.length()) return 0;
        if (memo[i][j] != null) return memo[i][j];
        int total = count(i + 1, j);
        if (source.charAt(i) == target.charAt(j)) total += count(i + 1, j + 1);
        memo[i][j] = total;
        return total;
    }
}
