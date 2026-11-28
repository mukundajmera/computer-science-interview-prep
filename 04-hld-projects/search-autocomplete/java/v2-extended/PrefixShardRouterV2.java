import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.List;
import java.util.Set;

/**
 * Routes queries to per-shard services by first-character range, the
 * sharding-by-prefix scheme from FOLLOW-UPS.md #2 ('a'-'c' on server 1,
 * 'd'-'f' on server 2, and so on). Autocomplete asks for one exact
 * prefix, so the first character deterministically picks a single shard
 * and no scatter-gather is needed. Non-letter prefixes land on a
 * catch-all (the last shard).
 */
public class PrefixShardRouterV2 {
    private static final char[] DEFAULT_BOUNDARIES = {'a', 'd', 'g', 'j', 'm', 'p', 's', 'v', 'y'};

    private final char[] boundaries;
    private final List<AutocompleteServiceV2> shards;

    public PrefixShardRouterV2(Set<String> profanityBlacklist) {
        this(null, profanityBlacklist);
    }

    public PrefixShardRouterV2(char[] shardBoundaries, Set<String> profanityBlacklist) {
        this.boundaries = shardBoundaries != null
                ? shardBoundaries.clone() : DEFAULT_BOUNDARIES.clone();
        Arrays.sort(this.boundaries);
        this.shards = new ArrayList<>();
        for (int i = 0; i < this.boundaries.length; i++) {
            this.shards.add(new AutocompleteServiceV2(profanityBlacklist));
        }
    }

    /** Owning shard for a prefix, or -1 for a null/empty prefix. */
    public int shardIndex(String prefix) {
        if (prefix == null || prefix.isEmpty()) {
            return -1;
        }
        char first = Character.toLowerCase(prefix.charAt(0));
        if (first < 'a' || first > 'z') {
            return boundaries.length - 1; // catch-all shard
        }
        int index = 0;
        for (int i = 0; i < boundaries.length; i++) {
            if (first >= boundaries[i]) {
                index = i;
            }
        }
        return index;
    }

    public int shardCount() {
        return shards.size();
    }

    public AutocompleteServiceV2 getShard(int index) {
        return shards.get(index);
    }

    public void addQuery(String query, long epochSeconds) {
        int index = shardIndex(query);
        if (index < 0) {
            return;
        }
        shards.get(index).getAggregator().addQuery(query, epochSeconds);
    }

    public void recordUserQuery(String userId, String query, long epochSeconds) {
        int index = shardIndex(query);
        if (index < 0) {
            return;
        }
        shards.get(index).recordUserQuery(userId, query, epochSeconds);
    }

    public void rebuildAll() {
        for (AutocompleteServiceV2 shard : shards) {
            shard.rebuildTrie(shard.getAggregator().getAggregatedFrequencies());
        }
    }

    public List<String> getSuggestions(String prefix) {
        int index = shardIndex(prefix);
        if (index < 0) {
            return Collections.emptyList();
        }
        return shards.get(index).getSuggestions(prefix);
    }

    public List<String> getBlendedSuggestions(String prefix, long epochSeconds, String userId) {
        int index = shardIndex(prefix);
        if (index < 0) {
            return Collections.emptyList();
        }
        return shards.get(index).getBlendedSuggestions(prefix, epochSeconds, userId);
    }
}
