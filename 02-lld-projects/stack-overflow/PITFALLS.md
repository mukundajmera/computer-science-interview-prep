# Stack Overflow - Common Pitfalls

## Common pitfalls
1. Storing only a score count and losing which user cast each vote.
2. Updating reputation without considering self-votes, vote changes, or accepted-answer bonuses.
3. Letting any user accept any answer instead of restricting acceptance to the question author.
4. Treating questions and answers as unrelated classes instead of sharing common post behavior.
5. Making search scan every question even though the design calls out tag and keyword lookup.

## Why these fail interviews
- They break core product rules under ordinary user actions.
- They make vote idempotency and reputation repair difficult.
- They miss the main extensibility point: common post behavior with specialized question and answer rules.

## Mitigations
- Store votes by user id per post so duplicate votes and vote changes are explicit.
- Centralize reputation deltas in the service or a dedicated policy.
- Use an abstract `Post` for shared vote/comment behavior.
- Keep tag indexes and ranking data separate from post mutation logic.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Code walkthrough](./CODE-WALKTHROUGH.md)
