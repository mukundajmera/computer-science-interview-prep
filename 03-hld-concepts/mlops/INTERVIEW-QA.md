# Interview Questions: MLOps

Covers the folder's pages on [real-time feature store architecture](feature-store-architecture.md) and [LLM inference serving](model-inference-serving.md).

## Core Concepts

### 1. Why does an ML platform need a feature store at all?
**Q**: Teams already have data warehouses and Redis. What breaks without a dedicated feature store?
**A**: Without a feature store, every team re-implements feature logic, and the code that computes a feature for training quietly diverges from the code that computes it in production. That training-serving skew is one of the most common causes of models that look great offline and disappoint live. A feature store centralizes feature definitions so the exact same logic feeds both training and inference, and it makes features discoverable and reusable across teams. The trade-off is platform complexity: you adopt another critical system and force teams into its data model. Follow-up: how would you detect training-serving skew in practice?

### 2. Why split the feature store into online and offline layers?
**Q**: Why not serve both training and inference from one database?
**A**: The two workloads have irreconcilable access patterns. Training scans billions of historical rows and wants cheap, high-throughput batch storage, which data lakes and warehouses (Hive, Snowflake, BigQuery) provide. Real-time inference reads a handful of the newest values per request with millisecond latency, which calls for an in-memory or low-latency key-value store like Redis, DynamoDB, or Cassandra. One system optimized for both would be mediocre at each. The cost of the split is a synchronization problem: keeping the online store fresh and consistent with the offline one becomes its own pipeline.

### 3. What is point-in-time correctness, and what goes wrong without it?
**Q**: When you assemble a training set, why can't you just join the latest feature values onto historical events?
**A**: Joining current values onto past events leaks the future into training: the model sees information that would not have existed at prediction time. Point-in-time correctness means every training example carries only feature values as of the event's timestamp, such as the state of the world at 2:00 PM for a 2:00 PM transaction. Without it, offline evaluation is over-optimistic and the model fails against live, forward-facing data. This is why the [feature store page](feature-store-architecture.md) treats the temporal join ("time-travel") as a first-class feature rather than an implementation detail. Follow-up: what does this imply for how late-arriving data is handled?

### 4. How would you serve features for a real-time fraud model at checkout latency?
**Q**: Walk through the serving path when a transaction arrives and the model needs user and session features in single-digit milliseconds.
**A**: The request hits the online store, a key-value lookup keyed by entities like user ID and card ID, backed by something like Redis or DynamoDB. A streaming pipeline continuously materializes fresh feature values (recent clicks, session counters) into that store so reads are simple key fetches, not computations. Anything not pre-computed must be derivable from the request payload itself, because you cannot afford a warehouse query in the hot path. The trade-off is staleness: online values are only as fresh as the materialization pipeline, so you tune that pipeline's latency against infrastructure cost.

### 5. Feast vs Hopsworks: how do you evaluate feature store platforms?
**Q**: An interviewer asks you to pick a feature store. What axes do you compare on?
**A**: Feast is deliberately a serving and management layer: it registers, discovers, and serves features on top of infrastructure you already have, which lowers adoption cost but leaves feature engineering and monitoring to you. Hopsworks is an end-to-end platform with feature engineering, data-quality monitoring, and access control built in, which is more capability for more operational and conceptual weight. The honest answer is that the choice follows organizational shape: existing data platform and strong data engineering favors Feast's integration model; a greenfield team wanting one coherent system favors Hopsworks. Follow-up: what would make you build instead of buy?

### 6. Why is LLM inference memory-bound, and what is the KV cache?
**Q**: During text generation, where does the time and memory actually go?
**A**: Generation is auto-regressive: after a prefill phase that processes the whole prompt at once, tokens are produced one at a time, and each new token's attention needs the Keys and Values of every previous token. Recomputing those tensors per step would be wasteful, so engines cache them as the KV cache. The cache grows linearly with sequence length, so long contexts and large batches are bounded by memory capacity and memory bandwidth, not by raw compute. That is why the [inference serving page](model-inference-serving.md) calls KV cache management the dominant bottleneck at scale.

### 7. How do you estimate KV cache memory for a model?
**Q**: Give the formula and apply it to a 70B-class model.
**A**: Memory per token is `2 * Layers * Heads * Head Dimension * Precision Bytes`, where the factor of 2 covers the Key and Value matrices. For LLaMA 2 70B (80 layers, 64 heads, head dimension 128, 16-bit precision) that is `2 * 80 * 64 * 128 * 2 = 2.6 MB per token` per request. A batch of 128 requests averaging 2,048 tokens then needs roughly 681 GB of GPU memory just for KV cache, far beyond a single A100's 80 GB. Being able to run this math in an interview shows you understand why batch size, context length, and GPU count trade off against each other.

### 8. What does continuous batching fix that static batching cannot?
**Q**: Both process requests in batches, so why did ORCA's approach matter?
**A**: Static batching holds the whole batch hostage to its longest request: short requests finish early but keep occupying GPU slots until the longest sequence completes, wasting utilization. Continuous batching (iteration-level scheduling) re-evaluates the batch at every token step, evicting completed requests and injecting new arrivals immediately. That keeps the effective batch size high and constant, lifting throughput substantially without hurting per-request latency. The trade-off is scheduler complexity at each iteration, which is cheap compared to idle GPUs. Follow-up: what new fairness or starvation questions does per-iteration scheduling raise?

### 9. What problem does PagedAttention solve, and how?
**Q**: vLLM borrowed an idea from operating systems. Which one, and why?
**A**: Traditional engines pre-allocate one contiguous KV cache block sized for the maximum possible sequence length, which wastes memory two ways: internal fragmentation from reserved-but-unused space, and external fragmentation from unusable gaps between blocks, leaving utilization as low as 20 to 40 percent. PagedAttention applies virtual-memory paging: the KV cache is split into fixed-size blocks stored non-contiguously, with a block table mapping logical token positions to physical blocks, so memory is allocated on demand one block at a time. Uniform block size removes internal fragmentation and largely tames external fragmentation, pushing utilization above 90 percent. A bonus is that identical prefix blocks can be shared across sequences, which makes beam search and parallel sampling far cheaper. Follow-up: what does the block table cost in lookup overhead, and why is it negligible here?
