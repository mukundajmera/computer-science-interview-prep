import java.util.HashMap;
import java.util.Map;

class Solution {
    public String minWindow(String s, String t) {
        if (t.isEmpty()) {
            return "";
        }
        Map<Character, Integer> required = counts(t);
        String best = "";
        for (int start = 0; start < s.length(); start++) {
            Map<Character, Integer> window = new HashMap<>();
            int formed = 0;
            for (int end = start; end < s.length(); end++) {
                char ch = s.charAt(end);
                window.put(ch, window.getOrDefault(ch, 0) + 1);
                if (required.containsKey(ch) && window.get(ch).intValue() == required.get(ch).intValue()) {
                    formed++;
                }
                if (formed == required.size()) {
                    String candidate = s.substring(start, end + 1);
                    if (best.isEmpty() || candidate.length() < best.length()) {
                        best = candidate;
                    }
                    break;
                }
            }
        }
        return best;
    }

    private Map<Character, Integer> counts(String value) {
        Map<Character, Integer> counter = new HashMap<>();
        for (int i = 0; i < value.length(); i++) {
            char ch = value.charAt(i);
            counter.put(ch, counter.getOrDefault(ch, 0) + 1);
        }
        return counter;
    }
}
