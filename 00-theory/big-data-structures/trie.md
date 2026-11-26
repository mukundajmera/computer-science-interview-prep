# Trie

## Interview Mental Model

A trie is a prefix index. Each edge consumes one symbol, and each node represents the prefix formed by the path from the root to that node.

The key move in interviews is to separate three ideas:

1. A path exists: this prefix exists.
2. A terminal marker is set: this exact word exists.
3. Node metadata exists: this prefix can answer extra questions such as count, sum, top suggestions, or word id.

Think of a trie as trading memory for predictable prefix lookup. A hash set is excellent for exact membership, but it cannot efficiently answer "which stored keys share this prefix?" without scanning or building another index.

## Recognition Cues

Use trie thinking when the prompt contains:

- "starts with"
- "prefix"
- "autocomplete" or "typeahead"
- "dictionary words"
- "replace each word with the shortest root"
- "search word with `.` wildcard"
- "sum values for keys with this prefix"
- "find all words on a board"
- "longest word buildable one character at a time"
- "route prefix", "command prefix", or "URL path segment"

The deeper cue is repeated prefix-constrained work over a reusable dictionary. If the dictionary is built once and queried many times, a trie becomes much more attractive.

## When To Use

Use a trie when:

1. Prefix lookup is a first-class requirement.
2. Many queries reuse the same word set.
3. Early failure matters, such as board DFS pruning in Word Search II.
4. You need prefix-scoped metadata such as counts, sums, or top-k suggestions.
5. You can afford memory proportional to stored prefixes and child representation overhead.

Strong examples:

| Problem shape | Trie value |
|---|---|
| Implement Trie | `insert`, exact `search`, and `startsWith` are direct prefix-walk operations. |
| Word Dictionary | Fixed characters follow one child; wildcard characters branch over children. |
| Replace Words | The first terminal node on a path is the shortest replacement root. |
| Map Sum Pairs | Each prefix node stores an aggregate for all keys below it. |
| Word Search II | Board DFS stops immediately when the current path is not a dictionary prefix. |
| Autocomplete | Prefix traversal narrows candidates before ranking chooses the best suggestions. |

## When Not To Use

Avoid a trie when:

1. You only need exact membership. A hash set is simpler and usually faster.
2. The dataset is tiny. A sorted list or direct scan may be easier to explain and test.
3. Memory is tighter than latency. Tries can store many sparse nodes.
4. Full-text relevance, stemming, typo tolerance, phrase search, or semantic search dominate. Use a search index or retrieval system.
5. Updates are extremely frequent and every prefix node carries expensive metadata.
6. Prefix queries are rare and the dictionary is already sorted. Binary search over the sorted list can find a prefix range with lower memory overhead.

## Concrete Examples

Insert `app`, `apple`, and `bat`.

| Query | Result | Why |
|---|---:|---|
| `startsWith("ap")` | true | The path `a -> p` exists. |
| `search("app")` | true | The `app` node is terminal. |
| `search("appl")` | false | The path exists, but the node is not terminal. |
| `startsWith("ba")` | true | The path `b -> a` exists. |
| `search("ba")` | false | `ba` is only a prefix of `bat`. |
| `search("cat")` | false | The root has no `c` child. |

The exact-search bug is usually returning true just because a path exists. Exact search must check the terminal marker.

## Trie Node Design

Start by stating the node contract before discussing operations.

| Field | Purpose | When required |
|---|---|---|
| `children` | Maps next symbol to child node. | Always. |
| `is_word` or `terminal` | Marks that the current prefix is a stored key. | Exact word lookup. |
| `word` or `word_id` | Emits a result without rebuilding the string. | Board search, dictionary output. |
| `count` | Counts words passing through or ending at a node. | Duplicate handling, delete, prefix count. |
| `sum` | Stores aggregate value for subtree keys. | Map Sum style prefix aggregates. |
| `top_k` | Stores bounded ranked suggestions. | Read-heavy autocomplete. |
| `parent` | Enables upward cleanup. | Delete with node pruning. |

Child representation choices:

| Representation | Best for | Trade-off |
|---|---|---|
| Fixed array of 26 | Lowercase English letters with tight latency needs. | Fast indexing but wastes memory and assumes alphabet. |
| Hash map | Sparse or larger alphabets. | Flexible but higher per-entry overhead. |
| Sorted vector/list | Mostly static dictionaries and compact storage. | Lower memory, slower child lookup unless binary searched. |
| Segment edge label | Compressed trie or radix tree. | Fewer nodes, more complex matching logic. |

Clarify alphabet and normalization early: lowercase only, ASCII, Unicode, case folding, spaces, punctuation, and tokenization all affect node design.

## Core Operations And Complexities

Let:

- `L` = length of the input word or prefix.
- `T` = total stored characters after shared prefixes.
- `A` = alphabet size.
- `B` = effective branching factor during wildcard or DFS search.
- `K` = number of suggestions returned.

