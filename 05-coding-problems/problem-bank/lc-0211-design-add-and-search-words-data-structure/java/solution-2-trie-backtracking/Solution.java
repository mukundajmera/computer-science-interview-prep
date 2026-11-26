import java.util.HashMap;
import java.util.Map;

class WordDictionary {
    private final Node root = new Node();

    public void addWord(String word) {
        Node node = root;
        for (int i = 0; i < word.length(); i++) {
            char ch = word.charAt(i);
            node = node.children.computeIfAbsent(ch, unused -> new Node());
        }
        node.word = true;
    }

    public boolean search(String word) {
        return search(word, 0, root);
    }

    private boolean search(String word, int index, Node node) {
        if (index == word.length()) {
            return node.word;
        }
        char ch = word.charAt(index);
        if (ch == '.') {
            for (Node child : node.children.values()) {
                if (search(word, index + 1, child)) {
                    return true;
                }
            }
            return false;
        }
        Node child = node.children.get(ch);
        return child != null && search(word, index + 1, child);
    }

    private static class Node {
        private final Map<Character, Node> children = new HashMap<>();
        private boolean word;
    }
}
