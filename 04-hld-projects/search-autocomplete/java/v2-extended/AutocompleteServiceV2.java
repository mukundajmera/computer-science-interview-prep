import java.util.AbstractMap;
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicReference;

/**
 * v2-extended search-autocomplete service. Each improvement is one the
 * project's own docs already call for:
 *
 * 1. Trending fast-path (FOLLOW-UPS.md #1): a sliding-window counter of
 *    recent queries is blended with the batch-built Trie at query time, so
 *    a spiking search shows up in minutes instead of waiting for the next
 *    offline rebuild.
 * 2. Personalized autocomplete (FOLLOW-UPS.md, "Variants and extensions"):
 *    a bounded per-user query history boosts suggestions the user has
 *    searched before. History per user is capped with oldest-first
 *    eviction so memory stays flat.
 * 3. Prefix-range sharding (FOLLOW-UPS.md #2): see PrefixShardRouterV2,
 *    which routes each prefix to the shard owning its first character.
 */
public class AutocompleteServiceV2 {
    private static final int MAX_PREFIX_LENGTH = 50;
    private static final int TOP_K = 5;

    private final AtomicReference<TrieNodeV2> root;
    private final Set<String> profanityBlacklist;
    private final QueryAggregatorV2 aggregator;
    // Blending weights: score = batchFrequency
    //   + trendingWeight * occurrences inside the recent window
    //   + personalWeight  * occurrences in this user's own history
    private final long trendingWeight;
    private final long personalWeight;
    private final int maxUserQueries;
    private final ConcurrentHashMap<String, LinkedHashMap<String, Long>> userHistories;

    public AutocompleteServiceV2(Set<String> profanityBlacklist) {
        this(profanityBlacklist, 50L, 10L, 1000, 60L, 5);
    }

    public AutocompleteServiceV2(Set<String> profanityBlacklist, long trendingWeight,
                                 long personalWeight, int maxUserQueries,
                                 long bucketSeconds, int windowBuckets) {
        this.root = new AtomicReference<>(new TrieNodeV2());
        this.profanityBlacklist = profanityBlacklist != null
                ? new HashSet<>(profanityBlacklist) : new HashSet<>();
        this.aggregator = new QueryAggregatorV2(bucketSeconds, windowBuckets);
        this.trendingWeight = trendingWeight;
        this.personalWeight = personalWeight;
        this.maxUserQueries = maxUserQueries;
        this.userHistories = new ConcurrentHashMap<>();
    }

    public QueryAggregatorV2 getAggregator() {
        return aggregator;
    }

    /** Log a query globally (batch + trending) and into the user's history. */
    public void recordUserQuery(String userId, String query, long epochSeconds) {
        aggregator.addQuery(query, epochSeconds);
        if (userId == null || userId.isEmpty() || query == null || query.trim().isEmpty()) {
            return;
        }
        String clean = query.toLowerCase();
        if (isProfane(clean)) {
            return;
        }
        LinkedHashMap<String, Long> history =
                userHistories.computeIfAbsent(userId, k -> new LinkedHashMap<>());
        synchronized (history) {
            Long existing = history.get(clean);
            if (existing != null) {
                history.put(clean, existing + 1);
            } else {
                if (history.size() >= maxUserQueries) {
                    Iterator<String> it = history.keySet().iterator();
                    it.next();
                    it.remove();
                }
                history.put(clean, 1L);
            }
        }
    }

