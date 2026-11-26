# Social Post Search System - Design

## 1. Requirements and Constraints

Search public and permissioned social posts by keyword with bounded freshness, privacy enforcement, and relevance ranking. The search index is a derived view; the post store remains the source of truth.

| Requirement | Target |
|---|---|
| Corpus | 500M active searchable posts, 5B archived posts |
| Writes | 3K post creates/sec average, 25K/sec peak during events |
| Search reads | 20K queries/sec average, 150K/sec peak |
| Freshness | p95 post searchable within 30 seconds, p99 within 2 minutes |
| Latency | p95 search < 300 ms, p99 < 800 ms |
| Availability | 99.95% search API, graceful degradation when ranking is impaired |

Out of scope: private DM search, ads auction, full recommendation feed, and legal discovery workflows.

## 2. API Contracts

```http
POST /api/v1/posts
Idempotency-Key: <uuid>
{
  "authorId": "u123",
  "text": "distributed search notes",
  "visibility": "PUBLIC|FOLLOWERS|PRIVATE",
  "language": "en",
  "mediaIds": ["m1"],
  "createdAt": "2026-06-14T10:00:00Z"
}
```

Response: `201 Created { "postId": "p789", "indexingStatus": "PENDING" }`.

```http
GET /api/v1/search/posts?q=distributed%20search&viewerId=u456&sort=relevance&cursor=...&limit=20
```

Response: `200 OK { "results": [{ "postId": "p789", "authorId": "u123", "snippet": "...", "score": 8.72, "createdAt": "..." }], "nextCursor": "...", "freshnessLagMs": 18000 }`.

```http
POST /api/v1/search/reindex
{
  "indexVersion": "posts_v7",
  "sourceRange": { "createdAfter": "2026-01-01T00:00:00Z" },
  "dryRun": false
}
```

Admin-only response: `202 Accepted { "jobId": "r42" }`.

## 3. Data Model and Storage

| Store | Key / Index | Contents | Partitioning | Retention |
|---|---|---|---|---|
| Post DB | `post_id` primary key; secondary `author_id, created_at` | canonical text, media refs, visibility, delete/edit version | hash by `post_id`; author timeline by `author_id` | active forever unless deleted; tombstones 90 days |
| Outbox | `event_id` primary key; `post_id, version` unique | `PostCreated`, `PostEdited`, `PostDeleted`, `VisibilityChanged` | hash by `event_id` | 14 days after acknowledged by indexer |
| Search index | inverted terms -> posting lists; document fields by `post_id` | tokenized text, author, created time, language, engagement counters, visibility bits | time-bucketed indices, shard by term/doc hash, replicas by region | hot 90 days, warm 2 years, cold/archive optional |
| Privacy graph cache | `viewer_id` -> followed/blocked author sets | compact allow/deny filters | hash by viewer | minutes; refreshed on graph events |
| Feature store | `post_id` and `author_id` features | likes, replies, trust signals, recency buckets | hash by entity id | rolling 30-180 days |

Deletes and visibility changes publish high-priority index events. Tombstones prevent stale reappearance during replay or reindex.

## 4. Architecture

[Architecture Diagram](./diagrams/architecture.mmd)


Use [Elasticsearch](../../03-hld-concepts/elasticsearch/) or a similar distributed inverted-index engine for retrieval, and [message queues](../../03-hld-concepts/message-queues/) for isolating post writes from index freshness.

## 5. Write Path

1. API gateway authenticates the author and enforces per-user create limits.
2. Post Service validates payload, applies the idempotency key, and writes the post plus an outbox event in one transaction.
3. The outbox publisher emits `PostCreated(postId, version, visibility, language, textHash)` to Kafka.
4. Indexing workers tokenize text, normalize language-specific fields, enrich with initial ranking features, and upsert the document into the active search index.
5. Edits, deletes, and visibility changes carry monotonically increasing versions; workers ignore stale events.

The user-facing create path does not wait for index acknowledgement. It returns `indexingStatus=PENDING`, and the post becomes searchable when the derived index catches up.

## 6. Read Path

