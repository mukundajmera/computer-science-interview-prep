# Monitoring & Observability

## What is it?

Observability is the ability to understand the internal state of a system by examining its external outputs (metrics, logs, traces).

## Why do we need it?

**Problem**: In distributed systems, failures are complex and debugging is hard.

**Solution**: Collect and correlate metrics, logs, and traces to understand system behavior.

## Three Pillars

### 1. Metrics
- Numeric measurements over time
- Examples: CPU, memory, request rate, latency percentiles
- Tools: Prometheus, Datadog, CloudWatch
- **Storage**: Time-series databases (InfluxDB, Prometheus, TimescaleDB)

### 2. Logs
- Timestamped event records
- Examples: Error messages, request details
- Tools: ELK Stack, Splunk, Loki

### 3. Traces
- Request flow through distributed system
- Examples: Service-to-service calls, latency breakdown
- Tools: Jaeger, Zipkin, AWS X-Ray

## Time-Series Databases for Metrics

Metrics are fundamentally **time-series data** - measurements indexed by timestamp. Specialized time-series databases optimize for this workload:

### Why Time-Series Databases?

| Feature | Time-Series DB | General-Purpose DB |
|---------|---------------|-------------------|
| **Write pattern** | Append-only, high throughput | Mixed read/write |
| **Compression** | 10-20× (delta encoding, Gorilla) | 2-3× (generic compression) |
| **Query pattern** | Range queries over time | Random access |
| **Retention** | Automated downsampling | Manual archival |
| **Performance** | Optimized for time-range queries | General-purpose indexes |

### Popular Time-Series Databases

**1. Prometheus**
```
Architecture:
├─ Pull-based metric collection (scraping)
├─ Local time-series database
├─ PromQL query language
└─ Built-in alerting (Alertmanager)

Use case: Kubernetes monitoring, microservices metrics
Example: Service latency, request rates, error rates

Query:
rate(http_requests_total[5m])  # Requests per second over 5 minutes
```

**2. InfluxDB**
```
Architecture:
├─ Push-based (write via HTTP/UDP)
├─ Time-series database with SQL-like query language
├─ Retention policies for automatic data expiration
└─ Continuous queries for downsampling

Use case: IoT sensor data, application metrics
Example: Temperature sensors, stock prices

Query:
SELECT mean("temperature") FROM "sensors"
WHERE time > now() - 1h
GROUP BY time(10m)
```

**3. TimescaleDB**
```
Architecture:
├─ PostgreSQL extension
├─ Automatic time-based partitioning (hypertables)
├─ Full SQL support
└─ Compression and continuous aggregates

Use case: Teams already using PostgreSQL, need SQL compatibility
Example: Application logs, financial data

Query:
SELECT time_bucket('5 minutes', time) AS bucket,
       avg(cpu_usage)
FROM metrics
WHERE time > now() - interval '1 hour'
GROUP BY bucket;
```

### When to Use Time-Series Databases

✅ **Use for:**
- **Metrics storage**: CPU, memory, request counts over time
- **IoT sensor data**: Temperature, pressure readings
- **Financial data**: Stock prices, trading volumes
- **Infrastructure monitoring**: System performance over time
- **APM (Application Performance Monitoring)**: Latency, throughput

**Example monitoring stack:**
```
Application → Prometheus (metrics) → Grafana (visualization)
           → Loki (logs)
           → Jaeger (traces)

Prometheus uses a time-series database for metrics; Loki and Jaeger use specialized backends for logs and traces
```

❌ **Don't use for:**
- Transactional data (use PostgreSQL, MySQL)
- Document storage (use MongoDB, Elasticsearch)
- Graph relationships (use Neo4j)
- Ad-hoc queries on diverse data (use data warehouses)

### Real-world Examples

**Netflix:**
- Atlas: Custom time-series database
- Handles 2 billion+ metrics per minute
- Powers observability at scale

**Uber:**
- M3: Open-source time-series database
- Multi-datacenter replication
- 500M+ metrics per second

**Datadog:**
- Custom time-series database
- Stores customer metrics at massive scale
- Automated retention and downsampling

### Time-Series Optimization Techniques

