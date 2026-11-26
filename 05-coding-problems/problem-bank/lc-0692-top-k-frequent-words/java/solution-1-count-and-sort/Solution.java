import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Solution {
    public List<String> topKFrequent(String[] words, int k) {
        Map<String, Integer> counts = new HashMap<>();
        for (String word : words) {
            counts.put(word, counts.getOrDefault(word, 0) + 1);
        }
        List<String> unique = new ArrayList<>(counts.keySet());
        unique.sort((left, right) -> {
            int byCount = counts.get(right) - counts.get(left);
            if (byCount != 0) {
                return byCount;
            }
            return left.compareTo(right);
        });
        return new ArrayList<>(unique.subList(0, k));
    }
}