1. Query Service parses the query, normalizes tokens, rejects abusive wildcard/regex patterns, and checks query cache for anonymous/public searches.
2. It fans out to relevant search shards and retrieves a candidate set using BM25/text relevance plus strict filters: language, time range, author exclusions, and coarse visibility.
3. Privacy Graph Cache applies viewer-specific filters for followers-only posts, blocks, mutes, takedowns, and author suspensions before results are returned.
4. Ranking combines text score, recency decay, engagement quality, author affinity, and integrity penalties.
5. Cursor pagination encodes the last score, created time, and shard tie-breaker so retries are stable.

If ranking features are slow, return text-relevance plus recency results and mark `rankingMode=DEGRADED`; never bypass privacy filters.

## 7. Failure and Recovery Paths

- **Indexer lag:** expose lag by partition and raise alerts before freshness SLO breach; Search API returns `freshnessLagMs`.
- **Poison events:** retry transient failures with backoff, then send to DLQ with `post_id`, `version`, and analyzer error. DLQ replay is idempotent.
- **Search cluster partial outage:** query replicas in another AZ/region, reduce optional ranking features, and fail closed on uncertain privacy state.
- **Post DB / outbox mismatch:** use transactional outbox scanning to guarantee every committed post mutation has a replayable event.
- **Rebuild:** reindex from Post DB snapshots plus outbox tail into a new index version, compare counts/checksums, then atomically switch alias `posts_current`.
- **Rollback:** switch alias back to the previous index version and pause new analyzer rollout; source-of-truth writes are unaffected.

## 8. Deep Dives

### Inverted Index Freshness

Freshness is eventually consistent by design. Keep a small "recent posts" side index for the last few minutes so hot event posts become searchable quickly while larger shards refresh on normal intervals. Track `post_committed_at -> indexed_at` latency, per-language analyzer failures, and shard refresh time. For celebrity/event spikes, batch by author and term to avoid over-refreshing the same shard.

### Privacy Filters

Index coarse visibility fields but enforce final visibility at query time with graph-derived allow/deny sets. Followers-only results require the viewer to follow the author at query time, not merely when the post was indexed. Blocks, mutes, suspensions, takedowns, and deletes are deny-first filters; if the privacy cache is unavailable or stale beyond its TTL, return only public posts or fail the request.

### Ranking

Rank in two stages: retrieve top N candidates cheaply from the inverted index, then rerank the top few hundred with features. Keep feature freshness looser than privacy correctness; stale engagement counters can affect ordering, but stale visibility cannot leak content. Add per-author and per-language diversity so one viral author or spam cluster does not dominate results.

### Reindexing

Mapping/analyzer changes create a new index version. Dual-write new mutations to old and new indices during backfill, shadow-read a sample of production queries, compare result overlap and latency, then flip the read alias. Keep the old index until rollback risk is low and storage budgets permit deletion.

## 9. Observability, Rollout, and Rollback

Metrics: QPS, p95/p99 latency, zero-result rate, timeout rate, shard CPU, heap pressure, refresh latency, index lag, DLQ depth, privacy-filter drop rate, degraded-ranking rate, and alias version.

Logs and traces include `query_id`, `viewer_id_hash`, `index_version`, shard fanout, ranking mode, and privacy-filter decision counts without logging raw private text.

Roll out analyzers, rankers, and index mappings by percentage of traffic and query class. Keep kill switches for new rankers, side index usage, and query-cache writes. Rollback is alias switch for index versions, config disable for rankers, and event replay for missed mutations.

## 10. Trade-offs and Interview Wrap-up

| Decision | Choice | Alternative | Why |
|---|---|---|---|
| Source of truth | Post DB owns writes; search index is derived | Search index as primary store | Prevents search outages from corrupting canonical posts |
| Freshness | Async indexing with explicit lag SLO | Synchronous index writes | Keeps post creation latency predictable under spikes |
| Privacy | Query-time final filtering | Index-time-only ACL expansion | Handles follows, blocks, and takedowns without reindexing every edge change |
| Relevance | Two-stage ranking | One heavy ML pass on all matches | Balances latency, cost, and ranking quality |

For a 45-minute spoken structure, use [STRONG-ANSWER.md](./STRONG-ANSWER.md): requirements, estimates, API/data model, architecture, deep dives, and wrap-up.

---
**Real-world reference**: See how Twitter solved this in the [Twitter case study](../../case-studies/twitter-timeline/)
