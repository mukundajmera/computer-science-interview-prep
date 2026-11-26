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
    
    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        WordFreq wordFreq = (WordFreq) o;
        return Objects.equals(word, wordFreq.word);
    }
    
    @Override
    public String toString() {
        return word;
    }
}

class TrieNode {
    Map<Character, TrieNode> children = new HashMap<>();
    List<WordFreq> topK = new ArrayList<>();
}

public class Trie {
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

    public void decay(double factor) {
        decayNode(root, factor);
    }

    private void decayNode(TrieNode node, double factor) {
        List<WordFreq> newTopK = new ArrayList<>();
        for (WordFreq wf : node.topK) {
            int newFreq = (int) (wf.frequency * factor);
            if (newFreq > 0) {
                newTopK.add(new WordFreq(wf.word, newFreq));
            }
        }
        node.topK = newTopK;
        
        for (TrieNode child : node.children.values()) {
            decayNode(child, factor);
        }
    }

    public static void main(String[] args) {
        // Test 1: top k
        Trie t1 = new Trie(2);
        t1.insert("apple", 10);
        t1.insert("app", 20);
        t1.insert("apricot", 5);
        List<String> res1 = t1.autocomplete("ap");
        assert res1.equals(Arrays.asList("app", "apple")) : "Test 1 Failed";

        // Test 2: update frequency
        Trie t2 = new Trie(2);
        t2.insert("apple", 10);
        t2.insert("app", 20);
        t2.insert("apricot", 5);
        t2.insert("apricot", 30);
        List<String> res2 = t2.autocomplete("ap");
        assert res2.equals(Arrays.asList("apricot", "app")) : "Test 2 Failed";

        // Test 3: no match
        Trie t3 = new Trie(5);
        t3.insert("apple", 10);
        assert t3.autocomplete("b").isEmpty() : "Test 3 Failed";

        // Test 4: exact match
        Trie t4 = new Trie(5);
        t4.insert("apple", 10);
        assert t4.autocomplete("apple").equals(Arrays.asList("apple")) : "Test 4 Failed";

        // Test 5: decay
        Trie t5 = new Trie(2);
        t5.insert("apple", 10);
        t5.insert("app", 20);
        t5.decay(0.5);
        List<String> res5 = t5.autocomplete("ap");
        assert res5.equals(Arrays.asList("app", "apple")) : "Test 5 Failed";
        
        // Test 6: decay drop
        Trie t6 = new Trie(2);
        t6.insert("apple", 1);
        t6.decay(0.5);
        assert t6.autocomplete("a").isEmpty() : "Test 6 Failed";

        System.out.println("Java V2 tests passed.");
    }
}
