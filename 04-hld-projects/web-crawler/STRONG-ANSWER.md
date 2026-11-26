# Web Crawler — Strong Answer Outline (Time-Boxed)

## 0-5 min: Requirements
- Clarify seed URLs, scope rules, crawl depth, recrawl freshness, robots, politeness, and whether JavaScript rendering is required.
- State that search ranking/index serving is out of scope; this design produces fetched content, metadata, and link graph outputs.
- Make politeness and robots compliance explicit correctness requirements.

Say: "I will treat robots and host politeness as correctness constraints, then optimize the frontier for freshness without overloading any one host."

## 5-10 min: Estimation
- Use a corpus like 2B tracked URLs and 5% daily recrawl to justify a persistent frontier and separate metadata/content storage.
- Use 50K fetches/s peak to motivate host-aware sharding, token-bucket budgets, and backpressure.

## 10-20 min: API + data model
- Present crawl-job create/pause/resume/status/error APIs and operator frontier-lag APIs.
- Model `crawl_job`, `frontier_item`, `visited_url`, `host_budget`, and content object pointers.
- Explain URL normalization, content fingerprints, and partitioning by due time plus host hash.

## 20-35 min: Architecture
- Walk the crawl path: API seeds jobs, frontier manager schedules URLs, host rate limiter grants fetch tokens, fetchers write content pointers, parsers extract links, and dedupe feeds the frontier.
- Separate normal fetch queue from expensive render queue.
- Describe status reads from job metadata, frontier lag, host errors, and freshness metrics.

## 35-42 min: Deep dives
- Deep dive host-aware frontier scheduling and starvation avoidance.
- Explain robots fail-closed behavior, token buckets, retry classification, and lease expiry after fetcher crashes.
- Discuss URL/content dedupe and adaptive recrawl scoring.

## 42-45 min: Wrap-up
- Restate durable frontier, host politeness, URL/content dedupe, metadata/content split, and render-only-when-needed strategy.
- Mention extensions: focused crawling, ML relevance scoring, and compliance policy hooks.

Say: "The crawler scales because scheduling, fetching, parsing, and storage are separated, and it remains safe because host budgets and robots checks gate every fetch."
