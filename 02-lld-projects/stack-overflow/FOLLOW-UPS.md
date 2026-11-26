# Stack Overflow - Follow-Up Questions

## Follow-up questions
1. How would you make voting idempotent when the same user clicks upvote twice?
2. What reputation changes occur when a user switches from upvote to downvote?
3. How would you prevent two concurrent accept-answer requests from leaving two accepted answers?
4. How would you index tags and keywords while keeping post writes simple?
5. How would you rank answers using score, acceptance, age, and author reputation?

## Variants and extensions
1. Close and reopen workflows with reputation thresholds.
2. Badge awards through observer-style reputation events.
3. Moderation queues for flagged posts and comments.
4. Search relevance with tag filters and full-text ranking.

## Interviewer probes to prepare
- "What key enforces one vote per user per post?"
- "Who is allowed to accept an answer?"
- "Where should reputation policy live?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Common pitfalls](./PITFALLS.md)
