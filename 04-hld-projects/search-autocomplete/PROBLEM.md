# Search Autocomplete - Problem Statement

## 1. Core User Value
Provide a system that suggests search queries as the user types, returning the top-k most relevant and popular suggestions in real-time to reduce typing effort and improve search discovery.

## 2. Functional Requirements
- Return top-5 suggestions matching a prefix in real time as the user types.
- Real-time response (<50ms P99) end-to-end latency.
- Rank suggestions by historical query frequency/popularity.
- Case-insensitive matching (lowercase English characters `[a-z]`).
- Blacklist/profanity filter to drop inappropriate suggestions.
- Offline frequency updates to recompute frequencies and rebuild Trie.

## 3. Non-Functional Requirements
- High availability (99.99%; stale suggestions preferred over outages).
- Low latency.
- Fault tolerance.
- Scalability: 5 Billion searches/day.

## 4. Sizing Math
- **Traffic**: 5 Billion searches/day = ~60,000 QPS average, ~120,000 peak QPS.
- **Storage**: Query length avg 20 chars. Total Trie storage ~100 GB.
