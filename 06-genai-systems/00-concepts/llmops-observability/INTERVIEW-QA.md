# LLMOps and Observability: Interview Q&A

## 1. What is the primary purpose of OpenTelemetry (OTel) in an LLM application?
OTel provides a standardized way to instrument, generate, collect, and export telemetry data (metrics, logs, and traces). In LLM apps, it is critical for tracing complex execution chains (like LangChain or LlamaIndex), recording exact token counts, and measuring granular latencies such as Time to First Token (TTFT).

## 2. How do you handle PII redaction without breaking the context of an LLM prompt?
Redaction should ideally happen asynchronously before logging to the observability platform, rather than modifying the prompt sent to the LLM (unless security policies strictly forbid PII hitting the provider). If redaction must occur before generation, using consistent hashing or placeholder replacement (e.g., replacing 'John' with '[USER_NAME_1]') preserves the semantic structure of the prompt.

## 3. Explain the concept of a prompt registry and its benefits.
A prompt registry is a centralized, version-controlled repository for prompt templates. It decouples prompt engineering from application code deployments, enabling dynamic A/B testing, rapid iteration by non-engineers, and strict tracking of which prompt version generated a specific output.

## 4. How would you implement evaluation in a CI/CD pipeline for LLMs?
I would integrate an automated evaluation step that triggers on pull requests. The pipeline would load a 'golden dataset' of inputs, generate outputs using the proposed code/prompt changes, and score them using an 'LLM-as-a-judge' approach or deterministic metrics (like ROUGE for summarization). If the aggregate score falls below the main branch baseline, the regression gate fails the build.

## 5. What is the difference between a shadow deployment and a canary deployment in LLMOps?
A shadow deployment routes a copy of live traffic to the new model version, logging the outputs for offline comparison without returning them to the user (zero risk to user experience). A canary deployment routes a small percentage (e.g., 5%) of live traffic to the new version, returning the responses to users and monitoring metrics to ensure stability before a full rollout.

## 6. How do you monitor for model drift in proprietary LLMs (e.g., GPT-4)?
Since weights are hidden, drift must be monitored observationally. Key metrics include tracking average output token lengths, failure rates of JSON schema adherence, and changes in the semantic distribution of outputs (measured by embedding outputs over time and checking for clustering shifts).

## 7. How do you attribute costs in a multi-tenant LLM application?
Cost attribution requires injecting a `tenant_id` into the tracing context of every request. An API gateway or interceptor tracks the exact `prompt_tokens` and `completion_tokens` returned by the provider, multiplies them by the specific model's pricing, and aggregates these costs grouped by `tenant_id` in the observability backend.

## 8. What mechanisms prevent a single tenant from exhausting the cost budget?
We implement strict budget quotas at the gateway layer. A real-time counter tracks the accumulated cost for each tenant. Once a daily or monthly budget threshold is hit, the gateway immediately rejects subsequent requests with a `429 Too Many Requests` or `402 Payment Required` status, preventing further API calls to the provider.

## 9. Describe how to mitigate noisy-neighbour problems in shared LLM deployments.
To prevent one tenant's massive batch jobs from starving others, the gateway must implement fair queuing algorithms. Alternatively, high-volume enterprise tenants can be routed to dedicated, provisioned throughput endpoints, while standard tenants share a pay-as-you-go pool, physically isolating the workloads.

## 10. How do you architect provider failover when an LLM API goes down?
The gateway is configured with a primary (e.g., OpenAI) and secondary (e.g., Anthropic) provider. On detecting a timeout or `50x` error, the gateway intercepts the failure. Crucially, it must translate the prompt into the secondary provider's required format and recalculate token limits using the secondary's tokenizer before executing the failover request.

## 11. What retry strategies are appropriate for LLM rate limits (429 errors)?
Standard retries can cause thundering herd issues. We use exponential backoff (increasing the wait time between retries) combined with jitter (adding a randomized duration to the backoff). This spreads out the retry attempts and gives the provider's rate limit buckets time to replenish.

## 12. What are typical Service Level Objectives (SLOs) for generative AI features?
Typical SLOs include Availability (e.g., 99.9% successful generations), Latency (e.g., p95 Time to First Token < 1.5 seconds, which is crucial for streaming UX), and Quality (e.g., < 1% critical hallucination rate, measured asynchronously via sampled evaluations).

## 13. How does a semantic cache impact the arithmetic of monthly LLM costs?
A semantic cache stores previous query/response pairs and serves them for similar incoming queries without calling the LLM. If the baseline cost for 1M requests is $35,000, a 20% cache hit rate eliminates the LLM provider cost for 200,000 requests. The arithmetic is simple: Total Cost = (Total Requests * (1 - Hit Rate)) * Cost Per Request, resulting in significant, linear cost savings.

## 14. Why is Time to First Token (TTFT) preferred over total generation time in observability?
For streaming applications, TTFT directly correlates with user perceived latency. A user sees the UI update immediately upon the first token, making a 5-second total generation time acceptable if the TTFT is under 1 second. Total generation time is highly dependent on output length, making it a noisy metric for diagnosing system responsiveness.

## 15. What are the regression gate considerations when setting temperature > 0 in CI?
If temperature > 0, outputs are non-deterministic, leading to flaky CI runs where tests pass and fail randomly on the same code. To handle this, CI regression gates should either force `temperature=0` for reproducibility, or if testing creative variance is required, use a large statistical sample (n > 100) and check if the mean evaluation score falls within an acceptable confidence interval.
