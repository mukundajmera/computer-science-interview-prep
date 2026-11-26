import java.util.HashMap;
import java.util.Map;

class Solution {
    public String minWindow(String s, String t) {
        if (t.isEmpty()) {
            return "";
        }
        Map<Character, Integer> required = counts(t);
        Map<Character, Integer> window = new HashMap<>();
        int formed = 0;
        int left = 0;
        int bestStart = 0;
        int bestLength = Integer.MAX_VALUE;
        for (int right = 0; right < s.length(); right++) {
            char added = s.charAt(right);
            window.put(added, window.getOrDefault(added, 0) + 1);
            if (required.containsKey(added) && window.get(added).intValue() == required.get(added).intValue()) {
                formed++;
            }
            while (formed == required.size()) {
                if (right - left + 1 < bestLength) {
                    bestStart = left;
                    bestLength = right - left + 1;
                }
                char removed = s.charAt(left);
                window.put(removed, window.get(removed) - 1);
                if (required.containsKey(removed) && window.get(removed) < required.get(removed)) {
                    formed--;
                }
                left++;
            }
        }
        return bestLength == Integer.MAX_VALUE ? "" : s.substring(bestStart, bestStart + bestLength);
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
