import java.util.HashSet;
import java.util.Set;

class Trie {
    private final Set<String> words = new HashSet<>();
    private final Set<String> prefixes = new HashSet<>();

    public void insert(String word) {
        words.add(word);
        for (int length = 1; length <= word.length(); length++) {
            prefixes.add(word.substring(0, length));
        }
    }

    public boolean search(String word) {
        return words.contains(word);
    }

    public boolean startsWith(String prefix) {
        return prefixes.contains(prefix);
    }
}
