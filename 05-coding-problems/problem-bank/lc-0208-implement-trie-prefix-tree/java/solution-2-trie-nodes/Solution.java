import java.util.HashMap;
import java.util.Map;

class Trie {
    private final Node root = new Node();

    public void insert(String word) {
        Node node = root;
        for (int i = 0; i < word.length(); i++) {
            char ch = word.charAt(i);
            node = node.children.computeIfAbsent(ch, unused -> new Node());
        }
        node.word = true;
    }

    public boolean search(String word) {
        Node node = find(word);
        return node != null && node.word;
    }

    public boolean startsWith(String prefix) {
        return find(prefix) != null;
    }

    private Node find(String text) {
        Node node = root;
        for (int i = 0; i < text.length(); i++) {
            node = node.children.get(text.charAt(i));
            if (node == null) {
                return null;
            }
        }
        return node;
    }

    private static class Node {
        private final Map<Character, Node> children = new HashMap<>();
        private boolean word;
    }
}
