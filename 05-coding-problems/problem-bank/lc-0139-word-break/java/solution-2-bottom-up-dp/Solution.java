import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;

class Solution {
    public boolean wordBreak(String s, List<String> wordDict) {
        List<String> words = new ArrayList<>(new HashSet<>(wordDict));
        boolean[] dp = new boolean[s.length() + 1];
        dp[0] = true;

        for (int start = 0; start < s.length(); start++) {
            if (!dp[start]) {
                continue;
            }
            for (String word : words) {
                int end = start + word.length();
                if (end <= s.length() && s.startsWith(word, start)) {
                    dp[end] = true;
                }
            }
        }

        return dp[s.length()];
    }
}
