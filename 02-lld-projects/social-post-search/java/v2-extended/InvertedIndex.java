package v2_extended;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class InvertedIndex {
    private final Map<String, Set<String>> index = new ConcurrentHashMap<>();
    private final Map<String, Integer> docLengths = new ConcurrentHashMap<>();
    private final Map<String, Map<String, Integer>> termFreqs = new ConcurrentHashMap<>();
    private final Map<String, String> documents = new ConcurrentHashMap<>();
    private int totalDocs = 0;

    public synchronized void indexPost(String postId, String content) {
        if (documents.containsKey(postId)) {
            deletePost(postId);
        }

        List<String> tokens = Tokenizer.tokenize(content);
        documents.put(postId, content);
        docLengths.put(postId, tokens.size());
        totalDocs++;
        
        for (String token : tokens) {
            index.computeIfAbsent(token, k -> ConcurrentHashMap.newKeySet()).add(postId);
            termFreqs.computeIfAbsent(postId, k -> new ConcurrentHashMap<>())
                     .merge(token, 1, Integer::sum);
        }
    }

    public synchronized void deletePost(String postId) {
        if (!documents.containsKey(postId)) {
            return;
        }

        totalDocs--;
        documents.remove(postId);
        docLengths.remove(postId);
        
        Map<String, Integer> freqs = termFreqs.remove(postId);
        if (freqs != null) {
            for (String token : freqs.keySet()) {
                Set<String> tokenDocs = index.get(token);
                if (tokenDocs != null) {
                    tokenDocs.remove(postId);
                    if (tokenDocs.isEmpty()) {
                        index.remove(token);
                    }
                }
            }
        }
    }

    public List<String> searchTerm(String term, int limit) {
        Set<String> postIds = index.getOrDefault(term, Collections.emptySet());
        return postIds.stream().limit(limit).collect(Collectors.toList());
    }
    
    public Map<String, Set<String>> getIndex() { return index; }
    public Map<String, Integer> getDocLengths() { return docLengths; }
    public Map<String, Map<String, Integer>> getTermFreqs() { return termFreqs; }
    public Map<String, String> getDocuments() { return documents; }
    public int getTotalDocs() { return totalDocs; }
}
