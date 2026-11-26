import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    public List<List<Integer>> palindromePairs(String[] words) {
        List<List<Integer>> result = new ArrayList<>();
        for (int i = 0; i < words.length; i++) {
            for (int j = 0; j < words.length; j++) {
                if (i != j && isPalindrome(words[i] + words[j])) {
                    result.add(Arrays.asList(i, j));
                }
            }
        }
        return result;
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
}
