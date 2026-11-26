import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Queue;
import java.util.Set;

class Solution {
    public int ladderLength(String beginWord, String endWord, List<String> wordList) {
        if (!wordList.contains(endWord)) {
            return 0;
        }

        Map<String, List<String>> byPattern = new HashMap<>();
        for (String word : wordList) {
            for (String pattern : patterns(word)) {
                byPattern.computeIfAbsent(pattern, unused -> new ArrayList<>()).add(word);
            }
        }

        Queue<String> queue = new ArrayDeque<>();
        Set<String> visited = new HashSet<>();
        queue.add(beginWord);
        visited.add(beginWord);
        int distance = 1;

        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            for (int i = 0; i < levelSize; i++) {
                String word = queue.remove();
                if (word.equals(endWord)) {
                    return distance;
                }
                for (String pattern : patterns(word)) {
                    List<String> neighbors = byPattern.get(pattern);
                    if (neighbors == null) {
                        continue;
                    }
                    for (String neighbor : neighbors) {
                        if (visited.add(neighbor)) {
                            queue.add(neighbor);
                        }
                    }
                    neighbors.clear();
                }
            }
            distance++;
        }
        return 0;
    }

    private List<String> patterns(String word) {
        List<String> result = new ArrayList<>();
        for (int i = 0; i < word.length(); i++) {
            result.add(word.substring(0, i) + "*" + word.substring(i + 1));
        }
        return result;
    }
}
