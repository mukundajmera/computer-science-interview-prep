# AI Coding Copilot - Common Pitfalls

## Common pitfalls

1. **Flawed Keystroke Debouncing (e.g., 300ms vs 30-50ms)**
   - Designing the system such that every keystroke in the IDE instantly triggers an API call to the backend model, without any client-side delay.
   - Alternatively, using a debounce time that is too long (like 300ms), which introduces unacceptable typing lag for inline completions.
   - Forgetting to cancel in-flight requests if the user continues typing after a request was sent.

2. **Relying on Remote Server-Side Caching for Completions**
   - Using a remote Redis cache for exact prefix+suffix matches. Remote keystroke caching has a <2% hit rate and adds a wasteful 10-15ms network hop to the critical latency budget.

3. **Using the Same Model for Inline and Chat**
   - Routing both fast inline ghost-text completions and complex chat-based queries to the same large model (e.g., GPT-4o or Claude 3.5 Sonnet).

4. **Poor Context Window Management**
   - Sending the entire codebase or just the current file blindly to the model without prioritizing relevant chunks, or exceeding the model's context window.
   - Using plain prefix completion rather than Fill-in-the-Middle (FIM) prompt formatting (`<|fim_prefix|>`, `<|fim_suffix|>`, `<|fim_middle|>`).

5. **Missing Post-Generation Safety and License Checks**
   - Assuming the LLM's output is safe to render immediately to the user, without verifying compliance or correctness.
   - Not having a fast license check (e.g., using a Bloom filter) to prevent verbatim reproduction of copyrighted code.

6. **Focusing Only on Server-Side Latency**
   - Optimizing the backend services and model inference time but ignoring the network round-trip time (RTT) from the user's IDE to the server.

7. **Incorrect Quality and Telemetry Metrics**
   - Measuring system success solely by backend metrics like QPS, server latency, or model tokens/second.
   - Failing to track user-centric quality metrics like Acceptance Rate or Persistence Rate.

## Why these fail interviews

- **Cost, Scale, and UX Failures:** Firing an API call on every keystroke will overwhelm the backend, spike costs astronomically, and return outdated completions. Conversely, a 300ms debounce makes the editor feel broken and laggy. Trailing-edge 30-50ms debouncing eliminates fast typing bursts while maintaining instant feel.
- **Wasted Network Hops:** Using a remote cache for exact keystroke matches penalizes every request with an extra network hop (e.g., 10-15ms) for a negligible <2% hit rate, blowing the strict latency budget.
- **Latency Budget Blown:** Using a massive model like GPT-4o for inline completions will never meet the strict <300ms latency budget. Ignoring network RTT means a user far from the server will experience terrible lag.
- **Context Blindness:** Just sending the current file isn't enough for good suggestions. Just saying "we use RAG" is usually too slow for inline completion. Context gathering must rely on fast heuristics built into the IDE extension.
- **Legal and Security Risks:** License compliance is a massive legal risk for Copilot-like products. Not scanning for vulnerabilities or copyrighted code shows a lack of production readiness.
- **Misaligned Product Understanding:** Acceptance rate is the North Star metric for a coding copilot. If you don't track whether the user actually accepted and kept the code, you aren't measuring the product's actual value.

## Mitigations

1. **Implement Trailing-Edge Client-Side Debouncing:** Add a realistic 30-50ms client-side delay in the IDE extension before firing a request. Cancel in-flight requests on new keystrokes to prevent laggy responses.
2. **Use a Dual-Path Architecture:** Route inline completions to a small, fast model (e.g., Codestral, GPT-4o-mini) and chat queries to a larger, more capable model.
3. **Structured Context Ranking:** Break down the token budget (e.g., 50% for current file, 30% for imported files, 20% for project structure) and use fast heuristics to rank relevant code chunks. Use FIM prompt formatting.
4. **Post-Generation Safety Pipeline:** Implement a fast Bloom filter check (< 1ms) for known copyrighted code snippets (> 50 tokens) and run a quick security scanner for obvious vulnerabilities before returning the suggestion.
5. **Optimize Network Path & Cache Locally:** Propose multi-region deployments or edge computing to reduce network RTT. Replace remote server-side caching with an in-IDE local client-side LRU prefix tree completion cache (e.g., completions for 'def cal' are reused when the user types 'c' to 'def calc').
6. **Track User-Centric Metrics:** Setup a non-blocking telemetry pipeline to track Acceptance Rate (>30% target), Persistence Rate (is the code still there after 30s?), and Keystrokes Saved.

## Cross-links

- [Problem Statement](./PROBLEM.md)
- [System Design Approach](./APPROACH.md)
- [Detailed Design](./DESIGN.md)
- [Interview Guide](./INTERVIEW-GUIDE.md)
