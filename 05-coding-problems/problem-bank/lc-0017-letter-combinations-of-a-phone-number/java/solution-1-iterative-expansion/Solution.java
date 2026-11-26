import java.util.ArrayList;
import java.util.List;

class Solution {
    private static final String[] MAP = {"", "", "abc", "def", "ghi", "jkl", "mno", "pqrs", "tuv", "wxyz"};

    public List<String> letterCombinations(String digits) {
        List<String> result = new ArrayList<>();
        if (digits.isEmpty()) {
            return result;
        }
        result.add("");
        for (char digit : digits.toCharArray()) {
            List<String> next = new ArrayList<>();
            for (String prefix : result) {
                for (char letter : MAP[digit - '0'].toCharArray()) {
                    next.add(prefix + letter);
                }
            }
            result = next;
        }
        return result;
    }
}
