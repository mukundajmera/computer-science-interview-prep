# Instagram Core - Common Pitfalls

## Common pitfalls
1. Treating media upload, post mutation, follow graph updates, and feed composition as one class.
2. Building feeds from mutable post objects instead of stable snapshots.
3. Ignoring idempotency for repeated create-post or follow/unfollow requests.
4. Returning unbounded feeds without explaining the bounded window read path.
5. Hiding the storage gateway behind in-memory fields in the v2/v3 discussion.

## Why these fail interviews
- They blur the project docs' named service boundaries.
- They make repeated requests and concurrent reads produce surprising results.
- They skip the stated complexity goal for indexed lookup and bounded list reads.

## Mitigations
- State which service owns media, follow edges, feed assembly, and storage integration.
- Treat `Snapshot` as the read model and `Mutation` as the write intent.
- Require stable request identifiers for replay-safe v3 mutations.
- Keep feed APIs paginated or windowed and explain the index used to serve them.

## Follow-up questions
See [FOLLOW-UPS.md](./FOLLOW-UPS.md).

## Cross-links
- [Scoring rubric](./RUBRIC.md)
- [Code walkthrough](./CODE-WALKTHROUGH.md)
