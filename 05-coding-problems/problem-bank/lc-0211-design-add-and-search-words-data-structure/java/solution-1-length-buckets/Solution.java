import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class WordDictionary {
    private final Map<Integer, List<String>> byLength = new HashMap<>();

    public void addWord(String word) {
        byLength.computeIfAbsent(word.length(), unused -> new ArrayList<>()).add(word);
    }

    public boolean search(String word) {
        List<String> candidates = byLength.get(word.length());
        if (candidates == null) {
            return false;
        }
        for (String candidate : candidates) {
            if (matches(candidate, word)) {
                return true;
            }
        }
        return false;
    }

    private boolean matches(String candidate, String pattern) {
        for (int i = 0; i < candidate.length(); i++) {
            char query = pattern.charAt(i);
            if (query != '.' && query != candidate.charAt(i)) {
                return false;
            }
        }
        return true;
    }
}
