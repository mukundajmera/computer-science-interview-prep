import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

class Solution {
    public List<Integer> findAnagrams(String s, String p) {
        List<Integer> result = new ArrayList<>();
        int windowSize = p.length();
        if (windowSize > s.length()) {
            return result;
        }
        char[] target = p.toCharArray();
        Arrays.sort(target);
        for (int start = 0; start + windowSize <= s.length(); start++) {
            char[] window = s.substring(start, start + windowSize).toCharArray();
            Arrays.sort(window);
            if (Arrays.equals(window, target)) {
                result.add(start);
            }
        }
        return result;
    }
}
