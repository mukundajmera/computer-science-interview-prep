import java.util.*;
import java.util.concurrent.atomic.AtomicReference;

public class AutocompleteService {
    private static final int MAX_PREFIX_LENGTH = 50;
    private static final int TOP_K = 5;

    private final AtomicReference<TrieNode> root;
    private final Set<String> profanityBlacklist;

    public AutocompleteService(Set<String> profanityBlacklist) {
        this.root = new AtomicReference<>(new TrieNode());
        this.profanityBlacklist = profanityBlacklist != null ? new HashSet<>(profanityBlacklist) : new HashSet<>();
    }

    public void rebuildTrie(Map<String, Long> queryFrequencies) {
        TrieNode newRoot = new TrieNode();
        for (Map.Entry<String, Long> entry : queryFrequencies.entrySet()) {
            String query = entry.getKey().toLowerCase();
            if (isProfane(query)) {
                continue;
            }
            insertQuery(newRoot, query, entry.getValue());
        }
        
        precomputeTopSuggestions(newRoot, "");
        
        this.root.set(newRoot);
    }

    private void insertQuery(TrieNode node, String query, long frequency) {
        TrieNode curr = node;
        for (int i = 0; i < query.length(); i++) {
            char c = query.charAt(i);
            curr.getChildren().putIfAbsent(c, new TrieNode());
            curr = curr.getChildren().get(c);
        }
        curr.setTerminal(true);
        curr.setFrequency(frequency);
    }

    private List<TrieNode.Suggestion> precomputeTopSuggestions(TrieNode node, String prefix) {
        List<TrieNode.Suggestion> allSuggestions = new ArrayList<>();
        if (node.isTerminal()) {
            allSuggestions.add(new TrieNode.Suggestion(prefix, node.getFrequency()));
        }
        
        for (Map.Entry<Character, TrieNode> entry : node.getChildren().entrySet()) {
            allSuggestions.addAll(precomputeTopSuggestions(entry.getValue(), prefix + entry.getKey()));
        }
        
        allSuggestions.sort((a, b) -> Long.compare(b.getFrequency(), a.getFrequency()));
        
        List<TrieNode.Suggestion> topSuggestions = allSuggestions.subList(0, Math.min(TOP_K, allSuggestions.size()));
        node.setTopSuggestions(new ArrayList<>(topSuggestions));
        
        return topSuggestions;
    }

    private boolean isProfane(String query) {
        for (String word : query.split("\\s+")) {
            if (profanityBlacklist.contains(word)) {
                return true;
            }
        }
        return false;
    }

    public List<String> getSuggestions(String prefix) {
        if (prefix == null || prefix.isEmpty()) {
            return Collections.emptyList();
        }
        
        String cleanPrefix = prefix.toLowerCase();
        if (cleanPrefix.length() > MAX_PREFIX_LENGTH) {
            cleanPrefix = cleanPrefix.substring(0, MAX_PREFIX_LENGTH);
        }

        TrieNode curr = root.get();
        for (int i = 0; i < cleanPrefix.length(); i++) {
            char c = cleanPrefix.charAt(i);
            curr = curr.getChildren().get(c);
            if (curr == null) {
                return Collections.emptyList();
            }
        }

        List<String> results = new ArrayList<>();
        for (TrieNode.Suggestion suggestion : curr.getTopSuggestions()) {
            results.add(suggestion.getQuery());
        }
        return results;
    }
}
