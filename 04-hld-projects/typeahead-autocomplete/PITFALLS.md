# Pitfalls: Typeahead Autocomplete

- **Memory Exhaustion**: Storing the full word at every node for top-k caching can blow up memory.
- **Hot Partitions**: Sharding blindly by first character leads to skewed data distribution.
- **Real-time updates**: Updating the trie synchronously on every query will bottleneck reads.
