package v3_optimized;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

public class InvertedIndex {
    private final Map<String, Set<String>> index = new ConcurrentHashMap<>();
    private final Map<String, Integer> docLengths = new ConcurrentHashMap<>();
    private final Map<String, Map<String, Integer>> termFreqs = new ConcurrentHashMap<>();
    private final Map<String, String> documents = new ConcurrentHashMap<>();
    private int totalDocs = 0;

    public synchronized void deletePost(String postId) {
        if (!documents.containsKey(postId)) {
            return;
        }

        Map<String, Integer> freqs = termFreqs.remove(postId);
        if (freqs != null) {
            for (String term : freqs.keySet()) {
                Set<String> postIds = index.get(term);
                if (postIds != null) {
                    postIds.remove(postId);
                    if (postIds.isEmpty()) {
                        index.remove(term);
                    }
                }
            }
        }

        documents.remove(postId);
        docLengths.remove(postId);
        totalDocs--;
    }

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

