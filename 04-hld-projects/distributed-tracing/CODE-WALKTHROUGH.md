# Code Walkthrough: Distributed Tracing Simulator

This document outlines how the in-memory implementations (`v1-basic`) reflect the architecture and failure traces described in `DESIGN.md`. Both Java and Python versions achieve full behavioral parity without using external frameworks, package managers, or non-standard libraries.

## 1. Tail-Based Sampling

The `TailSampler` module acts as the "Ingestion Worker" from the design doc. Rather than sampling head-based (random 1% at the edge), it uses tail-based sampling by collecting incoming spans into memory buffers partitioned by `traceId` (a dictionary/map). It evaluates the entire trace when `evaluateWindow` is called.

If a trace contains an error (`span.isError()`) or exceeds the latency threshold (e.g., > 1 second duration), the entire trace is preserved and returned. Otherwise, it is dropped.

## 2. Trace DAG Assembly

To reconstruct parent-child relationships before storage, the `DAGAssembler` module processes lists of spans. It iterates through them, connecting spans with a `parentSpanId` to their respective parent nodes. Spans without a `parentSpanId`, or those whose parent is missing from the list (fragmented traces), are pushed into the root list.

## 3. Failure Trace Implementation

The core design documentation includes an explicit failure trace:

**Ingestion Worker Crash:**
> A worker applying tail-based sampling crashes. Some in-memory span buffers (tail sampling state) may be lost, leading to dropped or fragmented traces during the short crash window.

This is implemented via the `.crash()` method in the `TailSampler` module. Invoking `.crash()` clears the local buffer map. The tests (`testIngestionWorkerCrash_LosesInMemorySpans` / `test_ingestion_worker_crash_loses_in_memory_spans`) demonstrate this by ingesting a slow trace and calling `.crash()`, verifying that the spans are effectively lost and an empty list is evaluated instead.
