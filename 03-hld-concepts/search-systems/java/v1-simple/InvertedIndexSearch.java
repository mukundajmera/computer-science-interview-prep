import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class InvertedIndexSearch {

    // Maps docId to original text
    private final Map<Integer, String> documents = new HashMap<>();

    // Maps term to a map of {docId: term_frequency_count}
    private final Map<String, Map<Integer, Integer>> index = new HashMap<>();

    // Maps docId to total number of terms in the document
    private final Map<Integer, Integer> docLengths = new HashMap<>();

    public void addDocument(int docId, String text) {
        documents.put(docId, text);
        List<String> tokens = tokenize(text);
        docLengths.put(docId, tokens.size());

        Map<String, Integer> termCounts = new HashMap<>();
        for (String token : tokens) {
            termCounts.put(token, termCounts.getOrDefault(token, 0) + 1);
        }

        for (Map.Entry<String, Integer> entry : termCounts.entrySet()) {
            String term = entry.getKey();
            int count = entry.getValue();
            index.computeIfAbsent(term, k -> new HashMap<>()).put(docId, count);
        }
    }

    private List<String> tokenize(String text) {
        text = text.toLowerCase();
        text = text.replaceAll("[^a-z0-9\\s]", "");
        String[] parts = text.split("\\s+");
        List<String> tokens = new ArrayList<>();
        for (String part : parts) {
            if (!part.isEmpty()) {
                tokens.add(part);
            }
        }
        return tokens;
    }

    private double tf(String term, int docId) {
        Map<Integer, Integer> docFreqs = index.get(term);
        if (docFreqs == null) {
            return 0.0;
        }
        int tfCount = docFreqs.getOrDefault(docId, 0);
        int docLength = docLengths.getOrDefault(docId, 0);
        if (docLength == 0) {
            return 0.0;
        }
        return (double) tfCount / docLength;
    }

    private double idf(String term) {
        int nDocs = documents.size();
        Map<Integer, Integer> docFreqs = index.get(term);
        int df = (docFreqs == null) ? 0 : docFreqs.size();
        if (df == 0 || nDocs == 0) {
            return 0.0;
        }
        return Math.log((1.0 + nDocs) / (1.0 + df)) + 1.0;
    }

    public static class SearchResult {
        public final int docId;
        public final double score;

        public SearchResult(int docId, double score) {
            this.docId = docId;
            this.score = score;
        }
    }

    public List<SearchResult> search(String query, String operator) {
        List<String> tokens = tokenize(query);
        if (tokens.isEmpty()) {
            return new ArrayList<>();
        }

        Set<Integer> matchingDocs = new HashSet<>();
        if ("AND".equalsIgnoreCase(operator)) {
            Map<Integer, Integer> firstTermDocs = index.get(tokens.get(0));
            if (firstTermDocs != null) {
                matchingDocs.addAll(firstTermDocs.keySet());
            }
            for (int i = 1; i < tokens.size(); i++) {
                Map<Integer, Integer> termDocs = index.get(tokens.get(i));
                if (termDocs == null) {
                    matchingDocs.clear();
                    break;
                }
                matchingDocs.retainAll(termDocs.keySet());
            }
        } else { // OR
            for (String token : tokens) {
                Map<Integer, Integer> termDocs = index.get(token);
                if (termDocs != null) {
                    matchingDocs.addAll(termDocs.keySet());
                }
            }
        }

        List<SearchResult> results = new ArrayList<>();
        for (int docId : matchingDocs) {
            double score = 0.0;
            for (String token : tokens) {
                score += tf(token, docId) * idf(token);
            }
            if (score > 0) {
                results.add(new SearchResult(docId, score));
            }
        }

        results.sort((a, b) -> {
            int scoreCompare = Double.compare(b.score, a.score);
            if (scoreCompare != 0) {
                return scoreCompare;
            }
            return Integer.compare(a.docId, b.docId);
        });

        return results;
    }
}