**1. Compression**
```
Gorilla compression (Facebook):
- Delta-of-deltas encoding
- XOR-based value compression
- 10-20× reduction in storage

Example:
Timestamps: 1000, 1001, 1002, 1003 → Store: 1000, +1, +1, +1
Values: 100.5, 100.7, 100.9 → XOR differences
```

**2. Downsampling**
```
Raw metrics (1-second resolution):
├─ Keep for 7 days
└─ After 7 days → Downsample to 1-minute averages

Downsampled (1-minute resolution):
├─ Keep for 30 days
└─ After 30 days → Downsample to 1-hour averages

Long-term (1-hour resolution):
└─ Keep for 1 year

Saves 99%+ storage while preserving trends
```

**3. Partitioning**
```
TimescaleDB hypertables:
├─ Automatic time-based partitioning
├─ Query planner skips irrelevant partitions
└─ Old partitions dropped efficiently

Example:
Partition 2024-03-01 (can be dropped atomically)
Partition 2024-03-02 (current)
Partition 2024-03-03 (pre-created)
```

**Cross-reference:** See [Big Data Structures](../../00-theory/data-structures/big-data-structures.md) for time-series data structures like LSM trees used in many time-series databases.

---

## Key Concepts

### SLI/SLO/SLA
- **SLI** (Indicator): Measured metric (e.g., latency p99)
- **SLO** (Objective): Target value (e.g., p99 < 200ms)
- **SLA** (Agreement): Contract with consequences

### Four Golden Signals
1. **Latency**: Request duration
2. **Traffic**: Request rate
3. **Errors**: Failure rate
4. **Saturation**: Resource utilization


## Performance Analysis & Load Testing Validity

Understanding how to measure, interpret, and validate system performance is critical before making any performance claims. Measurements from load testing can be deeply misleading if the methodology is flawed.

### Little's Law and Steady-State Concurrency

**Little's Law** relates concurrency ($L$), arrival rate ($\lambda$), and average wait time ($W$):
$$ L = \lambda \times W $$

**Worked Example:**
If your system receives $\lambda = 1000$ requests per second, and each request takes $W = 50ms$ (0.05s) to process, the average number of concurrent requests in the system is:
$$ L = 1000 \times 0.05 = 50 \text{ concurrent requests} $$

**When Little's Law Cannot Be Naively Applied:**
Little's Law assumes a **stable, steady-state system** where arrival rate equals departure rate. It breaks down when:
- The system is saturated (arrival rate > processing rate).
- The system is experiencing unbound queue growth (requests are piling up).
- The system is in transient states (e.g., during startup or sudden traffic spikes).
Near saturation, queue lengths and latency grow non-linearly, and Little's Law will under-predict actual queue sizes.

### Percentile Math: Non-Additivity and Tail Fan-out

A common mistake in performance analysis is treating percentiles like averages. **Percentiles are not additive.**

- **Sum of p99s $\neq$ End-to-End p99:** If Service A has a p99 latency of 100ms and Service B has a p99 latency of 200ms, the end-to-end p99 of calling A then B is *not* 300ms. The p99 request for A is highly unlikely to be the exact same request that hits the p99 latency in B. The actual end-to-end p99 is usually much lower than the sum of component p99s.
- **Percentiles cannot be averaged:** If you have two shards, one with a p99 of 10ms (100 requests) and one with a p99 of 50ms (10,000 requests), the global p99 is not (10+50)/2 = 30ms. It must be computed from the merged raw dataset or using specialized data structures like T-Digest or HDRHistogram.

**Fan-out Tail Effects:**
When a single user request fans out to multiple backend nodes (e.g., scatter-gather in a microservices architecture), the probability of hitting a tail latency increases dramatically.
If you call 10 downstream services in parallel, and each has a 1% chance of being slow (p99), the probability that *at least one* is slow is:
$$ 1 - (0.99)^{10} \approx 0.0956 \text{ or } 9.5\% $$
A 1% tail latency for a component becomes a ~9.5% tail latency for the end-to-end request.

### Open-Loop vs. Closed-Loop Testing

How you generate load fundamentally alters the results.

