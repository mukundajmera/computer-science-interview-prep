# Elasticsearch

**Deep dive**: See [Search Systems](../search-systems/THEORY.md) for canonical theory.

## What is it?
Elasticsearch is a distributed search and analytics engine optimized for full-text retrieval, filtering, and aggregations on document data.

## Code and Tests
This directory (`elasticsearch/`) is the canonical location for implementation examples and tests.

## 📊 Diagrams

- [Indexing write path](./diagrams/indexing-write-path.mmd): how a document write is routed to its primary shard, buffered and appended to the translog for durability, made searchable by the periodic refresh, and acknowledged after replica quorum.
- [Search scatter-gather](./diagrams/search-scatter-gather.mmd): how the coordinating node broadcasts a query to all shards and merges each shard's top hits into one ranked result set across the query and fetch phases.
