"""v2-extended search-autocomplete service.

A real step up from v1-basic. Each improvement is one the project's own
docs already call for:

1. Trending fast-path (FOLLOW-UPS.md #1): a sliding-window counter of
   recent queries is blended with the batch-built Trie at query time, so a
   search that spikes 1000x shows up in minutes instead of waiting for the
   next offline rebuild. The batch path stays untouched; the fast path is
   merged on read, exactly the "smaller Trie of recent heavy hitters
   merged at query time" the docs describe.
2. Personalized autocomplete (FOLLOW-UPS.md, "Variants and extensions"):
   a bounded per-user query history boosts suggestions the user has
   searched before, merged with global results at query time. History per
   user is capped (oldest entries evicted) so memory stays flat.
3. Prefix-range sharding (FOLLOW-UPS.md #2): PrefixShardRouterV2 routes a
   query to the shard that owns its first-character range, the way the
   docs split 'a'-'c' on server 1, 'd'-'f' on server 2, and so on. Exact
   prefix lookup is deterministic, so no scatter-gather is needed.

Thread safety matches v1: a single lock guards all mutable service state,
and the aggregator uses its own lock around its maps.
"""

import bisect
import threading
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class TrieNode:
    children: Dict[str, 'TrieNode'] = field(default_factory=dict)
    is_terminal: bool = False
    frequency: int = 0
    top_suggestions: List[Dict[str, int]] = field(default_factory=list)


