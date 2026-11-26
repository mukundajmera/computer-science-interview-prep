# Code Walkthrough: Stack Overflow

## Overview

Q&A platform with voting and reputation.

---

## Core Entities

| Entity | Key Features |
|--------|-------------|
| Question | title, body, tags, votes, answers |
| Answer | body, votes, isAccepted |
| User | reputation, badges |
| Comment | body, parent (Q or A) |
| Vote | type (up/down), voter |

---

## Key Operations

### Voting System

```java
void vote(Post post, User voter, VoteType type) {
    if (voter == post.author) throw new Exception("Can't vote own post");
    if (voter.reputation < VOTE_THRESHOLD) throw new Exception("Not enough rep");
    
    post.addVote(type);
    
    // Update author reputation
    if (type == UP) post.author.addReputation(10);
    else post.author.addReputation(-2);
}
```

### Reputation Rules

| Action | Points |
|--------|--------|
| Question upvote | +10 |
| Answer upvote | +10 |
| Answer accepted | +15 |
| Downvote received | -2 |
| Downvote given | -1 |

---

## Interview Questions

### 1. "How to rank answers?"

```java
List<Answer> getSortedAnswers(Question q) {
    return q.answers.stream()
        .sorted(Comparator
            .comparing(Answer::isAccepted).reversed()
            .thenComparing(Answer::getVoteCount).reversed())
        .collect(toList());
}
```

### 2. "How to implement search?"

- Full-text search: Elasticsearch
- Tag-based filtering
- Sort by relevance/votes/date

### 3. "How to prevent spam?"

- Rate limiting
- Reputation-based privileges
- Community flagging
- Captcha for new users

---

## Design Patterns

| Pattern | Usage |
|---------|-------|
| **Observer** | Notifications |
| **Strategy** | Sorting algorithms |
| **Decorator** | Badge system |
