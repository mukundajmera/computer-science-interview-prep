import java.util.ArrayList;
import java.util.Collections;
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
        int totalWords = words.length;
        Map<String, Integer> required = counts(words);
        for (int offset = 0; offset < wordLength; offset++) {
            Map<String, Integer> window = new HashMap<>();
            int left = offset;
            int used = 0;
            for (int right = offset; right + wordLength <= s.length(); right += wordLength) {
                String word = s.substring(right, right + wordLength);
                if (!required.containsKey(word)) {
                    window.clear();
                    used = 0;
                    left = right + wordLength;
                    continue;
                }
                window.put(word, window.getOrDefault(word, 0) + 1);
                used++;
                while (window.get(word) > required.get(word)) {
                    String removed = s.substring(left, left + wordLength);
                    window.put(removed, window.get(removed) - 1);
                    used--;
                    left += wordLength;
                }
                if (used == totalWords) {
                    result.add(left);
                    String removed = s.substring(left, left + wordLength);
                    window.put(removed, window.get(removed) - 1);
                    used--;
                    left += wordLength;
                }
            }
        }
        Collections.sort(result);
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
