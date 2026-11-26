# Instagram Core - Follow-Up Questions

## Follow-up questions
1. How would you make post creation idempotent if the client retries the same request?
2. Where should media validation happen relative to `MediaStorageGateway`?
3. How would `FeedComposer` change for fanout-on-write versus fanout-on-read?
4. What indexes are needed to serve recent posts for a bounded feed window?
5. How would follow/unfollow mutations stay safe under concurrent requests?

## Variants and extensions
1. Private accounts and follow-request approval.
2. Like/comment counters on media posts.
3. Media-processing status before posts become feed-visible.
4. Personalized ranking strategy plugged into feed composition.

## Interviewer probes to prepare
- "Which object is the canonical write model and which is the read snapshot?"
- "What is the idempotency key for a post mutation?"
- "What changes when the media store is no longer in memory?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