class QueryAggregatorV2:
    """All-time counts plus a sliding window of recent (trending) counts.

    Counts land in fixed-size time buckets; buckets older than the window
    are evicted on write, so memory is bounded by the window length.
    """

    def __init__(self, bucket_seconds: int = 60, window_buckets: int = 5):
        self.bucket_seconds = bucket_seconds
        self.window_buckets = window_buckets
        self.total_counts = defaultdict(int)
        self.buckets = defaultdict(lambda: defaultdict(int))
        self.lock = threading.Lock()

    def add_query(self, query: str, timestamp: Optional[float] = None) -> None:
        if not query or not query.strip():
            return
        clean_query = query.lower()
        ts = time.time() if timestamp is None else timestamp
        bucket = int(ts // self.bucket_seconds)
        with self.lock:
            self.total_counts[clean_query] += 1
            self.buckets[bucket][clean_query] += 1
            oldest = bucket - self.window_buckets + 1
            for index in [i for i in self.buckets if i < oldest]:
                del self.buckets[index]

    def get_aggregated_frequencies(self) -> Dict[str, int]:
        with self.lock:
            return dict(self.total_counts)

    def get_trending_counts(self, timestamp: Optional[float] = None) -> Dict[str, int]:
        """Per-query counts inside the current sliding window."""
        ts = time.time() if timestamp is None else timestamp
        current = int(ts // self.bucket_seconds)
        oldest = current - self.window_buckets + 1
        trending = defaultdict(int)
        with self.lock:
            for index, counts in self.buckets.items():
                if oldest <= index <= current:
                    for query, count in counts.items():
                        trending[query] += count
        return dict(trending)


class SearchAutocompleteServiceV2:
    MAX_PREFIX_LENGTH = 50
    TOP_K = 5

    def __init__(self, profanity_blacklist: Optional[Set[str]] = None,
                 trending_weight: int = 50, personal_weight: int = 10,
                 max_user_queries: int = 1000,
                 bucket_seconds: int = 60, window_buckets: int = 5):
        self.root = TrieNode()
        self.profanity_blacklist = profanity_blacklist or set()
        self.aggregator = QueryAggregatorV2(bucket_seconds, window_buckets)
        # Blending weights for the fast paths. score(query) =
        #   batch_frequency
        #   + trending_weight * occurrences inside the recent window
        #   + personal_weight  * occurrences in this user's own history
        self.trending_weight = trending_weight
        self.personal_weight = personal_weight
        self.max_user_queries = max_user_queries
        self.user_histories = {}  # user_id -> {query: count}, insertion ordered
        self.lock = threading.Lock()

    def add_query_log(self, query: str, timestamp: Optional[float] = None) -> None:
        if not query or not query.strip():
            return
        clean_query = query.lower()
        if self._is_profane(clean_query):
            return
        self.aggregator.add_query(clean_query, timestamp)

    def record_user_query(self, user_id: str, query: str,
                          timestamp: Optional[float] = None) -> None:
        """Log a query globally (batch + trending) and into user history."""
        self.add_query_log(query, timestamp)
        if not user_id or not query or not query.strip():
            return
        clean_query = query.lower()
        if self._is_profane(clean_query):
            return
        with self.lock:
            history = self.user_histories.setdefault(user_id, {})
            if clean_query in history:
                history[clean_query] += 1
            else:
                if len(history) >= self.max_user_queries:
                    oldest = next(iter(history))
                    del history[oldest]
                history[clean_query] = 1

    def _is_profane(self, query: str) -> bool:
        for word in query.split():
            if word in self.profanity_blacklist:
                return True
        return False

    def rebuild_trie(self) -> None:
        """Offline-style batch rebuild with an atomic root swap, as in v1."""
        new_root = TrieNode()
        current_counts = self.aggregator.get_aggregated_frequencies()

        for query, freq in current_counts.items():
            if self._is_profane(query):
                continue
            self._insert_query(new_root, query, freq)

        self._precompute_top_suggestions(new_root, "")

        with self.lock:
            self.root = new_root

    def _insert_query(self, root: TrieNode, query: str, freq: int) -> None:
        curr = root
        for char in query:
            if char not in curr.children:
                curr.children[char] = TrieNode()
            curr = curr.children[char]
        curr.is_terminal = True
        curr.frequency = freq

    def _precompute_top_suggestions(self, node: TrieNode, prefix: str) -> List[Dict[str, int]]:
        all_suggestions = []

        if node.is_terminal:
            all_suggestions.append({"query": prefix, "frequency": node.frequency})

        for char, child_node in node.children.items():
            all_suggestions.extend(self._precompute_top_suggestions(child_node, prefix + char))

        # Sort by frequency descending, then lexicographically for tie-breaking
        all_suggestions.sort(key=lambda x: (-x["frequency"], x["query"]))

        node.top_suggestions = all_suggestions[:self.TOP_K]
        return node.top_suggestions

    def get_suggestions(self, prefix: str) -> List[str]:
        """Batch-only suggestions, identical in behavior to v1."""
        if not prefix:
            return []

        clean_prefix = prefix.lower()
        if len(clean_prefix) > self.MAX_PREFIX_LENGTH:
            clean_prefix = clean_prefix[:self.MAX_PREFIX_LENGTH]

        with self.lock:
            curr = self.root
            for char in clean_prefix:
                if char not in curr.children:
                    return []
                curr = curr.children[char]

            return [s["query"] for s in curr.top_suggestions]

    def get_blended_suggestions(self, prefix: str,
                                timestamp: Optional[float] = None,
                                user_id: Optional[str] = None) -> List[str]:
        """Global Trie merged with the trending fast-path and user history.

        Candidates come from the prefix node's cached top-k, plus any query
        seen in the recent window or in the user's own history that starts
        with the prefix (even if the Trie was built before it appeared).
        Batch frequency comes from the Trie cache when present, else from
        the aggregator's all-time counts.
        """
        if not prefix:
            return []

        clean_prefix = prefix.lower()
        if len(clean_prefix) > self.MAX_PREFIX_LENGTH:
            clean_prefix = clean_prefix[:self.MAX_PREFIX_LENGTH]

        candidates = {}
        with self.lock:
            curr = self.root
            for char in clean_prefix:
                if char not in curr.children:
                    curr = None
                    break
                curr = curr.children[char]
            if curr is not None:
                for suggestion in curr.top_suggestions:
                    candidates[suggestion["query"]] = suggestion["frequency"]

        totals = self.aggregator.get_aggregated_frequencies()
        trending = self.aggregator.get_trending_counts(timestamp)
        for query in trending:
            if query.startswith(clean_prefix) and query not in candidates \
                    and not self._is_profane(query):
                candidates[query] = totals.get(query, 0)

        personal = {}
        if user_id:
            with self.lock:
                personal = dict(self.user_histories.get(user_id, {}))
            for query in personal:
                if query.startswith(clean_prefix) and query not in candidates \
                        and not self._is_profane(query):
                    candidates[query] = totals.get(query, 0)

        scored = []
        for query, batch_freq in candidates.items():
            score = batch_freq \
                + self.trending_weight * trending.get(query, 0) \
                + self.personal_weight * personal.get(query, 0)
            scored.append((query, score))
        scored.sort(key=lambda x: (-x[1], x[0]))
        return [query for query, _ in scored[:self.TOP_K]]


class PrefixShardRouterV2:
    """Routes queries to per-shard services by first-character range.

    Mirrors FOLLOW-UPS.md #2: 'a'-'c' on server 1, 'd'-'f' on server 2,
    etc. Autocomplete asks for one exact prefix, so the first character
    deterministically picks a single shard and no scatter-gather is
    required. Non-letter prefixes land on a catch-all (the last shard).
    """

    DEFAULT_BOUNDARIES = ['a', 'd', 'g', 'j', 'm', 'p', 's', 'v', 'y']

    def __init__(self, shard_boundaries: Optional[List[str]] = None,
                 profanity_blacklist: Optional[Set[str]] = None,
                 **service_kwargs):
        boundaries = shard_boundaries or self.DEFAULT_BOUNDARIES
        self.boundaries = sorted(boundaries)
        self.shards = [
            SearchAutocompleteServiceV2(profanity_blacklist, **service_kwargs)
            for _ in self.boundaries
        ]

    def shard_index(self, prefix: str) -> Optional[int]:
        if not prefix:
            return None
        first = prefix.lower()[0]
        if not ('a' <= first <= 'z'):
            return len(self.boundaries) - 1  # catch-all shard
        return max(0, bisect.bisect_right(self.boundaries, first) - 1)

    def add_query_log(self, query: str, timestamp: Optional[float] = None) -> None:
        index = self.shard_index(query)
        if index is None:
            return
        self.shards[index].add_query_log(query, timestamp)

    def record_user_query(self, user_id: str, query: str,
                          timestamp: Optional[float] = None) -> None:
        index = self.shard_index(query)
        if index is None:
            return
        self.shards[index].record_user_query(user_id, query, timestamp)

    def rebuild_all(self) -> None:
        for shard in self.shards:
            shard.rebuild_trie()

    def get_suggestions(self, prefix: str) -> List[str]:
        index = self.shard_index(prefix)
        if index is None:
            return []
        return self.shards[index].get_suggestions(prefix)

    def get_blended_suggestions(self, prefix: str,
                                timestamp: Optional[float] = None,
                                user_id: Optional[str] = None) -> List[str]:
        index = self.shard_index(prefix)
        if index is None:
            return []
        return self.shards[index].get_blended_suggestions(prefix, timestamp, user_id)
