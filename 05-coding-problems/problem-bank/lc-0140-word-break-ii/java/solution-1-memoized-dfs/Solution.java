import java.util.*;

class Solution {
    public List<String> wordBreak(String s, List<String> wordDict) {
        Set<String> dict = new HashSet<>(wordDict);
        Map<Integer, List<String>> memo = new HashMap<>();
        return dfs(s, 0, dict, memo);
    }

    private List<String> dfs(String s, int start, Set<String> dict, Map<Integer, List<String>> memo) {
        if (memo.containsKey(start)) {
            return memo.get(start);
        }

        List<String> results = new ArrayList<>();
        if (start == s.length()) {
            results.add("");
            return results;
        }

        for (int end = start + 1; end <= s.length(); end++) {
            String word = s.substring(start, end);
            if (dict.contains(word)) {
                List<String> subResults = dfs(s, end, dict, memo);
                for (String sub : subResults) {
                    if (sub.isEmpty()) {
                        results.add(word);
                    } else {
                        results.add(word + " " + sub);
                    }
                }
            }
        }

        memo.put(start, results);
        return results;
    }
}