    public void rebuildTrie(Map<String, Long> queryFrequencies) {
        TrieNodeV2 newRoot = new TrieNodeV2();
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

    private void insertQuery(TrieNodeV2 node, String query, long frequency) {
        TrieNodeV2 curr = node;
        for (int i = 0; i < query.length(); i++) {
            char c = query.charAt(i);
            curr.getChildren().putIfAbsent(c, new TrieNodeV2());
            curr = curr.getChildren().get(c);
        }
        curr.setTerminal(true);
        curr.setFrequency(frequency);
    }

    private List<TrieNodeV2.Suggestion> precomputeTopSuggestions(TrieNodeV2 node, String prefix) {
        List<TrieNodeV2.Suggestion> allSuggestions = new ArrayList<>();
        if (node.isTerminal()) {
            allSuggestions.add(new TrieNodeV2.Suggestion(prefix, node.getFrequency()));
        }

        for (Map.Entry<Character, TrieNodeV2> entry : node.getChildren().entrySet()) {
            allSuggestions.addAll(precomputeTopSuggestions(entry.getValue(), prefix + entry.getKey()));
        }

        allSuggestions.sort((a, b) -> Long.compare(b.getFrequency(), a.getFrequency()));

        List<TrieNodeV2.Suggestion> topSuggestions =
                allSuggestions.subList(0, Math.min(TOP_K, allSuggestions.size()));
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

    /** Batch-only suggestions, identical in behavior to v1. */
    public List<String> getSuggestions(String prefix) {
        if (prefix == null || prefix.isEmpty()) {
            return Collections.emptyList();
        }

        String cleanPrefix = prefix.toLowerCase();
        if (cleanPrefix.length() > MAX_PREFIX_LENGTH) {
            cleanPrefix = cleanPrefix.substring(0, MAX_PREFIX_LENGTH);
        }

        TrieNodeV2 curr = root.get();
        for (int i = 0; i < cleanPrefix.length(); i++) {
            char c = cleanPrefix.charAt(i);
            curr = curr.getChildren().get(c);
            if (curr == null) {
                return Collections.emptyList();
            }
        }

        List<String> results = new ArrayList<>();
        for (TrieNodeV2.Suggestion suggestion : curr.getTopSuggestions()) {
            results.add(suggestion.getQuery());
        }
        return results;
    }

    /**
     * Global Trie merged with the trending fast-path and user history.
     * Candidates come from the prefix node's cached top-k plus any query in
     * the recent window or the user's own history that starts with the
     * prefix (even if the Trie was built before it appeared). Batch
     * frequency comes from the Trie cache when present, else from the
     * aggregator's all-time counts.
     */
    public List<String> getBlendedSuggestions(String prefix, long epochSeconds, String userId) {
        if (prefix == null || prefix.isEmpty()) {
            return Collections.emptyList();
        }

        String cleanPrefix = prefix.toLowerCase();
        if (cleanPrefix.length() > MAX_PREFIX_LENGTH) {
            cleanPrefix = cleanPrefix.substring(0, MAX_PREFIX_LENGTH);
        }

        Map<String, Long> candidates = new HashMap<>();
        TrieNodeV2 curr = root.get();
        for (int i = 0; i < cleanPrefix.length(); i++) {
            curr = curr.getChildren().get(cleanPrefix.charAt(i));
            if (curr == null) {
                break;
            }
        }
        if (curr != null) {
            for (TrieNodeV2.Suggestion suggestion : curr.getTopSuggestions()) {
                candidates.put(suggestion.getQuery(), suggestion.getFrequency());
            }
        }

        Map<String, Long> totals = aggregator.getAggregatedFrequencies();
        Map<String, Long> trending = aggregator.getTrendingCounts(epochSeconds);
        for (String query : trending.keySet()) {
            if (query.startsWith(cleanPrefix) && !candidates.containsKey(query)
                    && !isProfane(query)) {
                candidates.put(query, totals.getOrDefault(query, 0L));
            }
        }

        Map<String, Long> personal = new HashMap<>();
        if (userId != null) {
            LinkedHashMap<String, Long> history = userHistories.get(userId);
            if (history != null) {
                synchronized (history) {
                    personal.putAll(history);
                }
            }
            for (String query : personal.keySet()) {
                if (query.startsWith(cleanPrefix) && !candidates.containsKey(query)
                        && !isProfane(query)) {
                    candidates.put(query, totals.getOrDefault(query, 0L));
                }
            }
        }

        List<Map.Entry<String, Long>> scored = new ArrayList<>();
        for (Map.Entry<String, Long> entry : candidates.entrySet()) {
            long score = entry.getValue()
                    + trendingWeight * trending.getOrDefault(entry.getKey(), 0L)
                    + personalWeight * personal.getOrDefault(entry.getKey(), 0L);
            scored.add(new AbstractMap.SimpleEntry<>(entry.getKey(), score));
        }
        scored.sort((a, b) -> {
            int cmp = Long.compare(b.getValue(), a.getValue());
            return cmp != 0 ? cmp : a.getKey().compareTo(b.getKey());
        });

        List<String> results = new ArrayList<>();
        for (int i = 0; i < Math.min(TOP_K, scored.size()); i++) {
            results.add(scored.get(i).getKey());
        }
        return results;
    }
}
