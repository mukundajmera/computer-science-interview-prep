# Live Comments - Follow-Up Questions

## Follow-up questions
1. How would `CommentIngressService` deduplicate a retried comment submission?
2. What cursor should a client send when reconnecting to a live session?
3. How large should the `CommentReplayStore` bounded replay window be?
4. What happens if fanout fails after the comment has been accepted?
5. How would you keep comment order deterministic across concurrent writers?

## Variants and extensions
1. Moderation hold or delete events.
2. Slow-mode rate limits per live session.
3. Pinned comments and creator highlights.
4. Backpressure handling for slow consumers.

## Interviewer probes to prepare
- "What is the source of truth for replay?"
- "How do you separate accepted comments from delivered comments?"
- "What changes when comments are served from an external store?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
