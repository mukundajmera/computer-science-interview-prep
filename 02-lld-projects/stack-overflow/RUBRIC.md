# Stack Overflow - Interview Scoring Rubric

## Scoring rubric
| Dimension | Weight | Strong signal |
|---|---:|---|
| Requirements clarity | 15% | Clarifies question, answer, comment, tag, voting, acceptance, reputation, and search scope |
| Domain modeling | 20% | Separates `User`, abstract `Post`, `Question`, `Answer`, `Vote`, `Comment`, `Tag`, and service operations |
| Voting and reputation correctness | 30% | Enforces one vote per user per post, no self-voting, vote changes, accepted-answer rules, and consistent reputation deltas |
| Search and ranking design | 15% | Supports tag and keyword lookup with answer/question ranking without coupling search to post mutation |
| Concurrency and communication | 20% | Explains thread-safe voting, cached scores, answer ranking, and v1 to v3 progression without premature distributed design |

## Performance bands
- `1/5`: CRUD-only Q&A model with no vote identity, reputation rules, or acceptance ownership checks.
- `3/5`: working service with posts, tags, comments, basic votes, and search, but weak concurrency or vote-change handling.
- `5/5`: consistent content model with safe voting, reputation updates, accepted answers, indexed search paths, and clear ranking tradeoffs.

## Common pitfalls
See [PITFALLS.md](./PITFALLS.md).

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Approach](./APPROACH.md)
- [Design](./DESIGN.md)
