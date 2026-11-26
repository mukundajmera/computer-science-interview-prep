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
        int[] target = new int[26];
        int[] window = new int[26];
        for (int i = 0; i < windowSize; i++) {
            target[p.charAt(i) - 'a']++;
            window[s.charAt(i) - 'a']++;
        }
        if (Arrays.equals(target, window)) {
            result.add(0);
        }
        for (int right = windowSize; right < s.length(); right++) {
            window[s.charAt(right) - 'a']++;
            window[s.charAt(right - windowSize) - 'a']--;
            if (Arrays.equals(target, window)) {
                result.add(right - windowSize + 1);
            }
        }
        return result;
    }
}
