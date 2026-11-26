# Web Crawler - Follow-Up Questions

## Follow-up questions
1. How would you add focused crawl scoring for topical relevance without breaking deterministic tests?
2. What is your strategy for JavaScript-rendered pages when the current tests avoid live network dependencies?
3. How do you make crawl state resumable after restart?
4. Which boundaries should become remote services at 10x scale?
5. How would you add robots-policy caching with expiry?

## Variants and extensions
1. Priority frontier based on freshness, depth, or page score.
2. Per-host and global crawl budgets with backpressure.
3. Content fingerprinting for near-duplicate pages.
4. Recrawl scheduler with checkpointed frontier snapshots.

## Interviewer probes to prepare
- "When is a URL considered visited?"
- "Where do host politeness and retry budgets live?"
- "What state must survive a crawler restart?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
