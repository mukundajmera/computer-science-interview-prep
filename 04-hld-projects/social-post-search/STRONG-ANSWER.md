
# Social Post Search System - Strong Answer

## 0-5 min: Requirements

Say: "I will treat the post database as the source of truth and the search index as a derived, eventually consistent read model."

- Support keyword search over public or viewer-authorized posts, freshness targets, pagination, filters, and basic ranking.
- Non-goals: private-message search, ads ranking, and full social graph recommendation.
- Correctness boundary: privacy filtering must be enforced even when ranking or freshness degrades.

## 5-10 min: Scale and Constraints

Say: "Search reads dominate, but post writes must stay fast even if the search index is unhealthy."

- Plan for around 20K average search QPS and 150K peak QPS.
- Use an explicit freshness SLO and return `freshnessLagMs` in responses.
- Degrade by disabling expensive ranking or using cached results, never by bypassing privacy filters.

## 10-20 min: API and Data Model

Say: "The API should expose what is stale or degraded so clients and operators can reason about result quality."

- `GET /search/posts?q=...&cursor=...&filters=...` returns results, next cursor, rank version, and freshness lag.
- Post creation writes canonical post rows plus an outbox event in the same transaction.
- Search documents include post id, author id, visibility fields, normalized text, language, timestamp, and ranking features.
- Index aliases separate read traffic from backfill and analyzer migrations.

## 20-35 min: Architecture

Say: "Writes flow through the canonical post service; indexers consume outbox events and build searchable documents asynchronously."

- API Gateway handles auth, abuse limits, and query budget checks.
- Search API rewrites queries, fetches candidates from Elasticsearch or a similar inverted index, filters visibility, and applies ranking.
- Indexer pipeline consumes post events, enriches documents, writes to versioned indexes, and records lag by partition.
- Recent-post side index handles freshness for hot events while the main index refreshes normally.

## 35-42 min: Deep Dives

Say: "The riskiest changes are analyzer and ranking changes, so I would roll them with dual-write, shadow-read, and alias rollback."

- Freshness: track committed-to-indexed latency and alert before the SLO is breached.
- Privacy: fail closed on unavailable visibility metadata; never return unverified private posts.
- Reindexing: build a new index version, dual-write mutations, compare shadow-read overlap, then switch the alias.
- Failure: if indexers lag, search still serves older results with explicit lag; post writes continue.

## 42-45 min: Wrap-up

Say: "I chose asynchronous indexing because it protects write latency and lets search evolve independently, with visible freshness and privacy guardrails."

- Trade-off: users may not see brand-new posts immediately, but the system avoids coupling posting success to search health.
- Next evolution: personalized ranking, per-language analyzers, and query-class-specific caches behind kill switches.
