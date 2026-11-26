# Social Post Search - Follow-Up Questions

## Follow-up questions
1. How would `PostIngestionService` make repeated post-ingestion requests idempotent?
2. What token normalization belongs before writing to `InvertedIndex`?
3. How should `QueryPlanner` combine candidates for multi-keyword searches?
4. What deterministic tie-breaker should `SearchRankingService` use?
5. How do you remove stale index entries when a post is deleted or edited?

## Variants and extensions
1. Hashtag and author filters.
2. Time-decay ranking.
3. Prefix or autocomplete search.
4. External search-store gateway behind the same interfaces.

## Interviewer probes to prepare
- "Why is an inverted index better than scanning posts?"
- "Which service owns ranking versus candidate retrieval?"
- "What changes when index writes become asynchronous?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
