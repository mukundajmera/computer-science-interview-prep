# Private backlog record (221 items)

Status of every work item from the former private curriculum repo, checked against this repo on 2026-11-28. Titles are kept; task prompts are not copied.

## How status was decided

- **done**: every file the item was meant to create exists here. This is a file-presence check, not a quality review.
- **open**: one or more target files are missing. The evidence column names one.
- **dropped**: the item targets a folder that does not exist in this repo, so it no longer applies.
- **AT link**: open items that match a task in [agent-task-backlog.md](agent-task-backlog.md).

## Counts

| Status | Items |
|---|---:|
| done | 199 |
| open | 20 |
| dropped | 2 |
| **Total** | **221** |

## Items

| ID | Title | Category | Pri | Status | Evidence | AT |
|---|---|---|---|---|---|---|
| `T-HLDC-DOC-kafka-zerocopy-internals` | Kafka Architecture Deep-Dive: OS Zero-Copy (sendfile), Page Cache, Compaction, Rebalance, & ISR Dynamics | HLD_CONCEPT | P0 | done | `03-hld-concepts/kafka/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-redis-eventloop-multithread` | Redis Internals: Event Loop vs Multi-Threaded I/O (Redis 6+), CoW Forks, AOF Policies & Cluster Slots | HLD_CONCEPT | P0 | done | `03-hld-concepts/redis/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-postgresql-mvcc-vacuum` | PostgreSQL Deep-Dive: MVCC Heap, Autovacuum Tuning, HOT Optimization, Write Amplification, & PgBouncer | HLD_CONCEPT | P0 | done | `03-hld-concepts/postgresql/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-cassandra-tombstones-repair` | Cassandra Deep-Dive: LSM Write Path, Tombstone Lifecycle, Repair Protocols, & Compaction Strategies | HLD_CONCEPT | P0 | done | `03-hld-concepts/cassandra/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-dynamodb-internals-merge` | DynamoDB Deep-Dive: Physical Partitions, Adaptive Capacity, GSI Lag, & Single-Table Modeling | HLD_CONCEPT | P0 | done | `03-hld-concepts/dynamodb/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-websockets-deep-dive` | WebSockets Architectural Blueprint: Framing, Handshake, Socket Memory Budgeting, & Scale Backplanes | HLD_CONCEPT | P0 | done | `03-hld-concepts/websockets/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-data-partitioning-deep-dive` | Data Partitioning & Resharding: Strategy Trade-offs, Key Salting, CDC Migration, & Split Protocols | HLD_CONCEPT | P0 | done | `03-hld-concepts/data-partitioning/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-resilience-patterns-deep-dive` | Resilience Patterns: Circuit Breaker Sliding Windows, Bulkhead Thread/Semaphore Pools, & Full Jitter Backoff | HLD_CONCEPT | P0 | done | `03-hld-concepts/resilience-patterns/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-caching-xfetch-thundering-herd` | Advanced Caching Patterns: XFetch Probabilistic Early Expiration, Singleflight Mutex, & Cache Catastrophes | HLD_CONCEPT | P0 | done | `03-hld-concepts/caching/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-raft-leaseread-readindex` | Raft Consensus Deep-Dive: Linearizable Reads (ReadIndex vs LeaseRead), Joint Consensus, & Compaction | HLD_CONCEPT | P0 | done | `03-hld-concepts/distributed-consensus-raft/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-lsm-compaction-math` | Storage Engine Compaction Math: WAF, SAF, RAF Formulations for STCS vs LCS & Bloom Filter Sizing | HLD_CONCEPT | P0 | done | `03-hld-concepts/storage-engine-internals/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-cap-pacelc-clarification` | CAP & PACELC Theorems Clarification: Network Partitions, CA Myth, & Real-World System Mappings | HLD_CONCEPT | P1 | done | `03-hld-concepts/cap-theorem/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-database-isolation-levels` | Database Isolation Levels: Berenson Taxonomy, Snapshot Isolation, Write Skew, & SSI | HLD_CONCEPT | P0 | done | `03-hld-concepts/database-isolation-levels/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-distributed-rate-limiting-batching` | Distributed Rate Limiting at Scale: Token Reservation, Local Batching, & Redis Network Protection | HLD_CONCEPT | P1 | done | `03-hld-concepts/distributed-rate-limiting-scale/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-logical-clocks-truetime` | Logical Clocks & Google TrueTime: Lamport, Vector Clocks, Bounded Uncertainty, & Commit Wait | HLD_CONCEPT | P0 | done | `03-hld-concepts/logical-clocks-truetime/THEORY.md` (+1 more files) |  |
| `T-HLDC-DOC-sql-nosql-taxonomy-unification` | SQL vs NoSQL Architectural Taxonomy: Unifying Data Models, Query Patterns, & Storage Trade-offs | HLD_CONCEPT | P1 | done | `03-hld-concepts/sql-vs-nosql/THEORY.md` (+2 more files) |  |
| `T-HLDC-DIAG-concept-diagram-suite` | Author Complete Mermaid Diagram Suite for 51 Concepts Lacking Visual Architecture | HLD_CONCEPT | P1 | done | `03-hld-concepts/kafka/diagrams/zero-copy-architecture.mmd` (+6 more files) |  |
| `T-HLDC-CODE-fix-failing-python-tests` | Fix Failing Python Tests in CDN, Consistent Hashing, Live Resharding, & Microservice Security | HLD_CONCEPT | P0 | done | `03-hld-concepts/cdn/python/tests/test_cdn.py` (+3 more files) |  |
| `T-HLDC-CODE-fix-java-demo-collisions` | Resolve Java Package Collisions for Demo Classes Across 7 Concept Directories | HLD_CONCEPT | P0 | done | `03-hld-concepts/caching/java/` (+6 more files) |  |
| `T-HLDC-CODE-caching-xfetch-singleflight` | Implement Executable Java & Python Demos for XFetch Probabilistic Cache & Singleflight Mutex | HLD_CONCEPT | P0 | open | Missing 2 of 4 files, e.g. `03-hld-concepts/caching/python/v3-production/xfetch_cache.py` |  |
| `T-HLDC-CODE-implement-missing-concept-code` | Implement Dual-Language Code and Tests for Pattern Selection, Sharding Resharding, & Rate Limiting | HLD_CONCEPT | P1 | open | Missing 2 of 4 files, e.g. `03-hld-concepts/pattern-selection/python/tests/test_pattern_evaluator.py` |  |
| `T-HLDC-CASE-stripe-ledger-engine` | Author Stripe Ledger Engine Case Study: Double-Entry Bookkeeping, Idempotency, & Strict Linearizability | HLD_CONCEPT | P0 | open | Missing 1 of 2 files, e.g. `case-studies/stripe-ledger-engine/diagrams/architecture.mmd` |  |
| `T-HLDC-CASE-discord-cassandra-scylladb` | Author Discord Case Study: Trillion-Message Scale & Migration from Cassandra to ScyllaDB | HLD_CONCEPT | P0 | open | Missing 2 of 2 files, e.g. `case-studies/discord-cassandra-scylladb/README.md` | AT-017 |
| `T-HLDC-CASE-google-spanner-truetime` | Author Google Spanner & TrueTime Case Study: Planet-Scale External Consistency & 2PC Paxos | HLD_CONCEPT | P0 | done | `case-studies/google-spanner-truetime/README.md` (+1 more files) |  |
| `T-HLDC-CASE-meta-memcached-tao` | Author Meta Memcached & TAO Case Study: Scaling at 100M+ QPS, Lease Tokens, & Graph Invalidation | HLD_CONCEPT | P0 | open | Missing 2 of 2 files, e.g. `case-studies/meta-memcached-tao/README.md` | AT-018 |
| `T-HLDC-CASE-shopify-flash-sale` | Author Shopify Flash-Sale Case Study: BFCM Pod Architecture, Virtual Waiting Rooms, & Redis Lua Lockup | HLD_CONCEPT | P0 | open | Missing 2 of 2 files, e.g. `case-studies/shopify-flash-sale/README.md` | AT-019 |
| `T-HLDC-CASE-snowflake-data-warehouse` | Author Snowflake Cloud Data Warehouse Case Study: Disaggregated Storage/Compute & Micro-Partitions | HLD_CONCEPT | P0 | open | Missing 2 of 2 files, e.g. `case-studies/snowflake-data-warehouse/README.md` |  |
| `T-HLDC-DOC-chatgpt-copilot-expansion` | Expand ChatGPT & GitHub Copilot Case Studies to Comprehensive 400+ Line Standard | HLD_CONCEPT | P1 | done | `case-studies/chatgpt-inference/README.md` (+1 more files) |  |
| `T-HLDC-CLEANUP-orphan-directories` | Consolidate Orphan & Duplicate Concept Directories and Synchronize Root Indices | HLD_CONCEPT | P1 | dropped | Targets orphan folders that do not exist in the public repo (fresh history). |  |
| `T-GENAI-DOC-multi-agent-orchestrator` | Author Complete Markdown Documentation Suite for Multi-Agent Orchestrator LLD | GENAI | P0 | done | `06-genai-systems/01-llm-lld-projects/multi-agent-orchestrator/PROBLEM.md` (+6 more files) |  |
| `T-GENAI-DOC-speculative-decoding-cache` | Author Complete Markdown Documentation Suite for Speculative Decoding Verifier LLD | GENAI | P0 | done | `06-genai-systems/01-llm-lld-projects/speculative-decoding-cache/PROBLEM.md` (+6 more files) |  |
| `T-GENAI-DOC-streaming-token-aggregator` | Author Complete Markdown Documentation Suite for Streaming Token Aggregator LLD | GENAI | P0 | done | `06-genai-systems/01-llm-lld-projects/streaming-token-aggregator/PROBLEM.md` (+6 more files) |  |
| `T-GENAI-DOC-vector-store-inverted-index` | Author Complete Markdown Documentation Suite for Vector Store & Inverted Index LLD | GENAI | P0 | done | `06-genai-systems/01-llm-lld-projects/vector-store-inverted-index/PROBLEM.md` (+6 more files) |  |
| `T-GENAI-FIX-math-kv-cache-pagedattention` | Fix KV-Cache Math Derivations, GQA vs MHA Multipliers, and PagedAttention Block Allocation | GENAI | P0 | done | `06-genai-systems/00-concepts/streaming-kv-cache/README.md` (+2 more files) |  |
| `T-GENAI-EXPAND-llm-inference-serving-engine` | Deepen LLM Inference Serving Engine HLD with Ground-Level Math and Python Reference Implementation | GENAI | P0 | done | `06-genai-systems/02-llm-hld-projects/llm-inference-serving-engine/python/v1-basic/__init__.py` (+4 more files) |  |
| `T-GENAI-CONCEPT-rope-positional-encoding` | Add Comprehensive Concept Deep Dive on Rotary Position Embedding (RoPE) and Context Scaling | GENAI | P0 | done | `06-genai-systems/00-concepts/rope-positional-embedding/README.md` |  |
| `T-GENAI-CONCEPT-attention-variants-gqa-mqa` | Add Core Concept Deep Dive on Attention Variants: MHA vs MQA vs GQA and Memory Bandwidth Arithmetic | GENAI | P0 | open | Missing 1 of 1 files, e.g. `06-genai-systems/00-concepts/attention-mechanisms/README.md` | AT-020 |
| `T-GENAI-CONCEPT-hybrid-search-reranking` | Fix and Expand RAG Hybrid Search (BM25 + Dense) Fusion and Cross-Encoder Reranking in RAG Concepts | GENAI | P0 | done | `06-genai-systems/00-concepts/rag-architecture/README.md` |  |
| `T-GENAI-PROJECT-semantic-embedding-cache` | Implement Semantic Embedding Cache LLD Project (Code, Tests, and Architecture Docs) | GENAI | P0 | open | Missing 1 of 10 files, e.g. `06-genai-systems/01-llm-lld-projects/semantic-embedding-cache/python/v1-basic/__init__.py` | AT-024 (v2 follow-up only) |
| `T-GENAI-PROJECT-context-window-manager` | Implement Context Window Manager LLD Project (Priority Compaction & Token Budgeting) | GENAI | P0 | done | `06-genai-systems/01-llm-lld-projects/context-window-manager/PROBLEM.md` (+9 more files) |  |
| `T-GENAI-PROJECT-token-streaming-server` | Implement Token Streaming Server LLD Project (Async SSE / WebSocket with Backpressure) | GENAI | P0 | done | `06-genai-systems/01-llm-lld-projects/token-streaming-server/PROBLEM.md` (+9 more files) |  |
| `T-GENAI-PROJECT-ai-safety-guardrails` | Implement Multi-Tier AI Safety Guardrails LLD Project (Input/Output Safety & PII Redaction) | GENAI | P0 | done | `06-genai-systems/01-llm-lld-projects/ai-safety-guardrails/PROBLEM.md` (+9 more files) |  |
| `T-GENAI-PROJECT-multi-tenant-enterprise-rag` | Design Multi-Tenant Enterprise RAG HLD (Document Security, ACL Filtering & Hybrid Search) | GENAI | P0 | done | `06-genai-systems/02-llm-hld-projects/multi-tenant-enterprise-rag/PROBLEM.md` (+11 more files) |  |
| `T-GENAI-CONCEPT-lora-peft-derivation` | Add Deep Dive on Parameter-Efficient Fine-Tuning (PEFT), LoRA Rank Derivation, and Serving Multiplexing | GENAI | P1 | done | `06-genai-systems/00-concepts/model-adaptation-lora/README.md` |  |
| `T-GENAI-CONCEPT-dpo-preference-optimization` | Add Core Concept Deep Dive on Alignment: RLHF, PPO, and Direct Preference Optimization (DPO) Formulation | GENAI | P1 | open | Missing 1 of 1 files, e.g. `06-genai-systems/00-concepts/alignment-dpo-rlhf/README.md` | AT-021 |
| `T-GENAI-PROJECT-llm-eval-benchmark-platform` | Design LLM Evaluation & Benchmark Platform HLD and Consolidate Duplicate Eval Projects | GENAI | P1 | done | `06-genai-systems/02-llm-hld-projects/llm-eval-benchmark-platform/PROBLEM.md` (+5 more files) |  |
| `T-GENAI-FIX-copilot-latency-caching` | Fix Unrealistic Debounce Latency and Remote Caching Anti-Pattern in AI Coding Copilot HLD | GENAI | P1 | done | `06-genai-systems/02-llm-hld-projects/ai-coding-copilot/DESIGN.md` (+2 more files) |  |
| `T-GENAI-FIX-semantic-retrieval-memory-acl` | Enrich Semantic Retrieval Platform HLD with Vector Memory Quantization and In-Engine ACL Filtering | GENAI | P1 | done | `06-genai-systems/02-llm-hld-projects/semantic-retrieval-platform/DESIGN.md` (+1 more files) |  |
| `T-GENAI-INFRA-pytest-collection-fix` | Fix Pytest Module Collection Namespace Collisions and Synchronize Curriculum Matrix | GENAI | P1 | open | Missing 1 of 1 files, e.g. `06-genai-systems/conftest.py` |  |
| `T-HLD-CLEAN-proximity-service-ghost` | Clean Ghost proximity-service Directory and Restore Inventory Invariant | HLD | P0 | dropped | Targets a ghost folder that is absent from the public repo. |  |
| `T-HLD-FIX-quick-commerce-delivery-java` | Implement Stub Methods in Quick Commerce Delivery Java Simulation Suite | HLD | P0 | done | `04-hld-projects/quick-commerce-delivery/java` |  |
| `T-HLD-FIX-ecommerce-backend-java` | Fix 45 Compilation Errors in E-Commerce Backend Java Implementation | HLD | P0 | done | `04-hld-projects/ecommerce-backend/java` |  |
| `T-HLD-FIX-video-streaming-java` | Fix Compilation Error in Video Streaming Java CachedVideoService | HLD | P0 | done | `04-hld-projects/video-streaming/java` |  |
| `T-HLD-CODE-kafka-distributed-broker` | Implement Dual-Language Simulation Engine for Kafka Distributed Broker | HLD | P0 | open | Missing 8 of 8 files, e.g. `04-hld-projects/kafka-distributed-broker/java/v1-basic/PartitionLog.java` |  |
| `T-HLD-CODE-distributed-cloud-storage-s3` | Implement Dual-Language Simulation Engine for Distributed Cloud Storage S3 | HLD | P0 | done | `04-hld-projects/distributed-cloud-storage-s3/diagrams/architecture.mmd` (+7 more files) |  |
| `T-HLD-DOC-collaborative-doc-editor` | Deep Technical Expansion of Collaborative Doc Editor DESIGN.md | HLD | P0 | done | `04-hld-projects/collaborative-doc-editor/DESIGN.md` |  |
| `T-HLD-DOC-ride-sharing` | Deep Technical Expansion of Ride Sharing DESIGN.md | HLD | P0 | done | `04-hld-projects/ride-sharing/DESIGN.md` |  |
| `T-HLD-DOC-distributed-cache` | Deep Technical Expansion of Distributed Cache DESIGN.md | HLD | P0 | done | `04-hld-projects/distributed-cache/DESIGN.md` |  |
| `T-HLD-DOC-brokerage-platform` | Deep Technical Expansion of Brokerage Platform DESIGN.md | HLD | P0 | done | `04-hld-projects/brokerage-platform/DESIGN.md` |  |
| `T-HLD-DOC-web-crawler` | Deep Technical Expansion of Web Crawler DESIGN.md | HLD | P0 | done | `04-hld-projects/web-crawler/DESIGN.md` |  |
| `T-HLD-DOC-video-recommendations` | Deep Technical Expansion of Video Recommendations DESIGN.md | HLD | P0 | done | `04-hld-projects/video-recommendations/DESIGN.md` |  |
| `T-HLD-DOC-ad-click-aggregator` | Deep Technical Expansion of Ad Click Aggregator DESIGN.md | HLD | P1 | done | `04-hld-projects/ad-click-aggregator/DESIGN.md` |  |
| `T-HLD-DOC-metrics-monitoring` | Deep Technical Expansion of Metrics Monitoring DESIGN.md | HLD | P1 | done | `04-hld-projects/metrics-monitoring/DESIGN.md` |  |
| `T-HLD-DOC-job-scheduler` | Deep Technical Expansion of Distributed Job Scheduler DESIGN.md | HLD | P1 | done | `04-hld-projects/job-scheduler/DESIGN.md` |  |
| `T-HLD-DOC-content-moderation` | Deep Technical Expansion of Content Moderation DESIGN.md | HLD | P1 | done | `04-hld-projects/content-moderation/DESIGN.md` |  |
| `T-HLD-DOC-ticketing-platform` | Deep Technical Expansion of Ticketing Platform DESIGN.md | HLD | P1 | done | `04-hld-projects/ticketing-platform/DESIGN.md` |  |
| `T-HLD-DOC-quick-commerce-delivery` | Deep Technical Expansion of Quick Commerce Delivery DESIGN.md | HLD | P1 | done | `04-hld-projects/quick-commerce-delivery/DESIGN.md` |  |
| `T-HLD-DOC-bot-detection` | Deep Technical Expansion of Bot Detection DESIGN.md | HLD | P1 | done | `04-hld-projects/bot-detection/DESIGN.md` |  |
| `T-HLD-MATH-search-autocomplete` | Reconcile Capacity Math and Trie Sizing in Search Autocomplete | HLD | P1 | done | `04-hld-projects/search-autocomplete/PROBLEM.md` (+1 more files) |  |
| `T-HLD-MATH-digital-wallet` | Fix Unrealistic 1M TPS Scale and Correct TCC Double-Credit Protocol Flaw in Digital Wallet | HLD | P1 | done | `04-hld-projects/digital-wallet/PROBLEM.md` (+1 more files) |  |
| `T-HLD-MATH-stock-exchange-matching-engine` | Correct L3 Cache Memory Claim and Document Ring Buffer Memory Model in Stock Exchange | HLD | P1 | done | `04-hld-projects/stock-exchange-matching-engine/DESIGN.md` (+1 more files) |  |
| `T-HLD-MATH-realtime-gaming-leaderboard` | Fix Redis Memory Undercount and Detail Floating-Point Composite Score Encoding in Leaderboard | HLD | P1 | done | `04-hld-projects/realtime-gaming-leaderboard/DESIGN.md` |  |
| `T-HLD-MATH-distributed-email-service` | Reconcile Ingress vs Egress Traffic Profile in Distributed Email Service | HLD | P1 | done | `04-hld-projects/distributed-email-service/PROBLEM.md` (+1 more files) |  |
| `T-HLD-MATH-video-streaming` | Add Full Capacity Planning, Transcoding Storage, and CDN Egress Math to Video Streaming | HLD | P1 | done | `04-hld-projects/video-streaming/DESIGN.md` |  |
| `T-HLD-MATH-url-shortener` | Document Multiplier Rationale for Storage Capacity in URL Shortener | HLD | P2 | done | `04-hld-projects/url-shortener/DESIGN.md` |  |
| `T-HLD-DIAG-migrate-inline-diagrams` | Extract Inline Mermaid Diagrams to External mmd Files Across 7 Projects | HLD | P1 | done | `04-hld-projects/bot-detection-platform/diagrams/architecture.mmd` (+6 more files) |  |
| `T-HLD-DIAG-sync-matrix` | Synchronize HLD Diagram Source Matrix with All 44 Projects | HLD | P2 | done | `04-hld-projects/hld-diagram-source-matrix.md` |  |
| `T-HLD-NEW-content-delivery-network` | Create Flagship System: Content Delivery Network (CDN) | HLD | P0 | open | Missing 4 of 13 files, e.g. `04-hld-projects/content-delivery-network/python/v1-basic/cdn_edge_cache.py` |  |
| `T-HLD-NEW-distributed-unique-id-snowflake` | Create Flagship System: Distributed Unique ID Generator (Snowflake) | HLD | P0 | open | Missing 2 of 13 files, e.g. `04-hld-projects/distributed-unique-id-snowflake/java/v1-basic/SnowflakeIdGenerator.java` |  |
| `T-HLD-NEW-api-gateway` | Create Flagship System: Enterprise API Gateway | HLD | P0 | open | Missing 4 of 13 files, e.g. `04-hld-projects/api-gateway/python/v1-basic/api_gateway_router.py` |  |
| `T-HLD-NEW-distributed-tracing` | Create Flagship System: Distributed Tracing System (OpenTelemetry/Jaeger) | HLD | P0 | open | Missing 4 of 13 files, e.g. `04-hld-projects/distributed-tracing/python/v1-basic/tracing_collector.py` |  |
| `T-HLD-NEW-multi-region-active-active` | Create Flagship System: Multi-Region Active-Active Architecture | HLD | P0 | open | Missing 4 of 13 files, e.g. `04-hld-projects/multi-region-active-active/python/v1-basic/active_active_replicator.py` |  |
| `T-LLD-JAVA-atm-system-fix` | Fix Duplicate Class Declarations and Package Collisions in ATM System Java | LLD | P0 | done | `02-lld-projects/atm-system/java/` |  |
| `T-LLD-JAVA-car-rental-fix` | Fix Duplicate Class Declarations in Car Rental Java | LLD | P0 | done | `02-lld-projects/car-rental/java/` |  |
| `T-LLD-JAVA-elevator-system-fix` | Fix Duplicate Class Declarations in Elevator System Java | LLD | P0 | done | `02-lld-projects/elevator-system/java/` |  |
| `T-LLD-JAVA-hotel-reservation-fix` | Fix Duplicate Class Declarations in Hotel Reservation Java | LLD | P0 | done | `02-lld-projects/hotel-reservation/java/` |  |
| `T-LLD-JAVA-library-management-fix` | Fix Duplicate Class Declarations in Library Management Java | LLD | P0 | done | `02-lld-projects/library-management/java/` |  |
| `T-LLD-JAVA-linkedin-connection-fix` | Fix Missing Symbol getCommonSkills in LinkedIn Connection Java v2 | LLD | P0 | done | `02-lld-projects/linkedin-connection/java/` |  |
| `T-LLD-JAVA-lru-cache-fix` | Fix Duplicate Classes and Incompatible Types in LRU Cache Java | LLD | P0 | done | `02-lld-projects/lru-cache/java/` |  |
| `T-LLD-JAVA-online-shopping-cart-fix` | Fix Duplicate Class Declarations in Online Shopping Cart Java | LLD | P0 | done | `02-lld-projects/online-shopping-cart/java/` |  |
| `T-LLD-JAVA-parking-lot-fix` | Fix Duplicate Pricing Strategy Declarations in Parking Lot Java v2 | LLD | P0 | done | `02-lld-projects/parking-lot/java/` |  |
| `T-LLD-JAVA-rate-limiter-fix` | Fix Duplicate RateLimitResult and Constructor Mismatches in Rate Limiter Java | LLD | P0 | done | `02-lld-projects/rate-limiter/java/` |  |
| `T-LLD-JAVA-restaurant-management-fix` | Fix Duplicate TableStatus and OrderStatus Enums in Restaurant Management Java | LLD | P0 | done | `02-lld-projects/restaurant-management/java/` |  |
| `T-LLD-JAVA-ride-sharing-system-fix` | Fix Duplicate Location, Rider, and Driver Classes in Ride Sharing Java | LLD | P0 | done | `02-lld-projects/ride-sharing-system/java/` |  |
| `T-LLD-JAVA-splitwise-fix` | Fix Duplicate Split Class Declaration in Splitwise Java v2 | LLD | P0 | done | `02-lld-projects/splitwise/java/` |  |
| `T-LLD-JAVA-stack-overflow-fix` | Fix Duplicate StackOverflowService and VoteType in Stack Overflow Java | LLD | P0 | done | `02-lld-projects/stack-overflow/java/` |  |
| `T-LLD-JAVA-tic-tac-toe-fix` | Fix Game Constructor Mismatch in Tic Tac Toe Java v3 | LLD | P0 | done | `02-lld-projects/tic-tac-toe/java/` |  |
| `T-LLD-JAVA-vending-machine-fix` | Fix Duplicate Coin Enum Declaration in Vending Machine Java | LLD | P0 | done | `02-lld-projects/vending-machine/java/` |  |
| `T-LLD-CONC-parking-lot` | Eliminate Double-Allocation Race Condition in Parking Lot (Java & Python) | LLD | P0 | done | `02-lld-projects/parking-lot/java/v3-optimized/` (+1 more files) |  |
| `T-LLD-CONC-elevator-system` | Implement Thread-Safe ConcurrentSkipListSet and State Machine in Elevator (Java & Python) | LLD | P0 | done | `02-lld-projects/elevator-system/java/v3-optimized/` (+1 more files) |  |
| `T-LLD-CONC-ride-sharing-system` | Eliminate Double-Matching Driver Race Condition in Ride Sharing (Java & Python) | LLD | P0 | done | `02-lld-projects/ride-sharing-system/java/v3-optimized/` (+1 more files) |  |
| `T-LLD-CONC-movie-ticket-booking` | Fix TOCTOU Seat Double-Booking Race Condition in Movie Ticket Booking (Java & Python) | LLD | P0 | done | `02-lld-projects/movie-ticket-booking/java/v3-optimized/` (+1 more files) |  |
| `T-LLD-CONC-rate-limiter` | Implement Atomic Compare-And-Swap Token Bucket & Sliding Window Counter (Java & Python) | LLD | P0 | done | `02-lld-projects/rate-limiter/java/v3-optimized/` (+1 more files) |  |
| `T-LLD-CONC-lru-cache` | Implement High-Throughput Concurrent LRU with Lock Striping / Read Buffers (Java & Python) | LLD | P0 | done | `02-lld-projects/lru-cache/java/v3-optimized/` (+1 more files) |  |
| `T-LLD-CONC-job-scheduler` | Implement Thread-Safe Worker Pool and DAG Dependency Execution in Job Scheduler | LLD | P0 | done | `02-lld-projects/job-scheduler/java/v3-optimized/` (+1 more files) |  |
| `T-LLD-CONC-meeting-room-scheduler` | Fix Concurrent Interval Overlap Race in Meeting Room Scheduler (Java & Python) | LLD | P0 | done | `02-lld-projects/meeting-room-scheduler/java/v3-optimized/` (+1 more files) |  |
| `T-LLD-CONC-atm-system` | Implement Atomic Account Transfers with Deterministic Lock Ordering in ATM System | LLD | P0 | done | `02-lld-projects/atm-system/java/v3-optimized/` (+1 more files) |  |
| `T-LLD-JAVA-elevator-v3-real` | Implement SCAN/LOOK Algorithm & Dispatch Strategy in Elevator Java v3 | LLD | P1 | done | `02-lld-projects/elevator-system/java/v3-optimized/` |  |
| `T-LLD-PY-elevator-v2-v3-real` | Implement Dynamic Dispatch and SCAN Algorithm in Elevator Python v2 and v3 | LLD | P1 | done | `02-lld-projects/elevator-system/python/` |  |
| `T-LLD-JAVA-car-rental-v3-real` | Implement Dynamic Pricing and Fleet Rebalancing in Car Rental Java v3 | LLD | P1 | done | `02-lld-projects/car-rental/java/v3-optimized/` |  |
| `T-LLD-PY-car-rental-v2-v3-real` | Implement Vehicle Type Strategies and Dynamic Pricing in Car Rental Python v2/v3 | LLD | P1 | done | `02-lld-projects/car-rental/python/` |  |
| `T-LLD-JAVA-hotel-reservation-v3-real` | Implement Overbooking Buffer and Dynamic Pricing in Hotel Reservation Java v3 | LLD | P1 | done | `02-lld-projects/hotel-reservation/java/v3-optimized/` |  |
| `T-LLD-PY-hotel-reservation-v2-v3-real` | Implement Room Amenities Strategy and Seasonal Rates in Hotel Reservation Python v2/v3 | LLD | P1 | done | `02-lld-projects/hotel-reservation/python/` |  |
| `T-LLD-JAVA-library-management-v3-real` | Implement Reservation Waitlist and Tiered Fine Strategy in Library Java v3 | LLD | P1 | done | `02-lld-projects/library-management/java/v3-optimized/` |  |
| `T-LLD-PY-library-management-v2-v3-real` | Implement Automated Lending Policies and Reservation Queue in Library Python v2/v3 | LLD | P1 | done | `02-lld-projects/library-management/python/` |  |
| `T-LLD-JAVA-snake-and-ladder-v2-v3-real` | Implement Special Obstacles and Simulation Engine in Snake & Ladder Java v2/v3 | LLD | P1 | done | `02-lld-projects/snake-and-ladder/java/` |  |
| `T-LLD-PY-snake-and-ladder-v2-v3-real` | Implement Extensible Obstacle Strategies in Snake & Ladder Python v2/v3 | LLD | P1 | done | `02-lld-projects/snake-and-ladder/python/` |  |
| `T-LLD-JAVA-online-shopping-cart-v3-real` | Implement Temporary Inventory Lock with TTL and Coupon Engine in Shopping Cart Java v3 | LLD | P1 | done | `02-lld-projects/online-shopping-cart/java/v3-optimized/` |  |
| `T-LLD-JAVA-ride-sharing-v3-real` | Implement Surge Pricing Multiplier and Ride Pooling in Ride Sharing Java v3 | LLD | P1 | done | `02-lld-projects/ride-sharing-system/java/v3-optimized/` |  |
| `T-LLD-JAVA-stack-overflow-v3-real` | Implement Reputation Scoring and Tag Inverted Index in Stack Overflow Java v3 | LLD | P1 | done | `02-lld-projects/stack-overflow/java/v3-optimized/` |  |
| `T-LLD-JAVA-movie-ticket-v2-real` | Implement Theatre Seating Tiers and Addon Packages in Movie Ticket Booking Java v2 | LLD | P1 | done | `02-lld-projects/movie-ticket-booking/java/v2-extended/` |  |
| `T-LLD-PY-movie-ticket-v2-real` | Implement Tiered Seating and Payment Integration in Movie Ticket Booking Python v2 | LLD | P1 | done | `02-lld-projects/movie-ticket-booking/python/v2-extended/` |  |
| `T-LLD-CODE-ad-click-aggregator` | Implement Real Sliding Window Click Aggregator and Deduplication (Java & Python) | LLD | P0 | done | `02-lld-projects/ad-click-aggregator/java/` (+1 more files) |  |
| `T-LLD-CODE-instagram-core-v2-v3` | Implement Fan-Out on Write & Read Feeds and Follow Graph in Instagram Core | LLD | P0 | done | `02-lld-projects/instagram-core/java/v2-extended/` (+3 more files) |  |
| `T-LLD-CODE-job-scheduler-v1` | Implement Real Cron Parser and Scheduled Delay Queue in Job Scheduler | LLD | P0 | done | `02-lld-projects/job-scheduler/java/v1-basic/` (+1 more files) |  |
| `T-LLD-CODE-live-comments-v2-v3` | Implement Live Comment Broadcast, Replay Ring Buffer, and Ingress Rate Limiting | LLD | P0 | done | `02-lld-projects/live-comments/java/v2-extended/` (+3 more files) |  |
| `T-LLD-CODE-online-auction-v2-v3` | Implement English / Vickrey Auction Engine, Proxy Bidding, and Anti-Sniping | LLD | P0 | done | `02-lld-projects/online-auction/java/v2-extended/` (+3 more files) |  |
| `T-LLD-CODE-payment-system-v1-v2-v3` | Implement Idempotent Payment Intent Engine, Multi-PSP Routing, and Webhook Processor | LLD | P0 | done | `02-lld-projects/payment-system/java/` (+1 more files) |  |
| `T-LLD-CODE-price-tracking-service-v2-v3` | Implement Sliding Price History, Target Alerts, and Scraper Ingestion Engine | LLD | P0 | done | `02-lld-projects/price-tracking-service/java/v2-extended/` (+3 more files) |  |
| `T-LLD-CODE-social-post-search-v2-v3` | Implement Inverted Index, Tokenization, and BM25 Relevance Scoring Engine | LLD | P0 | done | `02-lld-projects/social-post-search/java/v2-extended/` (+3 more files) |  |
| `T-LLD-CODE-web-crawler-v1-v2-v3` | Implement Multi-Threaded BFS Web Crawler with URL Frontier and Bloom Filter | LLD | P0 | done | `02-lld-projects/web-crawler/java/` (+1 more files) |  |
| `T-LLD-CODE-youtube-top-k-v2-v3` | Implement Count-Min Sketch and Heavy Hitters Min-Heap in YouTube Top-K | LLD | P0 | done | `02-lld-projects/youtube-top-k/java/v2-extended/` (+3 more files) |  |
| `T-LLD-NORM-finite-state-machine` | Normalize Java Directory Layout to Kebab-Case in Finite State Machine | LLD | P1 | done | `02-lld-projects/finite-state-machine/java/` |  |
| `T-LLD-NORM-payment-gateway-router` | Normalize Java Directory Layout to Kebab-Case in Payment Gateway Router | LLD | P1 | done | `02-lld-projects/payment-gateway-router/java/` |  |
| `T-LLD-NORM-webhook-dispatcher` | Normalize Directory Layout and Remove Rogue python/src in Webhook Dispatcher | LLD | P1 | done | `02-lld-projects/webhook-dispatcher/` |  |
| `T-LLD-NORM-text-editor` | Flatten Nested java/src Folders in Text Editor to Standard Version Folders | LLD | P1 | done | `02-lld-projects/text-editor/java/` |  |
| `T-LLD-NORM-market-alert-engine` | Flatten Nested java/v2-extended/src and v3-optimized/src in Market Alert Engine | LLD | P1 | done | `02-lld-projects/market-alert-engine/java/` |  |
| `T-LLD-NORM-message-queue` | Flatten Nested java/v2-extended/src and v3-optimized/src in Message Queue | LLD | P1 | done | `02-lld-projects/message-queue/java/` |  |
| `T-LLD-CODE-rideshare-matching-v2-v3` | Implement v2 and v3 in Java & Python for Rideshare Matching Engine and Remove rideshare/ Dir | LLD | P1 | done | `02-lld-projects/rideshare-matching-engine/` |  |
| `T-LLD-CODE-unix-vfs-v2-v3` | Implement File Permissions, Open File Table, and Inode Cache in Unix VFS v2 and v3 | LLD | P1 | done | `02-lld-projects/unix-vfs/` |  |
| `T-LLD-DOC-strong-answers-batch-1` | Author Authoritative STRONG-ANSWER.md Guides for Projects 1 to 15 (Gaming & Classics) | LLD | P1 | done | `02-lld-projects/ad-click-aggregator/STRONG-ANSWER.md` (+14 more files) |  |
| `T-LLD-DOC-strong-answers-batch-2` | Author Authoritative STRONG-ANSWER.md Guides for Projects 16 to 30 (Booking & Infra) | LLD | P1 | done | `02-lld-projects/linkedin-connection/STRONG-ANSWER.md` (+14 more files) |  |
| `T-LLD-DOC-strong-answers-batch-3` | Author Authoritative STRONG-ANSWER.md Guides for Projects 31 to 46 (Streaming & Social) | LLD | P1 | done | `02-lld-projects/restaurant-management/STRONG-ANSWER.md` (+14 more files) |  |
| `T-LLD-DOC-expand-stub-docs` | Expand 36 Sub-80-Word Stub Documentation Files Across 14 Projects | LLD | P2 | done | `02-lld-projects/ad-click-aggregator/` (+13 more files) |  |
| `T-LLD-DOC-matrix-sync` | Synchronize LLD Documentation Coverage Matrix with Verified Reality | LLD | P2 | done | `02-lld-projects/lld-doc-coverage-matrix.md` |  |
| `T-LLD-NEW-food-delivery-platform` | Implement Food Delivery Platform (Swiggy / DoorDash) in Java & Python | LLD | P0 | done | `02-lld-projects/food-delivery-platform/PROBLEM.md` (+7 more files) |  |
| `T-LLD-NEW-in-memory-event-bus` | Implement In-Memory Event Bus / Pub-Sub (Kafka-Lite) in Java & Python | LLD | P0 | done | `02-lld-projects/in-memory-event-bus/PROBLEM.md` (+7 more files) |  |
| `T-LLD-NEW-circuit-breaker` | Implement Extensible Circuit Breaker Pattern (Resilience4j) in Java & Python | LLD | P0 | done | `02-lld-projects/circuit-breaker/PROBLEM.md` (+7 more files) |  |
| `T-LLD-NEW-api-gateway` | Implement API Gateway & Reverse Proxy Filter Pipeline in Java & Python | LLD | P0 | done | `02-lld-projects/api-gateway/PROBLEM.md` (+7 more files) |  |
| `T-LLD-NEW-distributed-counter` | Implement High-Concurrency Striped Counter (LongAdder) in Java & Python | LLD | P1 | done | `02-lld-projects/distributed-counter/PROBLEM.md` (+7 more files) |  |
| `T-LLD-NEW-hotel-management-system` | Implement Hotel Property Management System (PMS) in Java & Python | LLD | P1 | done | `02-lld-projects/hotel-management-system/PROBLEM.md` (+7 more files) |  |
| `T-LLD-NEW-dynamic-config-service` | Implement Dynamic Configuration & Feature Flag Engine in Java & Python | LLD | P1 | done | `02-lld-projects/dynamic-config-service/PROBLEM.md` (+7 more files) |  |
| `T-LLD-NEW-online-code-judge` | Implement Online Code Judge & Sandbox Runner in Java & Python | LLD | P1 | done | `02-lld-projects/online-code-judge/PROBLEM.md` (+7 more files) |  |
| `T-LLD-NEW-key-value-store-lsm` | Implement In-Memory LSM-Tree & WAL Key-Value Store in Java & Python | LLD | P1 | done | `02-lld-projects/key-value-store-lsm/PROBLEM.md` (+7 more files) |  |
| `T-LLD-NEW-notification-service` | Implement Multi-Channel Notification Router & Dispatcher in Java & Python | LLD | P1 | done | `02-lld-projects/notification-service/PROBLEM.md` (+7 more files) |  |
| `T-ASSESS-QUIZ-fix-applied-ml-answers` | Fix Bare Letters and 83% B Option Bias in Applied ML System Design Answers | ASSESSMENT | P0 | done | `quizzes/applied-ml-system-design-quiz.md` (+1 more files) |  |
| `T-ASSESS-QUIZ-fix-coding-pattern-answers` | Fix Bare Letter Answer Keys in Binary Search, Sliding Window, and Two Pointers Quizzes | ASSESSMENT | P0 | done | `quizzes/answers/binary-search-answers.md` (+5 more files) |  |
| `T-ASSESS-QUIZ-fix-behavioral-salary-answers` | Expand Behavioral and Salary Negotiation Answer Keys with Detailed Question Rationales and Rebalance Options | ASSESSMENT | P0 | done | `quizzes/answers/behavioral-interviews-answers.md` (+3 more files) |  |
| `T-ASSESS-QUIZ-fix-hld-infra-answers` | Expand 1-Line Soundbites in HLD Concepts, HLD Projects, and Infra Quizzes into Deep Technical Explanations | ASSESSMENT | P0 | done | `quizzes/answers/hld-concepts-answers.md` (+5 more files) |  |
| `T-ASSESS-QUIZ-reconcile-ai-coding-duplicates` | Reconcile and Deduplicate AI Coding Interview Quizzes and Answer Keys | ASSESSMENT | P1 | done | `quizzes/ai-coding-interview-quiz.md` (+4 more files) |  |
| `T-ASSESS-QUIZ-theory-networking-db-os` | Author Quizzes and Detailed Answer Keys for Core CS Theory (Networking, DB Internals, OS, Security) | ASSESSMENT | P1 | done | `quizzes/networking-fundamentals-quiz.md` (+7 more files) |  |
| `T-ASSESS-QUIZ-hld-modular-concepts` | Author Modular Quizzes and Answer Keys for Caching, Sharding, Message Queues, and API Gateways | ASSESSMENT | P1 | done | `quizzes/caching-strategies-quiz.md` (+7 more files) |  |
| `T-ASSESS-QUIZ-genai-specialized` | Author Specialized Quizzes and Answer Keys for RAG, LLM Inference, Agents, and Safety/Evals | ASSESSMENT | P1 | done | `quizzes/rag-vector-db-quiz.md` (+7 more files) |  |
| `T-ASSESS-QUIZ-coding-advanced` | Author Advanced Coding Pattern Quizzes (Graph Algorithms, Monotonic Stack, Intervals, Bit Manipulation) | ASSESSMENT | P2 | done | `quizzes/graph-algorithms-quiz.md` (+7 more files) |  |
| `T-ASSESS-FC-populate-flashcard-backs-part1` | Populate Authoritative Back Answers for Architecture & Pattern Flashcards (HLD, LLD, Patterns, Distributed) | ASSESSMENT | P0 | done | `flashcards/hld-concepts.md` (+3 more files) |  |
| `T-ASSESS-FC-populate-flashcard-backs-part2` | Populate Authoritative Back Answers for All 10 Coding Pattern Flashcard Decks | ASSESSMENT | P1 | done | `flashcards/binary-search.md` (+9 more files) |  |
| `T-ASSESS-FC-populate-flashcard-backs-part3` | Populate Authoritative Back Answers for Behavioral, Salary, Applied ML, AI Coding & GenAI Flashcards | ASSESSMENT | P1 | done | `flashcards/behavioral-interviews.md` (+6 more files) |  |
| `T-ASSESS-FC-missing-decks` | Author 7 Missing High-Yield Flashcard Decks with Front/Back Cards | ASSESSMENT | P1 | done | `flashcards/distributed-storage-consensus.md` (+6 more files) |  |
| `T-ASSESS-FC-anki-export-automation` | Automated Anki TSV Exporter Script & Updated Spaced-Repetition User Guide | ASSESSMENT | P2 | done | `scripts/export_anki_decks.py` |  |
| `T-ASSESS-SOL-dedup-orphan-solutions` | Deduplicate Solutions and Wire All 14 Orphaned Solutions in Interview Mode | ASSESSMENT | P0 | done | `solutions/hld-bot-detection-platform.md` (+4 more files) |  |
| `T-ASSESS-STA-lld-batch-1` | Author STRONG-ANSWER.md and Solution Files for Top 15 High-Frequency LLD Projects | ASSESSMENT | P0 | done | `02-lld-projects/elevator-system/STRONG-ANSWER.md` (+28 more files) |  |
| `T-ASSESS-STA-lld-batch-2` | Author STRONG-ANSWER.md and Solution Files for Mid-Tier 15 LLD Projects | ASSESSMENT | P1 | done | `02-lld-projects/library-management/STRONG-ANSWER.md` (+29 more files) |  |
| `T-ASSESS-STA-lld-batch-3` | Author STRONG-ANSWER.md and Solution Files for Final 16 LLD Projects | ASSESSMENT | P1 | done | `02-lld-projects/logging-framework/STRONG-ANSWER.md` (+27 more files) |  |
| `T-ASSESS-PLAN-60-and-90-day` | Author Comprehensive 60-Day (Senior) and 90-Day (Staff/Principal) Study Roadmaps | ASSESSMENT | P1 | done | `resources/study-plans/60-day-plan.md` (+1 more files) |  |
| `T-ASSESS-PLAY-company-playbooks-mamaa` | Author FAANG/MAMAA Company System Design & LLD Interview Playbooks | ASSESSMENT | P1 | done | `resources/interview-tips/company-playbooks/google.md` (+7 more files) |  |
| `T-PORTAL-UI-flashcards-route` | Implement Interactive /flashcards Route with Flip Card Component, Categories & TSV Download | PORTAL | P0 | open | Missing 2 of 5 files, e.g. `apps/portal/src/components/flashcards/flashcard-viewer.tsx` |  |
| `T-PORTAL-UI-start-here-onboarding` | Implement /start (Start Here) Onboarding Guide Route in Portal | PORTAL | P1 | open | Missing 2 of 3 files, e.g. `apps/portal/src/components/onboarding/level-assessment.tsx` |  |
| `T-PORTAL-UI-learning-paths` | Implement /learning-paths Route with Role-Tailored Curriculum Roadmaps (Junior, Mid, Senior, Staff) | PORTAL | P1 | open | Missing 1 of 3 files, e.g. `apps/portal/src/components/learning-paths/track-view.tsx` |  |
| `T-PORTAL-UI-sidebar-and-nav-sync` | Expose /progress, /flashcards, /learning-paths, and /start in Portal Sidebar Navigation | PORTAL | P0 | done | `apps/portal/src/lib/sections.ts` (+1 more files) |  |
| `T-PORTAL-UI-interview-mode-lld-expansion` | Wire and Auto-Discover All 46 LLD Projects in Interview Mode with Filter Tabs | PORTAL | P0 | done | `apps/portal/src/content/interviews.ts` (+2 more files) |  |
| `T-PORTAL-REG-sync-types-and-difficulty` | Sync LLDProject strongAnswer Type Contract and Calibrate Difficulties for 100+ Topics | PORTAL | P1 | done | `apps/portal/src/content/types.ts` (+1 more files) |  |
| `T-TH-DOC-paxos-consensus-variants` | Author Paxos Consensus Protocol & Variants (Single-Decree, Multi-Paxos, Fast Paxos, EPaxos) | THEORY | P0 | done | `00-theory/distributed-systems/paxos-consensus-variants.md` |  |
| `T-TH-DOC-raft-consensus-protocol` | Author Raft Distributed Consensus Protocol with Formal Safety Invariants & Joint Consensus | THEORY | P0 | done | `00-theory/distributed-systems/raft-consensus-protocol.md` |  |
| `T-TH-DOC-two-phase-and-three-phase-commit` | Author Two-Phase Commit (2PC) & Three-Phase Commit (3PC) Protocols with Failure Invariant Analysis | THEORY | P0 | done | `00-theory/distributed-systems/two-phase-and-three-phase-commit.md` |  |
| `T-TH-DOC-crdts-and-semilattice-proofs` | Author Conflict-Free Replicated Data Types (CRDTs) with Mathematical Semilattice Proofs & Parity Code | THEORY | P0 | done | `00-theory/distributed-systems/crdt-conflict-free-replicated-data-types.md` |  |
| `T-TH-DOC-logical-time-and-vector-clocks` | Author Logical Time, Lamport Clocks & Vector Clocks with Causality Proofs & Dual-Language Code | THEORY | P0 | done | `00-theory/distributed-systems/logical-time-and-vector-clocks.md` |  |
| `T-TH-DOC-swim-gossip-protocol` | Author SWIM Gossip & Failure Detection Protocol with Suspicion Mechanism Analysis | THEORY | P1 | done | `00-theory/distributed-systems/swim-gossip-protocol.md` |  |
| `T-TH-DOC-quorum-consistency-and-anti-entropy` | Author Quorum Consistency, Hinted Handoff & Merkle Tree Anti-Entropy Synchronization | THEORY | P1 | done | `00-theory/distributed-systems/quorum-consistency-and-anti-entropy.md` |  |
| `T-TH-DOC-aries-recovery-algorithm` | Author ARIES Database Recovery Algorithm, Physiological Logging & CLR Execution Traces | THEORY | P0 | done | `00-theory/database-concepts/aries-recovery-algorithm.md` |  |
| `T-TH-DOC-b-plus-tree-latch-crabbing` | Author B+ Tree Physical Node Layout, Fanout Calculus & Latch Crabbing Concurrency Protocol | THEORY | P0 | done | `00-theory/database-concepts/b-plus-tree-indexing-and-latch-crabbing.md` |  |
| `T-TH-DOC-database-normalization-theory` | Author Formal Database Normalization Theory (1NF through BCNF and 4NF) & Lossless Joins | THEORY | P1 | done | `00-theory/database-concepts/database-normalization-theory.md` |  |
| `T-TH-DOC-acid-isolation-mvcc-anomalies` | Overhaul ACID Properties: Berenson 1995 Critique, Snapshot Isolation, Write Skew & Python Parity | THEORY | P0 | done | `00-theory/database-concepts/acid-properties.md` |  |
| `T-TH-DOC-rum-conjecture-refactor` | Refactor RUM Conjecture: Delete Root Duplicate & Add Trade-off Radar Diagrams | THEORY | P1 | done | Moved to `00-theory/database-concepts/rum-conjecture.md`; no root duplicate. |  |
| `T-TH-DOC-database-sharding-internals` | Deepen Database Sharding: Routing Tiers, Scatter-Gather, Cross-Shard 2PC & Migration Math | THEORY | P1 | done | `00-theory/database-concepts/sharding.md` |  |
| `T-TH-DOC-replication-cdc-lag-anomalies` | Deepen Database Replication: SBR/RBR Formats, CDC Debezium, Lag Anomalies & Python Parity | THEORY | P1 | done | `00-theory/database-concepts/replication.md` |  |
| `T-TH-DOC-modern-sql-nosql-newsql` | Modernize SQL vs NoSQL: Eradicate Scaling Myths, Integrate Distributed SQL & Columnar OLAP | THEORY | P1 | done | `00-theory/database-concepts/sql-vs-nosql.md` |  |
| `T-TH-DOC-lock-free-data-structures-and-aba` | Author Lock-Free Data Structures (Treiber Stack, MS Queue) with ABA Solutions & Parity Code | THEORY | P0 | done | `00-theory/concurrency/lock-free-data-structures-and-aba.md` |  |
| `T-TH-DOC-deadlock-theory-and-coffman-conditions` | Author Deadlock Theory: Coffman Conditions, Resource Allocation Graphs & Banker's Algorithm | THEORY | P1 | done | `00-theory/concurrency/deadlock-theory-and-coffman-conditions.md` |  |
| `T-TH-DOC-synchronization-primitives-and-barriers` | Author Concurrency Synchronization Primitives, Hardware Memory Fences & JMM vs GIL | THEORY | P1 | done | `00-theory/concurrency/synchronization-primitives-and-barriers.md` |  |
| `T-TH-DOC-memory-models-and-cache-coherence-refresh` | Refresh Memory Models & Cache Coherence: Add MESI State Diagram, False Sharing Diagram & Code | THEORY | P1 | done | `00-theory/system-design-fundamentals/memory-models-and-cache-coherence.md` |  |
| `T-TH-DOC-b-trees-and-b-plus-trees` | Author B-Trees and B+ Trees Architectural Foundations, Split/Merge Algorithms & Fanout Math | THEORY | P0 | done | `00-theory/data-structures/b-trees-and-b-plus-trees.md` |  |
| `T-TH-DOC-advanced-hash-tables` | Author Advanced Hash Tables in Low-Latency Systems: Robin Hood, Hopscotch, Cuckoo & Swiss Tables | THEORY | P1 | done | `00-theory/data-structures/advanced-hash-tables.md` |  |
| `T-TH-DOC-inverted-indexes-and-roaring-bitmaps` | Author Inverted Indexes, Postings Compression (VByte) & Roaring Bitmaps with Parity Code | THEORY | P1 | done | `00-theory/data-structures/inverted-indexes-and-roaring-bitmaps.md` |  |
| `T-TH-DOC-spatial-indexing-geohash-quadtree-s2` | Author Spatial & Multidimensional Indexing (Geohash, Quadtree, R-Tree, Google S2 Geometry) | THEORY | P0 | done | `00-theory/data-structures/spatial-and-multidimensional-indexing.md` |  |
| `T-TH-DOC-ring-buffers-and-gorilla-compression` | Author Circular Ring Buffers, LMAX Disruptor & Gorilla Time-Series Compression with Parity Code | THEORY | P1 | done | `00-theory/data-structures/ring-buffers-and-gorilla-compression.md` |  |
| `T-TH-DOC-auth-sessions-and-jwts` | Author Authentication Architecture: Stateful Sessions vs Stateless JWTs & Token Revocation | THEORY | P0 | done | `00-theory/security-and-auth/authentication-sessions-and-jwts.md` |  |
| `T-TH-DOC-oauth2-and-oidc-protocols` | Author OAuth 2.0 & OpenID Connect (OIDC) Protocols with PKCE Flow & Sequence Diagrams | THEORY | P0 | done | `00-theory/security-and-auth/oauth2-and-oidc-protocols.md` |  |
| `T-TH-DOC-authorization-rbac-abac-rebac` | Author Authorization Architectures: RBAC, ABAC & ReBAC (Google Zanzibar Tuple Evaluation) | THEORY | P0 | done | `00-theory/security-and-auth/authorization-rbac-abac-rebac.md` |  |
| `T-TH-DOC-cryptography-tls-and-password-hashing` | Author Cryptographic Foundations, TLS 1.3 1-RTT Handshake & Argon2id Password Hashing | THEORY | P0 | done | `00-theory/security-and-auth/cryptography-tls-and-password-hashing.md` |  |
| `T-TH-DOC-appsec-threat-modeling-owasp` | Author Application Security, STRIDE Threat Modeling & OWASP Top 10 Engineering Defenses | THEORY | P1 | done | `00-theory/security-and-auth/application-security-and-threat-modeling.md` |  |
| `T-TH-DOC-solid-principles-python-parity-and-diagrams` | Enforce Python Parity & Author Mermaid Class Diagrams for SOLID Principles | THEORY | P1 | done | `00-theory/oop-principles/solid-principles.md` |  |
| `T-TH-DOC-composition-vs-inheritance-python-parity` | Enforce Python Parity & Author Fragile Base Class Mermaid Diagram for Composition vs Inheritance | THEORY | P1 | done | `00-theory/oop-principles/composition-vs-inheritance.md` |  |
| `T-TH-DOC-encapsulation-abstraction-python-parity` | Enforce Python Parity & Author Abstraction Barrier Diagram for Encapsulation & Abstraction | THEORY | P1 | done | `00-theory/oop-principles/encapsulation-abstraction.md` |  |
| `T-TH-DOC-dry-kiss-yagni-python-parity` | Enforce Python Parity & Author Rule-of-Three Flowchart for DRY, KISS, and YAGNI | THEORY | P1 | done | `00-theory/oop-principles/dry-kiss-yagni.md` |  |
| `T-TH-DOC-cap-theorem-deduplication-and-formal-proof` | Deduplicate CAP Theorem Article, Add Gilbert & Lynch 2002 Proof, Split-Brain Diagram & Code | THEORY | P0 | done | `00-theory/system-design-fundamentals/cap-theorem.md` |  |
| `T-TH-DOC-pacelc-theorem-diagrams-and-simulation` | Author PACELC 4-Quadrant Diagram, Cross-Region Latency Budget Trace & Quorum Simulation Code | THEORY | P1 | done | `00-theory/system-design-fundamentals/pacelc-theorem.md` |  |
| `T-TH-DOC-ml-generalization-relocation` | Relocate Orphan ML Generalization Note to GenAI Concepts Domain & Update References | THEORY | P2 | done | `06-genai-systems/00-concepts/ml-generalization/README.md` |  |
| `T-TH-DOC-architecture-fundamentals-parity-and-diagrams` | Enforce Python Parity & Author Architecture Diagrams across Core System Design Fundamentals | THEORY | P1 | done | `00-theory/system-design-fundamentals/client-server-architecture.md` (+4 more files) |  |
| `T-TH-DOC-networking-tls-http3-python-parity` | Upgrade Networking Basics: TLS 1.3 ECDHE Handshake, HTTP/3 Transport & Python asyncio Parity | THEORY | P1 | done | `00-theory/networking-basics/http-https.md` (+1 more files) |  |
| `T-TH-DOC-complexity-analysis-python-parity-and-curves` | Enforce Python Parity for All 21 Complexity Examples & Author Visual Big-O Growth Curves | THEORY | P2 | done | `00-theory/complexity-analysis/big-o-notation.md` (+1 more files) |  |
| `T-TH-DOC-theory-index-and-navigation-sync` | Synchronize Master Navigation Index, Reading Sequences & Cross-References in 00-theory/README.md | THEORY | P0 | done | `00-theory/README.md` (+2 more files) |  |
