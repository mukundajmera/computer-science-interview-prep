import java.util.HashMap;
import java.util.Map;

class Solution {
    public boolean isIsomorphic(String s, String t) {
        if (s.length() != t.length()) {
            return false;
        }
        Map<Character, Character> forward = new HashMap<>();
        Map<Character, Character> backward = new HashMap<>();
        for (int i = 0; i < s.length(); i++) {
            char left = s.charAt(i);
            char right = t.charAt(i);
            if (forward.containsKey(left) && forward.get(left) != right) {
                return false;
            }
            if (backward.containsKey(right) && backward.get(right) != left) {
                return false;
            }
            forward.put(left, right);
            backward.put(right, left);
        }
        return true;
    }
}
