# Strong Answer: Typeahead Autocomplete

A strong answer starts by sizing the problem to justify a custom in-memory data structure (Trie) over a relational DB. It moves to optimize reads by pre-computing top-K results at each node. Finally, it addresses scale by sharding the trie (e.g., by consistent hashing or prefix routing) and decoupling reads from writes using an offline build-and-swap pipeline.
