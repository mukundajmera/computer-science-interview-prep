import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        Map<String, List<String>> groups = new HashMap<>();
        for (String word : strs) {
            String key = countKey(word);
            groups.computeIfAbsent(key, unused -> new ArrayList<>()).add(word);
        }

        List<List<String>> result = new ArrayList<>();
        for (List<String> group : groups.values()) {
            Collections.sort(group);
            result.add(group);
        }
        return result;
    }

    private String countKey(String word) {
        int[] counts = new int[26];
        for (int i = 0; i < word.length(); i++) {
            counts[word.charAt(i) - 'a']++;
        }
        StringBuilder builder = new StringBuilder();
        for (int count : counts) {
            builder.append('#').append(count);
        }
        return builder.toString();
    }
}
