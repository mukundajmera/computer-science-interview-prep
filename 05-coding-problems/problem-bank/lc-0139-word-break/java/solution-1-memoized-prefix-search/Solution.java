import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

class Solution {
    public boolean wordBreak(String s, List<String> wordDict) {
        List<String> words = new ArrayList<>(new HashSet<>(wordDict));
        Boolean[] memo = new Boolean[s.length() + 1];
        return canBreak(s, 0, words, memo);
    }

    private boolean canBreak(String s, int start, List<String> words, Boolean[] memo) {
        if (start == s.length()) {
            return true;
        }
        if (memo[start] != null) {
            return memo[start];
        }
        for (String word : words) {
            int end = start + word.length();
            if (end <= s.length() && s.startsWith(word, start) && canBreak(s, end, words, memo)) {
                memo[start] = true;
                return true;
            }
        }
        memo[start] = false;
        return false;
    }
}
