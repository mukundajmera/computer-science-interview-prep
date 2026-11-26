package v2_extended;

import java.util.*;

public class SearchRankingService {
    private final InvertedIndex index;
    private final double k1 = 1.5;
    private final double b = 0.75;

    public SearchRankingService(InvertedIndex index) {
        this.index = index;
    }

    public List<String> rank(String rawQuery, List<String> candidatePostIds) {
        List<String> queryTerms = Tokenizer.tokenize(rawQuery);
        if (queryTerms.isEmpty() || candidatePostIds.isEmpty()) {
            return candidatePostIds;
        }

        double avgdl = 0;
        if (index.getTotalDocs() > 0) {
            int totalLen = index.getDocLengths().values().stream().mapToInt(Integer::intValue).sum();
            avgdl = (double) totalLen / index.getTotalDocs();
        }

        List<Map.Entry<String, Double>> scores = new ArrayList<>();
        for (String postId : candidatePostIds) {
            double score = 0.0;
            int docLen = index.getDocLengths().getOrDefault(postId, 0);
            
            Map<String, Integer> tfs = index.getTermFreqs().getOrDefault(postId, Collections.emptyMap());
            for (String term : queryTerms) {
                int tf = tfs.getOrDefault(term, 0);
                if (tf == 0) continue;
                
                int df = index.getIndex().getOrDefault(term, Collections.emptySet()).size();
                int N = index.getTotalDocs();
                
                double idf = Math.log(1 + (N - df + 0.5) / (df + 0.5));
                double termScore = idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * docLen / (avgdl == 0 ? 1 : avgdl))));
                score += termScore;
            }
            scores.add(new AbstractMap.SimpleEntry<>(postId, score));
        }

        scores.sort((e1, e2) -> {
            int cmp = Double.compare(e2.getValue(), e1.getValue());
            if (cmp == 0) return e1.getKey().compareTo(e2.getKey());
            return cmp;
        });

        List<String> ranked = new ArrayList<>();
        for (Map.Entry<String, Double> entry : scores) {
            ranked.add(entry.getKey());
        }
        return ranked;
    }
}
