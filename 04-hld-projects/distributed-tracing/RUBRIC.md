# Interview Rubric: Distributed Tracing

## 1. Requirements Handling
- **Weak:** Just says "store logs".
- **Strong:** Identifies the write-heavy nature, the need for context propagation (Trace ID / Span ID), and sampling requirements.

## 2. Architecture & Patterns
- **Weak:** Direct synchronous writes from apps to a database.
- **Strong:** Uses local sidecars/agents for batching, Kafka for buffering, and columnar storage.

## 3. Sampling Knowledge
- **Weak:** Doesn't understand how to reduce data volume.
- **Strong:** Clearly articulates the difference, pros, and cons of Head-based vs Tail-based sampling. Understands that tail-based sampling requires stateful processing/buffering.

## 4. Context Propagation
- **Weak:** Mentions passing "an ID".
- **Strong:** References standard protocols (W3C Trace Context) and understands how parent-child relationships form a DAG.

## 5. Failure & Bottleneck Handling
- **Weak:** Ignores what happens when the DB is slow.
- **Strong:** Uses Kafka as a shock absorber. Discusses how to handle agent failures (UDP vs TCP trade-offs locally).