| Operation | Basic time | Space impact | Notes |
|---|---:|---:|---|
| Insert word | `O(L)` | Up to `O(L)` new nodes | Existing prefixes are reused. |
| Exact search | `O(L)` | `O(1)` extra | Requires final terminal marker. |
| Prefix search | `O(L)` | `O(1)` extra | Only requires path existence. |
| Delete word | `O(L)` | May free up to `O(L)` nodes | Needs terminal clear and optional pruning. |
| Prefix count | `O(L)` query | Extra counter per node | Updates must maintain counts on insert/delete. |
| Prefix sum | `O(L)` query | Extra sum per node and key-value map | Overwrites need delta, not blind addition. |
| Wildcard search | Worst-case `O(B^L)` | Recursion depth `O(L)` | Fixed chars are linear; wildcards branch. |
| Autocomplete top-k | `O(L + K)` with cached top-k | Extra bounded list per prefix | Writes become more expensive. |
| Board search with trie | `O(mn * 4^L + T)` worst case | Trie plus DFS stack | Trie pruning usually cuts the practical search space. |

Memory is often the real interview trade-off. A trie is not simply `O(number of words)`. It is closer to "number of distinct prefix nodes times child overhead, plus metadata."

## Compressed Trie / Radix Tree Trade-Offs

A compressed trie, often called a radix tree when edges store string segments, merges chains of single-child nodes.

Example:

```text
Uncompressed: root -> c -> o -> m -> p -> a -> c -> t
Compressed:   root -> "compact"
```

Use compression when:

1. Many keys share long runs with no branching.
2. Memory overhead from one node per character is too high.
3. The dictionary is large and mostly static.
4. URL routes, file paths, IP prefixes, or command names have long common segments.

Trade-offs:

| Choice | Benefit | Cost |
|---|---|---|
| Basic trie | Simple insert/search and easy interview implementation. | More nodes and pointer overhead. |
| Compressed trie | Lower memory and fewer pointer hops. | Harder insert/delete because edges may split. |
| Radix over tokens | Natural for paths, routes, or words. | Must define tokenizer and matching semantics. |
| Suffix trie/tree | Supports substring queries. | Much more memory and complexity; rarely the first choice in coding interviews. |

In an interview, mention compressed tries as a scale follow-up, not as the default implementation unless the prompt is explicitly about memory or routing.

## Autocomplete And System Design Transfer

A trie gets you to the prefix node. It does not solve ranking.

Production autocomplete usually needs these separate responsibilities:

1. Prefix index: trie, sorted-term range, or search index prefix field.
2. Candidate ranking: frequency, recency, personalization, geography, business rules, and safety filters.
3. Freshness path: batch rebuilds, incremental updates, or streaming counters.
4. Memory bounds: cap `top_k` lists, cache hot prefixes, and avoid unbounded candidates at every node.
5. Abuse controls: block spam, offensive terms, low-quality injections, and bot-amplified suggestions.
6. Metrics: latency, zero-result rate, suggestion selection rate, CTR, freshness lag, and prefix miss rate.

Read-heavy typeahead often stores a bounded top-k list at each prefix node:

| Workload | Good design | Why |
|---|---|---|
| Many reads, few writes | Precompute top-k suggestions per prefix. | Query is fast after walking the prefix. |
| Many writes, fewer reads | Walk prefix then rank lazily. | Avoids updating many cached lists per write. |
| Very large corpus | Use trie only for hot prefixes or route to search infrastructure. | Keeps memory and rebuild costs bounded. |
| Multi-region autocomplete | Replicate read indexes and stream updates asynchronously. | Low latency matters more than perfect global freshness. |

System design phrasing: "The trie is the candidate-narrowing layer. Ranking, freshness, safety, and observability are separate services or metadata paths."

## Failure Modes

| Failure mode | Symptom | Prevention |
|---|---|---|
| Prefix equals word confusion | `search("app")` returns true after only `apple` is inserted. | Require terminal marker for exact search. |
| Missing terminal marker | Inserted words cannot be found exactly. | Set terminal only after consuming the full key. |
| Blind alphabet assumption | Uppercase, spaces, punctuation, or Unicode break indexing. | Clarify normalization and child representation. |
| Duplicate inserts | Counts, sums, or suggestions inflate incorrectly. | Define duplicate semantics and store current values if needed. |
| Prefix sum overwrite bug | Map Sum returns too large a value. | Apply `new_value - old_value` delta along the path. |
| Wildcard explosion | Dot-heavy patterns time out. | Bound pattern length, branch count, and recursion depth. |
| Board search duplicates | Same word appears multiple times in output. | Use a result set or clear terminal word after first emit. |
| Unbounded autocomplete metadata | Memory grows faster than dictionary size. | Store capped top-k lists and externalize full ranking. |
| Stale suggestions | Deleted or demoted terms still appear. | Track freshness and rebuild or stream updates. |
| Overfitted trie answer | Candidate ignores simpler sorted-array or hash-set solution. | Match data structure to query shape and constraints. |

