import java.util.*;

class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    boolean isEndOfWord = false;
}

public class Trie {
    private TrieNode root = new TrieNode();

    public void insert(String word) {
        TrieNode node = root;
        for (char c : word.toCharArray()) {
            node.children.putIfAbsent(c, new TrieNode());
            node = node.children.get(c);
        }
        node.isEndOfWord = true;
    }

    private TrieNode searchPrefix(String prefix) {
        TrieNode node = root;
        for (char c : prefix.toCharArray()) {
            if (!node.children.containsKey(c)) {
                return null;
            }
            node = node.children.get(c);
        }
        return node;
    }

    private void dfs(TrieNode node, String prefix, List<String> results) {
        if (results.size() >= 10) return;
        if (node.isEndOfWord) {
            results.add(prefix);
        }
        
        // Sort keys to ensure deterministic output
        List<Character> keys = new ArrayList<>(node.children.keySet());
        Collections.sort(keys);
        
        for (char c : keys) {
            dfs(node.children.get(c), prefix + c, results);
        }
    }

    public List<String> autocomplete(String prefix) {
        TrieNode node = searchPrefix(prefix);
        if (node == null) return new ArrayList<>();
        
        List<String> results = new ArrayList<>();
        dfs(node, prefix, results);
        return results;
    }

    public static void main(String[] args) {
        Trie t = new Trie();
        t.insert("apple");
        t.insert("app");
        t.insert("apricot");
        t.insert("banana");

        // Test 1: prefix matches
        List<String> res1 = t.autocomplete("ap");
        assert res1.equals(Arrays.asList("app", "apple", "apricot")) : "Test 1 Failed";

        // Test 2: no match
        List<String> res2 = t.autocomplete("b");
        assert res2.equals(Arrays.asList("banana")) : "Test 2 Failed";
        
        // Test 3: no match non-existent
        List<String> res3 = t.autocomplete("c");
        assert res3.isEmpty() : "Test 3 Failed";

        // Test 4: exact match
        List<String> res4 = t.autocomplete("apple");
        assert res4.equals(Arrays.asList("apple")) : "Test 4 Failed";

        // Test 5: limit 10
        Trie tLimit = new Trie();
        for (int i = 0; i < 15; i++) {
            tLimit.insert(String.format("app%02d", i));
        }
        List<String> res5 = tLimit.autocomplete("app");
        assert res5.size() == 10 : "Test 5 Failed";

        // Test 6: empty prefix
        Trie tEmpty = new Trie();
        tEmpty.insert("a");
        tEmpty.insert("b");
        List<String> res6 = tEmpty.autocomplete("");
        assert res6.equals(Arrays.asList("a", "b")) : "Test 6 Failed";

        System.out.println("Java V1 tests passed.");
    }
}
