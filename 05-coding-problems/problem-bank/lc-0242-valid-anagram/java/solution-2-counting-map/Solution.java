import java.util.HashMap;
import java.util.Map;

class Solution {
    public boolean isAnagram(String s, String t) {
        if (s.length() != t.length()) {
            return false;
        }
        Map<Character, Integer> counts = new HashMap<>();
        for (int i = 0; i < s.length(); i++) {
            char ch = s.charAt(i);
            counts.put(ch, counts.getOrDefault(ch, 0) + 1);
        }
        for (int i = 0; i < t.length(); i++) {
            char ch = t.charAt(i);
            int next = counts.getOrDefault(ch, 0) - 1;
            if (next < 0) {
                return false;
            }
            if (next == 0) {
                counts.remove(ch);
            } else {
                counts.put(ch, next);
            }
        }
        return counts.isEmpty();
    }
}
