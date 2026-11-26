import java.util.*;

class WordFreq implements Comparable<WordFreq> {
    String word;
    int frequency;

    public WordFreq(String word, int frequency) {
        this.word = word;
        this.frequency = frequency;
    }

    @Override
    public int compareTo(WordFreq other) {
        if (this.frequency != other.frequency) {
            return Integer.compare(other.frequency, this.frequency); // desc
        }
        return this.word.compareTo(other.word); // asc
    }
}

class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    List<WordFreq> topK = new ArrayList<>();
}

class Trie {
    TrieNode root = new TrieNode();
    int k;

    public Trie(int k) {
        this.k = k;
    }

    public void insert(String word, int frequency) {
        TrieNode node = root;
        updateTopK(node, word, frequency);
        for (char c : word.toCharArray()) {
            node.children.putIfAbsent(c, new TrieNode());
            node = node.children.get(c);
            updateTopK(node, word, frequency);
        }
    }

    private void updateTopK(TrieNode node, String word, int frequency) {
        boolean found = false;
        for (int i = 0; i < node.topK.size(); i++) {
            if (node.topK.get(i).word.equals(word)) {
                node.topK.set(i, new WordFreq(word, frequency));
                found = true;
                break;
            }
        }
        
        if (!found) {
            node.topK.add(new WordFreq(word, frequency));
        }
        
        Collections.sort(node.topK);
        
        if (node.topK.size() > k) {
            node.topK.remove(node.topK.size() - 1);
        }
    }

    public List<String> autocomplete(String prefix) {
        TrieNode node = root;
        for (char c : prefix.toCharArray()) {
            if (!node.children.containsKey(c)) {
                return new ArrayList<>();
            }
            node = node.children.get(c);
        }
        
        List<String> results = new ArrayList<>();
        for (WordFreq wf : node.topK) {
            results.add(wf.word);
        }
        return results;
    }
}

public class ShardedTrieManager {
    private int numShards;
    private int k;
    private Trie[] activeShards;
    private Trie[] snapshotShards;

    public ShardedTrieManager(int numShards, int k) {
        this.numShards = numShards;
        this.k = k;
        this.activeShards = new Trie[numShards];
        this.snapshotShards = new Trie[numShards];
        for (int i = 0; i < numShards; i++) {
            this.activeShards[i] = new Trie(k);
            this.snapshotShards[i] = new Trie(k);
        }
    }

    private int getShardIndex(String prefix) {
        if (prefix == null || prefix.isEmpty()) {
            return 0;
        }
        char c = Character.toLowerCase(prefix.charAt(0));
        if (c >= 'a' && c <= 'i') return 0;
        if (c >= 'j' && c <= 'r') return 1;
        return 2;
    }

    public void insert(String word, int frequency) {
        int shardIdx = getShardIndex(word);
        activeShards[shardIdx].insert(word, frequency);
    }

    public List<String> autocomplete(String prefix) {
        int shardIdx = getShardIndex(prefix);
        return activeShards[shardIdx].autocomplete(prefix);
    }

    public void swapSnapshot() {
        Trie[] temp = activeShards;
        activeShards = snapshotShards;
        snapshotShards = temp;
        
        // Clear old snapshots
        for (int i = 0; i < numShards; i++) {
            snapshotShards[i] = new Trie(k);
        }
    }

    public void buildSnapshot(List<WordFreq> data) {
        for (WordFreq wf : data) {
            int shardIdx = getShardIndex(wf.word);
            snapshotShards[shardIdx].insert(wf.word, wf.frequency);
        }
    }

    public static void main(String[] args) {
        // Test 1: distribution
        ShardedTrieManager m1 = new ShardedTrieManager(3, 5);
        m1.insert("apple", 10);
        m1.insert("mango", 20);
        m1.insert("zebra", 5);
        assert m1.autocomplete("a").equals(Arrays.asList("apple")) : "Test 1a Failed";
        assert m1.autocomplete("m").equals(Arrays.asList("mango")) : "Test 1b Failed";
        assert m1.autocomplete("z").equals(Arrays.asList("zebra")) : "Test 1c Failed";

        // Test 2: snapshot swap
        ShardedTrieManager m2 = new ShardedTrieManager(3, 5);
        m2.insert("apple", 10);
        assert m2.autocomplete("a").equals(Arrays.asList("apple")) : "Test 2a Failed";
        
        m2.buildSnapshot(Arrays.asList(new WordFreq("apricot", 20), new WordFreq("app", 15)));
        assert m2.autocomplete("a").equals(Arrays.asList("apple")) : "Test 2b Failed";
        
        m2.swapSnapshot();
        assert m2.autocomplete("a").equals(Arrays.asList("apricot", "app")) : "Test 2c Failed";

        // Test 3: empty prefix
        ShardedTrieManager m3 = new ShardedTrieManager(3, 5);
        m3.insert("apple", 10);
        m3.insert("mango", 20);
        assert m3.autocomplete("").equals(Arrays.asList("apple")) : "Test 3 Failed";

        // Test 4: no match
        ShardedTrieManager m4 = new ShardedTrieManager(3, 5);
        m4.insert("apple", 10);
        assert m4.autocomplete("b").isEmpty() : "Test 4 Failed";

        // Test 5: limit
        ShardedTrieManager m5 = new ShardedTrieManager(3, 2);
        m5.insert("apple", 10);
        m5.insert("app", 20);
        m5.insert("apricot", 30);
        assert m5.autocomplete("ap").equals(Arrays.asList("apricot", "app")) : "Test 5 Failed";

        // Test 6: build snapshot multiple
        ShardedTrieManager m6 = new ShardedTrieManager(3, 5);
        m6.buildSnapshot(Arrays.asList(
            new WordFreq("apple", 10),
            new WordFreq("mango", 20),
            new WordFreq("zebra", 30),
            new WordFreq("app", 5)
        ));
        m6.swapSnapshot();
        assert m6.autocomplete("a").equals(Arrays.asList("apple", "app")) : "Test 6a Failed";
        assert m6.autocomplete("m").equals(Arrays.asList("mango")) : "Test 6b Failed";
        assert m6.autocomplete("z").equals(Arrays.asList("zebra")) : "Test 6c Failed";

        System.out.println("Java V3 tests passed.");
    }
}
