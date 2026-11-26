# Design Approach for Stack Overflow

## Step 1: Identify Core Entities

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| User | ✅ Yes | Core actor with reputation |
| Question | ✅ Yes | Main content type |
| Answer | ✅ Yes | Response to question |
| Vote | ✅ Yes | User action on posts |
| Comment | ✅ Yes | Additional discussion |
| Tag | ✅ Yes | Categorization |

---

## Step 2: Define Relationships

```
User (1) ──asks──> (n) Question
User (1) ──answers──> (n) Answer
Question (1) ──has──> (n) Answer
Question (1) ──has──> (n) Tag
Post (1) ──has──> (n) Vote
Post (1) ──has──> (n) Comment
```

---

## Step 3: Choose Design Patterns

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Observer** | ✅ Yes | Notify on votes, answers |
| **Strategy** | ✅ Yes | Answer ranking algorithms |
| **Template** | ✅ Yes | Common post behavior |
| **Decorator** | 🔄 v2 | Reputation badges |

---

## Step 4: Design Classes

### User
- Attributes: userId, name, email, reputation
- Methods: askQuestion(), postAnswer(), vote(), updateReputation()

### Post (Abstract)
- Attributes: postId, author, content, createdAt, votes
- Methods: upvote(), downvote(), getScore()

### Question (extends Post)
- Attributes: title, tags, answers, acceptedAnswer
- Methods: addAnswer(), acceptAnswer(), addTag()

### Answer (extends Post)
- Attributes: question, isAccepted
- Methods: accept()

### Vote
- Attributes: user, post, voteType (UP/DOWN)

### StackOverflowService
- Methods: postQuestion(), postAnswer(), vote(), search()

---

## Step 5: Handle Edge Cases

- Self-voting prevention
- Duplicate vote handling
- Vote change (upvote to downvote)
- Accepting answer on closed question
- Negative reputation floor

---

## Step 6: Optimization Opportunities

| Operation | Optimized |
|-----------|-----------|
| Vote count | Cache score, update on vote |
| Search | Index by tags |
| Ranking | Pre-compute answer scores |
