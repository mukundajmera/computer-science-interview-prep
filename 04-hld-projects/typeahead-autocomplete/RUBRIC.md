# Rubric: Typeahead Autocomplete

- **Strong**: Candidate clearly defines the top-k caching mechanism at each trie node and explains the trade-offs of offline vs online trie builds.
- **Weak**: Candidate uses a simple DB query (e.g., `LIKE 'prefix%'`) without understanding why it won't scale for latency requirements.
