import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    public List<Integer> findSubstring(String s, String[] words) {
        List<Integer> result = new ArrayList<>();
        if (words.length == 0) {
            return result;
        }
        int wordLength = words[0].length();
        int totalLength = wordLength * words.length;
        Map<String, Integer> required = counts(words);
        for (int start = 0; start + totalLength <= s.length(); start++) {
            Map<String, Integer> seen = new HashMap<>();
            int used = 0;
            while (used < words.length) {
                int from = start + used * wordLength;
                String piece = s.substring(from, from + wordLength);
                int next = seen.getOrDefault(piece, 0) + 1;
                if (next > required.getOrDefault(piece, 0)) {
                    break;
                }
                seen.put(piece, next);
                used++;
            }
            if (used == words.length) {
                result.add(start);
            }
        }
        return result;
    }

    private Map<String, Integer> counts(String[] words) {
        Map<String, Integer> counter = new HashMap<>();
        for (String word : words) {
            counter.put(word, counter.getOrDefault(word, 0) + 1);
        }
        return counter;
    }
}