## Common Pitfalls

1. Saying "trie is `O(1)`" instead of `O(L)`.
2. Using `O(n)` without defining whether `n` is words, characters, or board cells.
3. Forgetting that wildcard search can branch exponentially in the number of wildcards.
4. Rebuilding the trie for every query.
5. Storing full strings at every node when a terminal marker or id is enough.
6. Forgetting that a word can also be a prefix of another word.
7. Not handling empty prefix behavior for `startsWith`.
8. Mixing autocomplete ranking logic into trie traversal until neither is testable.
9. Claiming a trie is a full search engine.
10. Ignoring delete and update semantics when adding metadata.

## Follow-up Questions

Expect follow-ups like:

1. How would you delete a word and remove unused nodes?
2. How do duplicate inserts behave?
3. How would you count words with a prefix?
4. How would you support Unicode or case-insensitive search?
5. When would you use a fixed array instead of a hash map for children?
6. Why is wildcard search not always linear?
7. How do you prevent duplicate words in Word Search II?
8. How would you store top three autocomplete suggestions per prefix?
9. How do you update suggestions when a sentence count changes?
10. When would a compressed trie or radix tree be worth the complexity?
11. How would you shard or cache autocomplete in production?
12. Why not use Elasticsearch or a sorted array instead?

## 60-90 Second Answer

"I use a trie when the core operation is prefix-constrained. Each node represents the prefix on the path from the root. For a basic node I store children and a terminal marker; then I add metadata only if the prompt needs it, such as counts, sums, word ids, or top suggestions.

Insert, exact search, and prefix search are `O(L)` for word length `L`, but memory is proportional to stored prefix nodes and child overhead. Exact search must check the terminal marker, while `startsWith` only checks that the path exists.

For wildcard search, fixed characters follow one child and wildcard characters branch, so the worst case can grow beyond linear. For autocomplete, the trie narrows candidates quickly, but ranking, freshness, abuse controls, and metrics are separate concerns. If memory is the bottleneck, I would discuss child maps, fixed arrays, capped metadata, or compressed tries."

## Scoring Rubric

| Dimension | Strong signal | Weak signal |
|---|---|---|
| Recognition | Ties trie to repeated prefix operations. | Says "tree" or "hash map" without prefix reasoning. |
| Node contract | Defines children, terminal marker, and optional metadata. | Starts coding without state definition. |
| Semantics | Separates exact word, prefix, wildcard, aggregate, and autocomplete behavior. | Treats all trie queries as the same. |
| Complexity | Uses `L`, total characters, branching factor, board cells, and metadata cost. | Claims constant time or vague `O(n)`. |
| Edge cases | Covers prefix-as-word, duplicates, empty prefix, missing child, overwrite, and dedupe. | Only handles happy path. |
| Trade-offs | Discusses child representation, compression, sorted arrays, hash sets, and search indexes. | Presents trie as always best. |
| System transfer | Separates prefix lookup from ranking, freshness, safety, and observability. | Calls trie autocomplete production-ready by itself. |
| Communication | Gives a crisp invariant before implementation. | Explains by code mechanics only. |

## Practice Path And Cross-Links

Work through these in order:

1. [Trie Pattern Pack](../../05-coding-problems/trie/README.md)
2. [Trie Overview](../../05-coding-problems/trie/01-overview.md)
3. [Implement Trie / Prefix Tree](../../05-coding-problems/trie/02-implement-trie-prefix-tree.md)
4. [Word Dictionary Wildcard Search](../../05-coding-problems/trie/03-word-dictionary-wildcard-search.md)
5. [Replace Words](../../05-coding-problems/trie/04-replace-words.md)
6. [Map Sum Pairs](../../05-coding-problems/trie/05-map-sum-pairs.md)
7. [Word Search II](../../05-coding-problems/trie/06-word-search-ii.md)
8. [Design Search Autocomplete System](../../05-coding-problems/trie/07-design-search-autocomplete-system.md)
9. [Longest Word in Dictionary](../../05-coding-problems/trie/08-longest-word-in-dictionary.md)

Reinforce with:

- [Trie Quiz](../../quizzes/trie-quiz.md)
- [Trie Quiz Answers](../../quizzes/answers/trie-answers.md)
- [Trie Flashcards](../../flashcards/trie.md)
- [Coach Answer: Coding Trie Pack](../../solutions/coding-trie.md)
- [Word Search II Problem Bank](../../05-coding-problems/problem-bank/lc-0212-word-search-ii/README.md)
- [Word Search II Solution Metadata](../../05-coding-problems/problem-bank/lc-0212-word-search-ii/solutions.json)
- [Pattern to System Design Map](../../05-coding-problems/PATTERN-SD-MAP.md)
- [Search Systems](../../03-hld-concepts/search-systems/THEORY.md)
- [Elasticsearch](../../03-hld-concepts/elasticsearch/THEORY.md)
