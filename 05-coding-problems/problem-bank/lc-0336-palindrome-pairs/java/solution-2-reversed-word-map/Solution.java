import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

class Solution {
    public List<List<Integer>> palindromePairs(String[] words) {
        Map<String, Integer> indexByWord = new HashMap<>();
        for (int i = 0; i < words.length; i++) {
            indexByWord.put(words[i], i);
        }
        Set<String> seen = new HashSet<>();
        List<List<Integer>> result = new ArrayList<>();
        for (int i = 0; i < words.length; i++) {
            String word = words[i];
            for (int split = 0; split <= word.length(); split++) {
                String prefix = word.substring(0, split);
                String suffix = word.substring(split);
                if (isPalindrome(prefix)) {
                    Integer match = indexByWord.get(reverse(suffix));
                    addPair(result, seen, match, i);
                }
                if (split != word.length() && isPalindrome(suffix)) {
                    Integer match = indexByWord.get(reverse(prefix));
                    addPair(result, seen, i, match);
                }
            }
        }
        return result;
    }

    private void addPair(List<List<Integer>> result, Set<String> seen, Integer left, Integer right) {
        if (left == null || right == null || left.equals(right)) {
            return;
        }
        String key = left + ":" + right;
        if (seen.add(key)) {
            result.add(Arrays.asList(left, right));
        }
    }

    private boolean isPalindrome(String value) {
        int left = 0;
        int right = value.length() - 1;
        while (left < right) {
            if (value.charAt(left++) != value.charAt(right--)) {
                return false;
            }
        }
        return true;
    }

    private String reverse(String value) {
        return new StringBuilder(value).reverse().toString();
    }
}
