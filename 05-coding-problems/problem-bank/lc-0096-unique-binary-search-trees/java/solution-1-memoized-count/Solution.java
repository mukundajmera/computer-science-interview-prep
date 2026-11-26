import java.util.*;
class Solution {
    private final Map<Integer, Integer> memo = new HashMap<>();
    public int numTrees(int n) {
        if (n <= 1) return 1;
        if (memo.containsKey(n)) return memo.get(n);
        int total = 0;
        for (int left = 0; left < n; left++) total += numTrees(left) * numTrees(n - 1 - left);
        memo.put(n, total);
        return total;
    }
}
