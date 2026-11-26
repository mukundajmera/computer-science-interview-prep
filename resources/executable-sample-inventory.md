# Executable Sample Inventory

This inventory lists executable source samples outside the main LLD project contracts. It excludes tests, `__init__.py`, and generated files.

Status meanings:

- `tested`: the same concept/language folder has a test suite. This indicates suite-backed sample coverage, not line coverage for every file.
- `illustrative-only`: no same-language test suite is present yet; the file is an instructional sample.
- `move-to-lld`: the sample should migrate to an LLD-style project before being treated as executable curriculum.

## Current Samples

| Path | Status | Evidence |
|------|--------|----------|
| `03-hld-concepts/api-design/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/api-design/java/v1-simple/IdempotencyStore.java` | tested | Same-language test suite present. |
| `03-hld-concepts/api-design/java/v1-simple/VersionedBookingApi.java` | tested | Same-language test suite present. |
| `03-hld-concepts/api-design/python/v1-simple/idempotency_store.py` | tested | Same-language test suite present. |
| `03-hld-concepts/api-design/python/v1-simple/versioned_booking_api.py` | tested | Same-language test suite present. |
| `03-hld-concepts/api-gateway/java/v1-simple/SimpleGateway.java` | tested | Same-language test suite present. |
| `03-hld-concepts/api-gateway/python/v1-simple/simple_gateway.py` | tested | Same-language test suite present. |
| `03-hld-concepts/cache-invalidation-patterns/java/ResilientCacheService.java` | tested | Same-language test suite present. |
| `03-hld-concepts/cache-invalidation-patterns/python/resilient_cache_service.py` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/java/v1-simple/SimpleCache.java` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/java/v2-realistic/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/java/v2-realistic/LRUCache.java` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/java/v3-production/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/java/v3-production/WriteThruCache.java` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/java/v4_xfetch/SingleflightMutex.java` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/java/v4_xfetch/XFetchCache.java` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/python/v1-simple/simple_cache.py` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/python/v2-realistic/lru_cache.py` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/python/v3-production/write_thru_cache.py` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/python/v4-xfetch/singleflight.py` | tested | Same-language test suite present. |
| `03-hld-concepts/caching/python/v4-xfetch/xfetch_cache.py` | tested | Same-language test suite present. |
| `03-hld-concepts/cap-theorem/java/v1-simple/CapSystem.java` | tested | Same-language test suite present. |
| `03-hld-concepts/cap-theorem/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/cap-theorem/python/v1-simple/cap_mode.py` | tested | Same-language test suite present. |
| `03-hld-concepts/cassandra/java/v1-simple/SimpleCassandraTable.java` | tested | Same-language test suite present. |
| `03-hld-concepts/cassandra/python/v1-simple/simple_cassandra_table.py` | tested | Same-language test suite present. |
| `03-hld-concepts/cdn/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/cdn/java/v1-simple/SimpleProxyCache.java` | tested | Same-language test suite present. |
| `03-hld-concepts/cdn/java/v2-realistic/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/cdn/java/v2-realistic/GeographicCDN.java` | tested | Same-language test suite present. |
| `03-hld-concepts/cdn/java/v3-production/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/cdn/java/v3-production/ProductionCDN.java` | tested | Same-language test suite present. |
| `03-hld-concepts/cdn/python/v1-simple/simple_proxy_cache.py` | tested | Same-language test suite present. |
| `03-hld-concepts/cdn/python/v2-realistic/geographic_cdn.py` | tested | Same-language test suite present. |
| `03-hld-concepts/cdn/python/v3-production/production_cdn.py` | tested | Same-language test suite present. |
| `03-hld-concepts/consistent-hashing/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/consistent-hashing/java/v1-simple/SimpleConsistentHash.java` | tested | Same-language test suite present. |
| `03-hld-concepts/consistent-hashing/java/v2-realistic/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/consistent-hashing/java/v2-realistic/VirtualNodeConsistentHash.java` | tested | Same-language test suite present. |
| `03-hld-concepts/consistent-hashing/java/v3-production/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/consistent-hashing/java/v3-production/ProductionConsistentHash.java` | tested | Same-language test suite present. |
| `03-hld-concepts/consistent-hashing/python/v1-simple/simple_consistent_hash.py` | tested | Same-language test suite present. |
| `03-hld-concepts/consistent-hashing/python/v2-realistic/virtual_node_hash.py` | tested | Same-language test suite present. |
| `03-hld-concepts/consistent-hashing/python/v3-production/production_hash.py` | tested | Same-language test suite present. |
| `03-hld-concepts/contention-control/java/v1-simple/OptimisticReservationService.java` | tested | Same-language test suite present. |
| `03-hld-concepts/contention-control/java/v2-realistic/ContentionPolicyCoordinator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/contention-control/java/v3-production/DistributedContentionCoordinator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/contention-control/python/v1-simple/optimistic_reservation_service.py` | tested | Same-language test suite present. |
| `03-hld-concepts/contention-control/python/v2-realistic/contention_policy_coordinator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/contention-control/python/v3-production/distributed_contention_coordinator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/data-partitioning/java/v1-simple/DataPartitioner.java` | tested | Same-language test suite present. |
| `03-hld-concepts/data-partitioning/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/data-partitioning/python/v1-simple/partitioner.py` | tested | Same-language test suite present. |
| `03-hld-concepts/database-isolation-levels/java/src/main/java/com/sysdesign/databaseisolationlevels/MvccTransactionEngine.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/database-isolation-levels/java/src/test/java/com/sysdesign/databaseisolationlevels/MvccTransactionEngineTest.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/database-isolation-levels/python/mvcc/mvcc_transaction_engine.py` | tested | Same-language test suite present. |
| `03-hld-concepts/database-live-resharding/java/src/LiveReshardingMigrator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-live-resharding/python/src/live_resharding_migrator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/database-replication/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-replication/java/v1-simple/SimplePrimaryReplica.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-replication/java/v2-realistic/AsyncReplication.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-replication/java/v2-realistic/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-replication/java/v3-production/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-replication/java/v3-production/MultiPrimaryReplication.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-replication/python/v1-simple/simple_primary_replica.py` | tested | Same-language test suite present. |
| `03-hld-concepts/database-replication/python/v2-realistic/async_replication.py` | tested | Same-language test suite present. |
| `03-hld-concepts/database-replication/python/v3-production/multi_primary_replication.py` | tested | Same-language test suite present. |
| `03-hld-concepts/database-sharding/java/v1-simple/HashShardRouter.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-sharding/java/v1-simple/V1Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-sharding/java/v2-realistic/RangeShardRouter.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-sharding/java/v2-realistic/V2Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-sharding/java/v3-production/ConsistentHashShardRouter.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-sharding/java/v3-production/V3Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/database-sharding/python/v1-simple/hash_shard_router.py` | tested | Same-language test suite present. |
| `03-hld-concepts/database-sharding/python/v2-realistic/range_shard_router.py` | tested | Same-language test suite present. |
| `03-hld-concepts/database-sharding/python/v3-production/consistent_hash_router.py` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-consensus-raft/java/RaftClusterSimulator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-consensus-raft/python/raft_cluster_simulator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-coordination/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-coordination/java/v1-simple/DistributedLock.java` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-coordination/python/v1-simple/distributed_lock.py` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-rate-limiting-scale/java/src/RedisSimulator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-rate-limiting-scale/java/src/Tier1DistributedRateLimiter.java` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-rate-limiting-scale/python/implementation/rate_limiter.py` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-transactions-saga-outbox/java/src/InboxConsumer.java` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-transactions-saga-outbox/java/src/SagaModels.java` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-transactions-saga-outbox/java/src/SagaOrchestratorEngine.java` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-transactions-saga-outbox/java/src/TransactionalOutboxRelay.java` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-transactions-saga-outbox/python/src/saga.py` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-transactions/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-transactions/java/v1-simple/TwoPhaseCommitCoordinator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-transactions/python/v1-simple/two_phase_commit_coordinator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/distributed-unique-id/java/ClockMovedBackwardsException.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/distributed-unique-id/java/Demo.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/distributed-unique-id/java/IdComponents.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/distributed-unique-id/java/SnowflakeIdGenerator.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/distributed-unique-id/java/SnowflakeIdGeneratorTest.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/distributed-unique-id/python/snowflake_id_generator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/dns/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/dns/java/v1-simple/DnsResolver.java` | tested | Same-language test suite present. |
| `03-hld-concepts/dns/java/v1-simple/SimpleDnsResolver.java` | tested | Same-language test suite present. |
| `03-hld-concepts/dns/python/v1-simple/dns_resolver.py` | tested | Same-language test suite present. |
| `03-hld-concepts/dns/python/v1-simple/simple_dns_resolver.py` | tested | Same-language test suite present. |
| `03-hld-concepts/dynamodb/java/v1-simple/DynamoAccessPatterns.java` | tested | Same-language test suite present. |
| `03-hld-concepts/dynamodb/java/v1-simple/SimpleDynamoTable.java` | tested | Same-language test suite present. |
| `03-hld-concepts/dynamodb/python/v1-simple/dynamo_access_patterns.py` | tested | Same-language test suite present. |
| `03-hld-concepts/dynamodb/python/v1-simple/simple_dynamo_table.py` | tested | Same-language test suite present. |
| `03-hld-concepts/elasticsearch/java/v1-simple/SimpleElasticsearchClient.java` | tested | Same-language test suite present. |
| `03-hld-concepts/elasticsearch/python/v1-simple/simple_elasticsearch_client.py` | tested | Same-language test suite present. |
| `03-hld-concepts/flink/java/v1-simple/StreamJobSkeleton.java` | tested | Same-language test suite present. |
| `03-hld-concepts/flink/python/v1-simple/stream_job_skeleton.py` | tested | Same-language test suite present. |
| `03-hld-concepts/idempotency/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/idempotency/java/v1-simple/IdempotencyKeyManager.java` | tested | Same-language test suite present. |
| `03-hld-concepts/idempotency/python/v1-simple/idempotency_key_manager.py` | tested | Same-language test suite present. |
| `03-hld-concepts/kafka/java/v1-simple/SimpleProducerConsumer.java` | tested | Same-language test suite present. |
| `03-hld-concepts/kafka/python/v1-simple/simple_producer_consumer.py` | tested | Same-language test suite present. |
| `03-hld-concepts/large-blob-handling/java/v1-simple/ChunkedBlobUploader.java` | tested | Same-language test suite present. |
| `03-hld-concepts/large-blob-handling/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/large-blob-handling/python/v1-simple/chunked_blob_uploader.py` | tested | Same-language test suite present. |
| `03-hld-concepts/load-balancing/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/load-balancing/java/v1-simple/RoundRobinLoadBalancer.java` | tested | Same-language test suite present. |
| `03-hld-concepts/load-balancing/java/v2-realistic/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/load-balancing/java/v2-realistic/WeightedLoadBalancer.java` | tested | Same-language test suite present. |
| `03-hld-concepts/load-balancing/java/v3-production/ConsistentHashingLB.java` | tested | Same-language test suite present. |
| `03-hld-concepts/load-balancing/java/v3-production/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/load-balancing/python/v1-simple/round_robin_lb.py` | tested | Same-language test suite present. |
| `03-hld-concepts/load-balancing/python/v2-realistic/weighted_lb.py` | tested | Same-language test suite present. |
| `03-hld-concepts/load-balancing/python/v3-production/consistent_hashing_lb.py` | tested | Same-language test suite present. |
| `03-hld-concepts/logical-clocks-truetime/java/src/CausalClockEngine.java` | tested | Same-language test suite present. |
| `03-hld-concepts/logical-clocks-truetime/python/causal_clock_engine.py` | tested | Same-language test suite present. |
| `03-hld-concepts/long-running-tasks/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/long-running-tasks/java/v1-simple/TaskTracker.java` | tested | Same-language test suite present. |
| `03-hld-concepts/long-running-tasks/python/v1-simple/task_tracker.py` | tested | Same-language test suite present. |
| `03-hld-concepts/message-queue-evolution/java/v1-basic/MessageQueueEvolutionSimulator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/message-queue-evolution/python/v1-basic/simulator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/message-queues/java/v1-simple/SimpleQueue.java` | tested | Same-language test suite present. |
| `03-hld-concepts/message-queues/java/v2-realistic/PubSubQueue.java` | tested | Same-language test suite present. |
| `03-hld-concepts/message-queues/java/v3-production/DurableQueue.java` | tested | Same-language test suite present. |
| `03-hld-concepts/message-queues/python/v1-simple/simple_queue.py` | tested | Same-language test suite present. |
| `03-hld-concepts/message-queues/python/v2-realistic/pubsub_queue.py` | tested | Same-language test suite present. |
| `03-hld-concepts/message-queues/python/v3-production/durable_queue.py` | tested | Same-language test suite present. |
| `03-hld-concepts/microservice-security/java/src/main/java/com/systemdesign/security/MicroserviceSecurityService.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/microservice-security/java/src/test/java/com/systemdesign/security/MicroserviceSecurityServiceTest.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/microservice-security/python/src/microservice_security.py` | tested | Same-language test suite present. |
| `03-hld-concepts/microservices-communication/java/v1-simple/SimpleServiceCall.java` | tested | Same-language test suite present. |
| `03-hld-concepts/microservices-communication/java/v2-realistic/CircuitBreaker.java` | tested | Same-language test suite present. |
| `03-hld-concepts/microservices-communication/java/v3-production/RetryWithBackoff.java` | tested | Same-language test suite present. |
| `03-hld-concepts/microservices-communication/python/v1-simple/simple_service_call.py` | tested | Same-language test suite present. |
| `03-hld-concepts/microservices-communication/python/v2-realistic/circuit_breaker.py` | tested | Same-language test suite present. |
| `03-hld-concepts/microservices-communication/python/v3-production/retry_with_backoff.py` | tested | Same-language test suite present. |
| `03-hld-concepts/mongodb/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/mongodb/java/v1-simple/DocumentStoreEngine.java` | tested | Same-language test suite present. |
| `03-hld-concepts/mongodb/python/v1-simple/document_store_engine.py` | tested | Same-language test suite present. |
| `03-hld-concepts/monitoring-observability/java/v1-simple/SimpleMetrics.java` | tested | Same-language test suite present. |
| `03-hld-concepts/monitoring-observability/java/v2-realistic/TimeSeriesMetrics.java` | tested | Same-language test suite present. |
| `03-hld-concepts/monitoring-observability/java/v3-production/AlertWindowEvaluator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/monitoring-observability/java/v3-production/AlertingSystem.java` | tested | Same-language test suite present. |
| `03-hld-concepts/monitoring-observability/java/v3-production/CardinalityGuard.java` | tested | Same-language test suite present. |
| `03-hld-concepts/monitoring-observability/python/v1-simple/simple_metrics.py` | tested | Same-language test suite present. |
| `03-hld-concepts/monitoring-observability/python/v2-realistic/time_series_metrics.py` | tested | Same-language test suite present. |
| `03-hld-concepts/monitoring-observability/python/v3-production/alert_window_evaluator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/monitoring-observability/python/v3-production/alerting_system.py` | tested | Same-language test suite present. |
| `03-hld-concepts/monitoring-observability/python/v3-production/cardinality_guard.py` | tested | Same-language test suite present. |
| `03-hld-concepts/mysql/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/mysql/java/v1-simple/InnoDBEngineSimulator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/mysql/python/v1-simple/innodb_engine_simulator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/network-protocol-evolution/java/src/main/java/network/Frame.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/network-protocol-evolution/java/src/main/java/network/ProtocolMultiplexer.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/network-protocol-evolution/java/src/test/java/network/ProtocolMultiplexerTest.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/network-protocol-evolution/python/src/protocol_multiplexer.py` | tested | Same-language test suite present. |
| `03-hld-concepts/nosql-databases/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/nosql-databases/java/v1-simple/LsmKeyStore.java` | tested | Same-language test suite present. |
| `03-hld-concepts/nosql-databases/python/v1-simple/lsm_key_store.py` | tested | Same-language test suite present. |
| `03-hld-concepts/pacelc-theorem/java/src/PacelcSimulator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/pacelc-theorem/python/pacelc_simulator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/pattern-selection/java/ConsistencyLevel.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/pattern-selection/java/PatternEvaluator.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/pattern-selection/java/PatternEvaluatorTest.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/pattern-selection/java/SystemRequirements.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/pattern-selection/python/pattern_evaluator.py` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/pattern-selection/python/test_pattern_evaluator.py` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/postgresql/java/v1-simple/PostgresReadWritePlanner.java` | tested | Same-language test suite present. |
| `03-hld-concepts/postgresql/python/v1-simple/postgres_read_write_planner.py` | tested | Same-language test suite present. |
| `03-hld-concepts/rate-limiting/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/rate-limiting/java/v1-simple/TokenBucketRateLimiter.java` | tested | Same-language test suite present. |
| `03-hld-concepts/rate-limiting/java/v2-realistic/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/rate-limiting/java/v2-realistic/SlidingWindowRateLimiter.java` | tested | Same-language test suite present. |
| `03-hld-concepts/rate-limiting/java/v3-production/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/rate-limiting/java/v3-production/DistributedRateLimiter.java` | tested | Same-language test suite present. |
| `03-hld-concepts/rate-limiting/python/v1-simple/token_bucket.py` | tested | Same-language test suite present. |
| `03-hld-concepts/rate-limiting/python/v2-realistic/sliding_window.py` | tested | Same-language test suite present. |
| `03-hld-concepts/rate-limiting/python/v3-production/distributed_limiter.py` | tested | Same-language test suite present. |
| `03-hld-concepts/read-scaling/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/read-scaling/java/v1-simple/ReadReplicaRouter.java` | tested | Same-language test suite present. |
| `03-hld-concepts/read-scaling/python/v1-simple/read_replica_router.py` | tested | Same-language test suite present. |
| `03-hld-concepts/real-time-updates/java/v1-simple/RealtimeChannelSelector.java` | tested | Same-language test suite present. |
| `03-hld-concepts/real-time-updates/java/v2-realistic/ConnectionRegistry.java` | tested | Same-language test suite present. |
| `03-hld-concepts/real-time-updates/java/v3-production/RealtimeUpdateCoordinator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/real-time-updates/python/v1-simple/realtime_channel_selector.py` | tested | Same-language test suite present. |
| `03-hld-concepts/real-time-updates/python/v2-realistic/connection_registry.py` | tested | Same-language test suite present. |
| `03-hld-concepts/real-time-updates/python/v3-production/distributed_realtime_router.py` | tested | Same-language test suite present. |
| `03-hld-concepts/redis/java/v1-simple/SimpleRedisCache.java` | tested | Same-language test suite present. |
| `03-hld-concepts/redis/python/v1-simple/simple_redis_cache.py` | tested | Same-language test suite present. |
| `03-hld-concepts/relational-databases/java/v1-simple/BPlusTreeIndex.java` | tested | Same-language test suite present. |
| `03-hld-concepts/relational-databases/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/relational-databases/python/v1-simple/b_plus_tree_index.py` | tested | Same-language test suite present. |
| `03-hld-concepts/resilience-patterns/java/src/main/java/resilience/ResilienceOrchestrator.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/resilience-patterns/java/src/test/java/resilience/ResilienceOrchestratorTest.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/resilience-patterns/python/src/resilience_orchestrator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/search-systems/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/search-systems/java/v1-simple/InvertedIndexSearch.java` | tested | Same-language test suite present. |
| `03-hld-concepts/search-systems/python/v1-simple/inverted_index_search.py` | tested | Same-language test suite present. |
| `03-hld-concepts/service-discovery/java/v1-simple/SimpleServiceRegistry.java` | tested | Same-language test suite present. |
| `03-hld-concepts/service-discovery/java/v2-realistic/HealthCheckRegistry.java` | tested | Same-language test suite present. |
| `03-hld-concepts/service-discovery/java/v3-production/DynamicServiceRegistry.java` | tested | Same-language test suite present. |
| `03-hld-concepts/service-discovery/python/v1-simple/simple_registry.py` | tested | Same-language test suite present. |
| `03-hld-concepts/service-discovery/python/v2-realistic/health_check_registry.py` | tested | Same-language test suite present. |
| `03-hld-concepts/service-discovery/python/v3-production/dynamic_registry.py` | tested | Same-language test suite present. |
| `03-hld-concepts/sql-fundamentals/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/sql-fundamentals/java/v1-simple/RelationalQueryEngine.java` | tested | Same-language test suite present. |
| `03-hld-concepts/sql-fundamentals/python/v1-simple/relational_query_engine.py` | tested | Same-language test suite present. |
| `03-hld-concepts/sql-vs-nosql/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/sql-vs-nosql/java/v1-simple/StoreSelector.java` | tested | Same-language test suite present. |
| `03-hld-concepts/sql-vs-nosql/python/v1-simple/store_selector.py` | tested | Same-language test suite present. |
| `03-hld-concepts/storage-engine-internals/java/src/main/java/storage/MiniLsmEngine.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/storage-engine-internals/java/src/test/java/storage/MiniLsmEngineTest.java` | illustrative-only | No same-language test suite present. |
| `03-hld-concepts/storage-engine-internals/python/storage/mini_lsm_engine.py` | tested | Same-language test suite present. |
| `03-hld-concepts/stream-processing/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/stream-processing/java/v1-simple/SlidingWindowAggregator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/stream-processing/python/v1-simple/demo.py` | tested | Same-language test suite present. |
| `03-hld-concepts/stream-processing/python/v1-simple/sliding_window_aggregator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/time-series-databases/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/time-series-databases/java/v1-simple/TimeSeriesDownsampler.java` | tested | Same-language test suite present. |
| `03-hld-concepts/time-series-databases/python/v1-simple/time_series_downsampler.py` | tested | Same-language test suite present. |
| `03-hld-concepts/websockets/java/v1-simple/ConnectionManager.java` | tested | Same-language test suite present. |
| `03-hld-concepts/websockets/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/websockets/python/v1-simple/connection_manager.py` | tested | Same-language test suite present. |
| `03-hld-concepts/workflow-orchestration/java/v1-simple/SagaStepRunner.java` | tested | Same-language test suite present. |
| `03-hld-concepts/workflow-orchestration/java/v2-realistic/WorkflowStateMachine.java` | tested | Same-language test suite present. |
| `03-hld-concepts/workflow-orchestration/java/v3-production/DurableWorkflowOrchestrator.java` | tested | Same-language test suite present. |
| `03-hld-concepts/workflow-orchestration/java/v3-production/JobOrchestrationMotif.java` | tested | Same-language test suite present. |
| `03-hld-concepts/workflow-orchestration/java/v3-production/PaymentOrchestrationMotif.java` | tested | Same-language test suite present. |
| `03-hld-concepts/workflow-orchestration/python/v1-simple/saga_step_runner.py` | tested | Same-language test suite present. |
| `03-hld-concepts/workflow-orchestration/python/v2-realistic/workflow_state_machine.py` | tested | Same-language test suite present. |
| `03-hld-concepts/workflow-orchestration/python/v3-distributed/job_orchestration_motif.py` | tested | Same-language test suite present. |
| `03-hld-concepts/workflow-orchestration/python/v3-distributed/payment_orchestration_motif.py` | tested | Same-language test suite present. |
| `03-hld-concepts/workflow-orchestration/python/v3-production/durable_workflow_orchestrator.py` | tested | Same-language test suite present. |
| `03-hld-concepts/write-scaling/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/write-scaling/java/v1-simple/WriteBatcher.java` | tested | Same-language test suite present. |
| `03-hld-concepts/write-scaling/python/v1-simple/write_batcher.py` | tested | Same-language test suite present. |
| `03-hld-concepts/zookeeper/java/v1-simple/Demo.java` | tested | Same-language test suite present. |
| `03-hld-concepts/zookeeper/java/v1-simple/ZkLeaderElector.java` | tested | Same-language test suite present. |
| `03-hld-concepts/zookeeper/python/v1-simple/zk_leader_elector.py` | tested | Same-language test suite present. |
| `06-genai-systems/00-concepts/vector-databases/python/v1-basic/simple_vector_store.py` | tested | Same-language test suite present. |
