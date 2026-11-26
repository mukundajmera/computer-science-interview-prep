# Stack Overflow

## Problem Statement

Design a Q&A platform similar to Stack Overflow where users can ask questions, post answers, vote on content, and build reputation through participation.

---

## Functional Requirements

1. **Post Question**: Users can ask questions with title, body, and tags
2. **Post Answer**: Users can answer questions
3. **Voting**: Upvote/downvote questions and answers
4. **Accept Answer**: Question author can accept best answer
5. **Comments**: Add comments on questions and answers
6. **Tags**: Categorize questions with tags
7. **Reputation System**: Track user reputation based on activity
8. **Search**: Find questions by keywords or tags

---

## Non-Functional Requirements

1. **Scalability**: Handle millions of questions and answers
2. **Performance**: Fast search and retrieval
3. **Concurrency**: Handle simultaneous votes safely
4. **Consistency**: Accurate reputation calculations
5. **Availability**: High uptime for read operations

---

## Constraints & Assumptions

- Users must have minimum reputation to perform certain actions
- One vote per user per post (can change vote)
- Question author cannot vote on own question
- Answer author cannot vote on own answer
- Maximum 5 tags per question
- Reputation change: +10 for upvote, -2 for downvote

---

## Sample Interactions

```
1. Alice asks question about "Java memory management"
2. Bob answers the question with detailed explanation
3. Charlie upvotes Bob's answer (+10 rep for Bob)
4. Diana also upvotes and adds a comment
5. Alice accepts Bob's answer (+15 rep for Bob)
6. Eve downvotes Charlie's competing answer (-2 rep for Charlie)
7. Alice searches for questions with tag "java"
```

---

## Entities to Identify

| Entity | Responsibility |
|--------|---------------|
| User | Profile, reputation, questions, answers |
| Question | Title, body, tags, votes, answers |
| Answer | Body, votes, acceptance status |
| Comment | Text on question or answer |
| Vote | User's vote on a post |
| Tag | Category for questions |
| StackOverflowService | Main operations facade |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Users, questions, answers, basic voting |
| v2-extended | Comments, tags, reputation, search |
| v3-optimized | Thread-safe voting, answer ranking |
