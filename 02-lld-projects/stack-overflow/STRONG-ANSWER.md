# Strong Answer: Stack Overflow System

**Pacing Target:** 45 minutes

## 1. Introduction & Requirements Gathering (0-5 minutes)

**Say:** "To design the Stack Overflow System, I will focus on modeling the core entities, defining the interfaces, and ensuring efficient operations. I'll begin by outlining the core data models, then progress to the API and architecture, and finally address scale and correctness. Our primary goal is to ensure consistency and correctness for Q&A workflows."

**Explicit Clarifications:**
- Normal use-case: Users can post questions, answers, and vote.
- Duplicate operation / Empty input: What happens if a user tries to accept an answer twice or post empty content? We'll enforce simple validation and state checks.
- Capacity boundary: Scaling search and voting under load.
- Failure rollback: If an operation fails midway (e.g., reputation update fails), the state shouldn't be partially committed. We'll discuss how a database transaction handles this compared to our in-memory data structures.

## 2. Entity Modeling & Core APIs (5-15 minutes)

**Say:** "The core entities are `User`, `Question`, `Answer`, and the central `StackOverflowService` (acting as a Manager). We use enums for `VoteType`. Notice that instead of a separate `Vote` entity instances for every single click, our optimized approach just increments counters on the `Post` (Question/Answer) to save memory, though we'd track actual user votes in a database to prevent duplicates."

### API Contracts
- `StackOverflowService.postQuestion(userId, title, content, tags) -> Question`
- `StackOverflowService.postAnswer(userId, questionId, content) -> Answer`
- `StackOverflowService.vote(postId, VoteType) -> void`
- `StackOverflowService.acceptAnswer(answerId) -> void`
- `StackOverflowService.search(keyword) -> List<Question>`

Version-specific feature deltas: The `v3-optimized` and `v1-basic` versions use HashMaps for `users`, `questions`, and `answers` for `O(1)` retrieval by ID, managing state explicitly. The `v2-extended` version adds explicit `Tag`, `Vote`, and `Comment` objects with more complex relationships like inheritance from an abstract `Post` class, whereas `v3-optimized` and `v1-basic` simplify the structure by treating `Question` and `Answer` as distinct standalone classes and tracking votes purely as integer counts.

## 3. Design Alternatives & Patterns (15-25 minutes)

**Say:** "We use the **Singleton Pattern** for `StackOverflowService` to centralize in-memory state. For extensibility (as unimplemented extensions), we could use the Strategy Pattern for different search or reputation algorithms, and the Observer Pattern to notify users of new answers. 
An alternative to tracking votes as an integer count directly on the `Question` and `Answer` is storing individual `Vote` objects mapping `User` to `Post`. We chose the integer counter in the optimized code for simplicity and reduced memory overhead, but the individual object approach (used in our extended versions) is required to accurately prevent duplicate voting by the same user."

## 4. Correctness & Complexity (25-35 minutes)

**Say:** "For complexity, our `HashMap` storage gives us `O(1)` lookups for voting and posting. However, `search(keyword)` requires `O(N)` time because it iterates over all questions to perform substring matching. To optimize this, we could build an Inverted Index mapping keywords to `Question` IDs, reducing search to `O(1)` or `O(log N)` at the cost of `O(K)` overhead during question creation."

**Acceptance Cases Execution:**
- **Normal use-case**: `postQuestion` and `postAnswer` successfully link entities.
- **Empty/invalid input**: Null checks in `postQuestion` and `postAnswer` return `null` if the user or question doesn't exist.
- **Duplicate operation**: `acceptAnswer` uses idempotency. If an answer is already accepted, setting `isAccepted = true` twice doesn't break logic, though reputation might be awarded twice unless we add a guard clause.
- **Capacity boundary**: In-memory maps grow linearly `O(N)` with posts.

## 5. Concrete Failure & Concurrency Discussion (35-45 minutes)

**Say:** "Because we rely on shared state (e.g., `votes` counter on `Question`/`Answer`, and `reputation` on `User`), concurrent requests can cause race conditions. If two threads call `vote()` on the same post simultaneously, they might read the same initial vote count and both write back the same incremented value, losing one vote."

**Failure Rollback & Concurrency Fix:**
In our Python and Java `v3-optimized` versions, operations like `votes += value` or `reputation += points` are not inherently thread-safe. While Java uses `public static synchronized StackOverflowService getInstance()` for singleton instantiation, the actual state mutation methods are unprotected. To fix this, we should add the explicitly discovered `synchronized` keyword directly to the mutating methods in `StackOverflowService.java` to prevent race conditions during concurrent voting or question posting. Additionally, if updating a user's reputation fails after updating a post's vote count, we would need a transactional rollback. In a real system, this is handled by database ACID transactions (e.g., `BEGIN; UPDATE POSTS...; UPDATE USERS...; COMMIT;`), ensuring either both succeed or neither does.
