# Approach for Social Post Search

## Overview and Core Strategy
The Social Post Search system aims to provide near real-time, highly relevant search results over a massive, constantly updating corpus of user-generated content. The primary challenge is balancing extreme write throughput with the low-latency requirements of complex text search queries.

Our approach relies on an in-memory `InvertedIndex` for search execution. We do not attempt to perform full-text search directly on a relational database.

## Supported Versions
- **v1-basic**: An in-memory baseline.
- **v2-extended**: Adds abstraction boundaries and richer query flows.
- **v3-optimized**: Implements distributed-friendly interfaces, query planning, and idempotency hooks with explicit BM25 search ranking.

## Inverted Index
The core of our approach is the `InvertedIndex`. Unlike a standard database index that maps a row ID to a string, our inverted index tokenizes a string into individual words (terms) and maps each term to a list of Document IDs (posts) that contain it, while also maintaining tracking metadata like `docLengths` and `termFreqs`.
- To handle scale, this index can be conceptually sharded by Document ID. The query planner maps query terms to their respective posting sets to find local matches and returns the relevant subset. The ranking service then evaluates this subset.

## Near Real-Time Index Updates
A social search engine must reflect new posts almost instantly. 
- When a user posts, `PostIngestionService` commits the record, with v3 applying idempotency using an `idempotencyKey` ensuring duplicate submissions within a short TTL are ignored.
- Indexer workers tokenize the text using `Tokenizer.tokenize`, explicitly removing common stopwords (e.g., `a`, `an`, `the`, `and`). Empty tokens and missing terms are ignored.
- Document deletes update the metadata correctly by removing the document from the term index and updating the total document count and term frequencies.

## Relevance and Query Grammar (BM25)
Retrieving matching documents is only half the battle; ranking them is harder. We implement a deterministic BM25 scoring algorithm in `SearchRankingService`.
- **Query Grammar**: `QueryPlanner` strictly evaluates AND/OR queries. It parses terms into conjunction groups separated by OR, ensuring that intersection logic is correctly applied before final union.
- **Relevance Scoring**: Relevance isn't arbitrarily assigned based on vague social signals. We calculate exact BM25 scores using localized Term Frequency (`tf`), Inverse Document Frequency (`idf`), and normalize against the global average document length (`avgdl`).
- Ties are broken deterministically by sorting on the Post ID lexicographically.
