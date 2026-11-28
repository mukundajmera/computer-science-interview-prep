# Interview Questions: Observability

Covers the folder's page on [distributed tracing and OpenTelemetry](distributed-tracing-opentelemetry.md).

## Core Concepts

### 1. Why do logs fall short in a microservices system?
**Q**: Every service already writes logs. What does distributed tracing add?
**A**: Logs are local: each service records its own view, and stitching a request's journey across dozens of services out of scattered log lines is manual, fragile guesswork. A trace represents one request end to end and is composed of spans, one per unit of work in a service, linked into a DAG by parent-child references. That structure turns "which of these 30 services added the latency" from a log-grep session into a picture you can read. The trade-off is instrumentation and pipeline cost: traces must be generated, propagated, collected, and stored. Follow-up: when are logs still the better tool?

### 2. What is the anatomy of a trace?
**Q**: Define trace and span precisely, and explain how spans relate to each other.
**A**: A trace models a single user request from entry to response. Each span is one operation inside one service, carrying metadata, tags, timestamps, and a reference to its parent span. Those references assemble the spans into a directed acyclic graph that mirrors the request's execution path across services. Because the structure is a DAG rather than a flat list, you can see fan-out, parallelism, and exactly which branch of the call tree burned the time. Follow-up: what does a span's duration hide when the work itself fanned out to children?

### 3. What problem does OpenTelemetry solve?
**Q**: Tracing existed long before OpenTelemetry, so why did the industry converge on it?
**A**: Before OTel, instrumentation was vendor-specific: adopting a tracing backend meant baking its proprietary libraries into every service, and switching backends meant re-instrumenting everything. OpenTelemetry, a CNCF project, standardizes the APIs, SDKs, and collection pipeline for traces, metrics, and logs, so services are instrumented once and telemetry can be exported to Jaeger, Zipkin, or a commercial platform interchangeably. The value is freedom from vendor lock-in at the instrumentation layer, which is the most expensive layer to change. The cost is living with a general-purpose standard that occasionally lags vendor-specific features.

### 4. How does tracing context cross service boundaries?
**Q**: Service A calls service B over HTTP. How does B know which trace its work belongs to?
**A**: The W3C TraceContext standard defines HTTP headers that carry the context. The `traceparent` header holds the global Trace ID, the parent Span ID, and sampling flags, so B can attach its spans to the same trace and record the correct parent. The companion `tracestate` header lets individual vendors pass their own metadata without interfering with the standard fields. Because the format is a W3C standard rather than a vendor invention, services written in different languages with different tracing libraries still assemble into one unified trace, as described on the [tracing page](distributed-tracing-opentelemetry.md).

### 5. Why is sampling necessary, and what are the two fundamental strategies?
**Q**: Why not keep a trace for every request, and what are your options when you cannot?
**A**: At high traffic, tracing everything produces telemetry volumes with punishing storage costs and measurable collection overhead, so systems keep a representative subset. Head-based sampling decides at the start of the request: the first service flips a weighted coin, sets the sampled flag in `traceparent`, and every downstream service honors it. Tail-based sampling waits until the trace completes, buffering all spans (typically in the OpenTelemetry Collector) and deciding based on the whole trace, such as keeping anything with an error span. The core trade-off is efficiency versus completeness: head is cheap but blind, tail is smart but expensive.

### 6. What are the trade-offs of head-based sampling?
**Q**: Head-based sampling is the default in many setups. What do you gain and what do you silently lose?
**A**: You gain simplicity and near-zero overhead: one random decision at the edge, propagated downstream, with no buffering anywhere. You lose any guarantee about *which* traces survive, because the coin flip is ignorant of what the request is about to do. Rare errors and anomalous high-latency requests are discarded at exactly the same rate as boring successes, so the traces you most want during an incident may not exist. For low-stakes traffic profiling that is fine; for debugging production failures it is a real gap. Follow-up: how would you keep 1 percent of successes but all errors?

### 7. When is tail-based sampling worth its cost?
**Q**: Tail-based sampling needs all spans buffered until the trace completes. When does that pay off?
**A**: It pays off when the interesting property of a request is only knowable at the end: whether any span errored, whether total latency crossed a threshold, whether a specific code path ran. Because the decision uses the whole trace, you can keep every error and every outlier while still dropping the bulk of routine traffic, which is precisely the signal-to-noise profile on-call engineers need. The cost is real: memory and CPU for buffering every span in a collector tier, plus architectural complexity and a new scaling concern. In low-traffic or latency-critical edge environments, that cost can exceed the benefit, which is why many systems run head-based at the edge and tail-based only where the traffic justifies it.

### 8. Design: how would you capture all errors while storing only 1 percent of successes?
**Q**: Sketch the sampling architecture for a high-traffic platform with that exact requirement.
**A**: Use head-based sampling at 1 percent as the baseline so a cheap random sample of healthy traffic flows through with minimal overhead. Layer tail-based sampling in the OpenTelemetry Collector for the remaining traffic: buffer spans per trace, and when the trace completes, keep it if any span carries an error status or the latency exceeds a budget, dropping it otherwise. This hybrid gets complete error coverage without paying tail-based storage for every success. The main trade-offs are collector memory sized for peak span throughput and the added latency between a request finishing and its trace becoming queryable. Follow-up: how do you handle traces whose spans arrive out of order or after the buffer window closes?