- **Closed-Loop Testing (Wait-for-Response):** The load generator runs $N$ threads. Each thread sends a request, waits for the response, and then sends the next request. Concurrency is fixed. If the server slows down, the *arrival rate* drops. This models systems with backpressure (e.g., maxing out connection pools) but completely fails to model the public internet.
- **Open-Loop Testing (Arrival Schedule):** The load generator sends requests at a fixed schedule (e.g., 100 requests/sec) regardless of how fast the server responds. If the server slows down, requests queue up and concurrency increases. This accurately models independent users hitting a website.

### Coordinated Omission

**Coordinated omission** is a severe measurement artifact in closed-loop load testers where the measuring tool inadvertently coordinates with the system under test to hide stalls.

**Worked Example (10ms arrival / 1000ms stall):**
Suppose you configure a load tester to generate 100 requests per second (1 request every 10ms).
1. The system normally responds in 1ms.
2. The system pauses for a 1000ms (1 second) GC pause.
3. In a correct **open-loop** world, 100 requests arrive during this stall. They queue up. The first waits 1000ms, the next 990ms, etc. You record 100 very slow requests.
4. In a flawed **closed-loop** tester, the single thread sends a request, hits the 1000ms stall, and *waits*. It cannot send the other 99 requests. After 1000ms, it records exactly *one* 1000ms latency, then resumes fast 1ms requests.

**Result:** The closed-loop tester recorded 1 slow request instead of 100. The stall is statistically erased from the latency histogram (coordinated omission), leading to falsely optimistic p99 claims.

### Staff Extension: Credible Benchmark Metrics

Before accepting any performance claim, a credible benchmark must explicitly detail:
1. **Achieved Rate vs. Target Rate:** Did the load generator actually sustain the target throughput, or did it fail to generate enough load?
2. **Admission Errors & Timeouts:** Were requests that timed out or were rejected by rate limiters (e.g., 503s) excluded from the latency calculation? Censoring errors artificially lowers measured latency.
3. **Warmup Phases:** JVM JIT compilation, connection pool initialization, and cache warming take time. Results must distinguish between warmup and steady-state.
4. **Payload & Read/Write Skew:** Were payloads realistic sizes? Was the read/write ratio representative of production (e.g., 99:1 vs 50:50)?
5. **System Metrics:** Benchmark results must include Memory/GC activity and CPU utilization. High throughput is meaningless if the system was one GC cycle away from OOM.

## Trade-offs

| Aspect | Trade-off |
|--------|-----------|
| **Granularity** | More detail = more storage cost |
| **Sampling** | Lower cost = less visibility |
| **Cardinality** | More labels = more memory |
| **Retention** | Longer = more storage |

## Key Takeaways

1. **Instrument everything**: Metrics from day one
2. **Correlate signals**: Link logs, metrics, traces
3. **Set meaningful SLOs**: Based on user experience
4. **Alert on symptoms**: Not just causes
5. **Avoid alert fatigue**: Only actionable alerts

---

## GenAI Notes

Observability in LLM-powered systems extends the three pillars with GenAI-specific signals:

| GenAI Observability Pattern | Description | Why It Matters |
|----------------------------|-------------|----------------|
| **Prompt/response tracing** | Log full prompts, completions, and token counts as structured traces | Debug hallucinations, understand cost drivers, and build evaluation datasets |
| **LLM-specific metrics** | Track tokens/sec, time-to-first-token (TTFT), cost-per-query, cache hit rate | Traditional latency/throughput metrics miss the nuances of LLM serving |
| **Evaluation dashboards** | Aggregate offline and online eval scores (faithfulness, relevance, safety) | Go beyond uptime—measure whether the model is actually helpful and safe |
| **Drift detection** | Monitor embedding distribution shift and answer quality over time | Model and data drift cause silent degradation in retrieval and generation quality |
| **Safety audit logs** | Record all safety filter triggers, PII detections, and human escalations | Compliance, incident response, and red-team analysis require full audit trails |

**Key differences from classical observability:**
- **Cardinality explodes**: Every prompt is unique, so you cannot aggregate by "endpoint" alone; you need semantic grouping or sampling.
- **Evaluation is continuous**: Classical systems alert on errors; LLM systems must continuously evaluate output quality (faithfulness, toxicity) even when there are no errors.
- **Cost is a first-class metric**: A single LLM call can cost cents, making cost-per-query as important as latency.

### Tracing Prompt Flows

