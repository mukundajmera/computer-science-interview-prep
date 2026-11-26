import java.util.ArrayDeque;
import java.util.HashSet;
import java.util.List;
import java.util.Queue;
import java.util.Set;

class Solution {
    public int ladderLength(String beginWord, String endWord, List<String> wordList) {
        Set<String> unvisited = new HashSet<>(wordList);
        if (!unvisited.contains(endWord)) {
            return 0;
        }

        Queue<String> queue = new ArrayDeque<>();
        queue.add(beginWord);
        int distance = 1;

        while (!queue.isEmpty()) {
            int levelSize = queue.size();
            for (int i = 0; i < levelSize; i++) {
                String word = queue.remove();
                if (word.equals(endWord)) {
                    return distance;
                }
                for (String candidate : List.copyOf(unvisited)) {
                    if (differsByOne(word, candidate)) {
                        unvisited.remove(candidate);
                        queue.add(candidate);
                    }
                }
            }
            distance++;
        }
        return 0;
    }

    private boolean differsByOne(String a, String b) {
        int differences = 0;
        for (int i = 0; i < a.length(); i++) {
            if (a.charAt(i) != b.charAt(i)) {
                differences++;
                if (differences > 1) {
                    return false;
                }
            }
        }
        return differences == 1;
    }
}
