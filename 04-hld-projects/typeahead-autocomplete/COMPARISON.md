# Comparison: Typeahead Autocomplete

| Feature | v1 (Basic) | v2 (Scaled) | v3 (Distributed) |
|---|---|---|---|
| Strategy | In-memory Trie | Trie with Top-K cached at nodes | Sharded Trie across nodes |
| Build Process | Online | Online with Decay | Offline Snapshot Swap |
| Scale | Small | Medium | Large |