In a classical service you trace an HTTP request across microservices. In an LLM system you also trace the **prompt lifecycle** — from user input through safety filters, retrieval, model inference, output filtering, and evaluation scoring.

```
trace_id: abc-123
├── span: api_gateway.receive_request
├── span: safety_filter.input_check
│   ├── attr: injection_score = 0.02
│   └── attr: pii_detected = false
├── span: retrieval_service.vector_search
│   ├── attr: top_k = 5
│   └── attr: relevance_score_avg = 0.87
├── span: prompt_builder.assemble
│   └── attr: total_tokens = 1,420
├── span: llm_inference
│   ├── attr: model = "gpt-4o"
│   ├── attr: tokens_in = 1,420
│   ├── attr: tokens_out = 312
│   ├── attr: time_to_first_token_ms = 180
│   └── attr: total_latency_ms = 1,250
├── span: safety_filter.output_check
│   ├── attr: toxicity_score = 0.01
│   └── attr: pii_detected = false
└── span: response.stream_to_client
    └── attr: total_latency_ms = 1,480
```

This trace lets you answer: *Where did latency come from? Did the safety filter block anything? How many tokens did retrieval contribute? Was the output safe?*

### Model Routing Metrics

When a system routes queries to different models (e.g., cheap model for simple queries, expensive model for complex ones), track routing decisions as first-class metrics:

| Metric | Type | Labels | Purpose |
|--------|------|--------|---------|
| `model_route_total` | counter | `model`, `reason` | How often each model is selected and why |
| `model_route_latency_ms` | histogram | `model` | Compare latency across models |
| `model_route_cost_per_query` | histogram | `model` | Track cost distribution |
| `model_fallback_total` | counter | `from_model`, `to_model` | Detect reliability issues with primary models |
| `model_route_quality_score` | gauge | `model` | Sampled quality comparison across routes |

Example alert: *"Fallback rate from gpt-4o to gpt-4o-mini exceeded 10% in the last hour — investigate primary model availability."*

### Safety-Related Dashboards

A safety dashboard extends the standard four-golden-signals dashboard with LLM-specific panels:

```
┌──────────────────────────────────────────────────────────┐
│  LLM Safety Dashboard (24h rolling)                      │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Safety Filter Triggers                                  │
│  Input blocks:   42 / 50,000 requests  (0.08%)           │
│  Output blocks:   7 / 50,000 responses (0.01%)           │
│  PII detections:  0 ✅                                    │
│                                                          │
│  Attack Success Rate (last red-team run)                 │
│  Prompt Injection  ██░░░░░░░░  2%                        │
│  Jailbreak         ████░░░░░░  6%                        │
│  Data Exfiltration █░░░░░░░░░  1%                        │
│                                                          │
│  Toxicity Trend (7-day)                                  │
│  0.05% ─── 0.04% ─── 0.03% ─── 0.05% ─── 0.04%         │
│                                                          │
│  Model Routing (24h)                                     │
│  gpt-4o:      35%  │  gpt-4o-mini: 60%  │  fallback: 5% │
│                                                          │
│  Cost & Tokens (24h)                                     │
│  Total cost: $142  │  Avg tokens/query: 1,820            │
│                                                          │
│  Quality (sampled, 5% of traffic)                        │
│  Faithfulness: 0.91  │  Relevance: 0.94  │  Trust: 0.92  │
└──────────────────────────────────────────────────────────┘
```

**Alert rules for safety:**

| Alert | Condition | Severity |
|-------|-----------|----------|
| PII leak detected | `pii_leak_count > 0` | Critical (page on-call) |
| Toxicity spike | `toxicity_rate > 1%` over 1h | High |
| ASR regression | `asr > 10%` on nightly red-team run | High |
| Excessive input blocks | `input_block_rate > 5%` over 1h | Medium (may indicate false-positive surge) |
| Cost anomaly | `daily_cost > 2 × 7-day average` | Medium |

> **Deep dive →** [LLM Evaluation](../../06-genai-systems/00-concepts/llm-evaluation/) · [Safety & Governance](../../06-genai-systems/00-concepts/safety-governance/) · [Safety, Evaluation & Governance](../../06-genai-systems/00-concepts/safety-eval/) · [LLM Safety & Eval Platform (HLD)](../../06-genai-systems/02-llm-hld-projects/llm-safety-eval-platform/)
