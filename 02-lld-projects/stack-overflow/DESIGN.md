# Design for Stack Overflow

## Mermaid Class Diagram

```mermaid
classDiagram
    class StackOverflowService {
        <<Singleton>>
        -Map~String, User~ users
        -Map~String, Question~ questions
        -Map~String, Tag~ tags
        +postQuestion(String, String, String, List~String~) Question
        +postAnswer(String, String, String) Answer
        +vote(String, String, VoteType) boolean
        +acceptAnswer(String, String) boolean
        +addComment(String, String, String) Comment
        +searchByTag(String) List~Question~
        +getTopQuestions(int) List~Question~
    }

    class User {
        -String userId
        -String name
        -String email
        -int reputation
        -List~Question~ questions
        -List~Answer~ answers
        -List~Badge~ badges
        +updateReputation(int) void
        +getReputation() int
        +awardBadge(Badge) void
    }

    class Post {
        <<abstract>>
        #String postId
        #User author
        #String content
        #Map~String, Vote~ votes
        #List~Comment~ comments
        #LocalDateTime createdAt
        #LocalDateTime updatedAt
        +getScore() int
        +addVote(Vote) boolean
        +removeVote(String) boolean
        +addComment(Comment) void
        +edit(String) void
    }

    class Question {
        -String title
        -Set~Tag~ tags
        -List~Answer~ answers
        -Answer acceptedAnswer
        -int viewCount
        -boolean isClosed
        +addAnswer(Answer) void
        +acceptAnswer(Answer) void
        +addTag(Tag) void
        +incrementViews() void
    }

    class Answer {
        -Question question
        -boolean isAccepted
        +accept() void
        +isAccepted() boolean
    }

    class Comment {
        -String commentId
        -User author
        -String text
        -LocalDateTime createdAt
    }

    class Vote {
        -String voteId
        -User user
        -VoteType voteType
        -LocalDateTime createdAt
    }

    class Tag {
        -String tagId
        -String name
        -String description
        -int questionCount
        +incrementCount() void
    }

    class Badge {
        -String badgeId
        -String name
        -BadgeLevel level
        -String description
    }

    class VoteType {
        <<enumeration>>
        UPVOTE
        DOWNVOTE
    }

    class BadgeLevel {
        <<enumeration>>
        GOLD
        SILVER
        BRONZE
    }

    StackOverflowService "1" --> "n" User : manages
    StackOverflowService "1" --> "n" Question : manages
    StackOverflowService "1" --> "n" Tag : manages
    Post <|-- Question
    Post <|-- Answer
    Post --> User : author
    Post "1" *-- "n" Comment : has
    Post "1" *-- "n" Vote : has
    Question "1" *-- "n" Answer : has
    Question --> Answer : acceptedAnswer
    Question "n" --> "n" Tag : tagged_with
    User "1" --> "n" Question : asks
    User "1" --> "n" Answer : answers
    User "1" --> "n" Badge : has
    Answer --> Question : answers
```

## Entity-Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ QUESTION : asks
    USER ||--o{ ANSWER : posts
    USER ||--o{ COMMENT : writes
    USER ||--o{ VOTE : casts
    USER ||--o{ USER_BADGE : earns
    BADGE ||--o{ USER_BADGE : awarded_to
    QUESTION ||--o{ ANSWER : has
    QUESTION ||--o{ QUESTION_TAG : tagged
    TAG ||--o{ QUESTION_TAG : applied_to
    QUESTION ||--o{ COMMENT : has
    ANSWER ||--o{ COMMENT : has
    QUESTION ||--o{ VOTE : receives
    ANSWER ||--o{ VOTE : receives

    USER {
        string user_id PK
        string username UK
        string email UK
        string display_name
        int reputation
        timestamp created_at
        timestamp last_seen
    }

    QUESTION {
        string question_id PK
        string author_id FK
        string accepted_answer_id FK
        string title
        text body
        int score
        int view_count
        boolean is_closed
        timestamp created_at
        timestamp updated_at
    }

    ANSWER {
        string answer_id PK
        string question_id FK
        string author_id FK
        text body
        int score
        boolean is_accepted
        timestamp created_at
        timestamp updated_at
    }

    COMMENT {
        string comment_id PK
        string post_id FK
        string post_type
        string author_id FK
        text text
        timestamp created_at
    }

    VOTE {
        string vote_id PK
        string post_id FK
        string post_type
        string user_id FK
        string vote_type
        timestamp created_at
    }

    TAG {
        string tag_id PK
        string name UK
        text description
        int question_count
    }

    QUESTION_TAG {
        string question_tag_id PK
        string question_id FK
        string tag_id FK
    }

    BADGE {
        string badge_id PK
        string name
        string level
        text description
    }

    USER_BADGE {
        string user_badge_id PK
        string user_id FK
        string badge_id FK
        timestamp awarded_at
    }
```

**Schema Notes:**
- `VOTE` uses polymorphic association via `post_type` (question/answer)
- `COMMENT` similarly uses `post_type` for questions or answers
- `QUESTION_TAG` junction table for many-to-many tagging
- Reputation updates triggered by vote events

---

## Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      StackOverflowService                                │
│                         <<Singleton>>                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ + postQuestion(userId, title, body, tags): Question                      │
│ + postAnswer(userId, questionId, body): Answer                           │
│ + vote(userId, postId, voteType): boolean                                │
│ + acceptAnswer(userId, answerId): boolean                                │
│ + addComment(userId, postId, text): Comment                              │
│ + searchByTag(tag): List<Question>                                       │
│ + getTopQuestions(count): List<Question>                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                         User                                             │
├─────────────────────────────────────────────────────────────────────────┤
│ - userId: String                                                         │
│ - name: String                                                           │
│ - reputation: int                                                        │
│ - questions: List<Question>                                              │
│ - answers: List<Answer>                                                  │
├─────────────────────────────────────────────────────────────────────────┤
│ + updateReputation(delta): void                                          │
│ + getReputation(): int                                                   │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────┐
│                      Post <<abstract>>                                   │
├─────────────────────────────────────────────────────────────────────────┤
│ # postId: String                                                         │
│ # author: User                                                           │
│ # content: String                                                        │
│ # votes: Map<String, Vote>                                              │
│ # comments: List<Comment>                                                │
│ # createdAt: DateTime                                                    │
├─────────────────────────────────────────────────────────────────────────┤
│ + getScore(): int                                                        │
│ + addVote(vote): boolean                                                 │
│ + addComment(comment): void                                              │
└────────────────────────┬────────────────────────────────────────────────┘
                         │
         ┌───────────────┴───────────────┐
         ▼                               ▼
┌─────────────────────────┐   ┌────────────────────────────┐
│       Question          │   │         Answer             │
├─────────────────────────┤   ├────────────────────────────┤
│ - title: String         │   │ - question: Question       │
│ - tags: Set<Tag>        │   │ - isAccepted: boolean      │
│ - answers: List<Answer> │   ├────────────────────────────┤
│ - acceptedAnswer: Answer│   │ + accept(): void           │
├─────────────────────────┤   │ + isAccepted(): boolean    │
│ + addAnswer(answer)     │   └────────────────────────────┘
│ + acceptAnswer(answer)  │
│ + addTag(tag)           │
└─────────────────────────┘

┌─────────────────────────┐   ┌────────────────────────────┐
│         Vote            │   │        Comment             │
├─────────────────────────┤   ├────────────────────────────┤
│ - user: User            │   │ - author: User             │
│ - voteType: VoteType    │   │ - text: String             │
│ - createdAt: DateTime   │   │ - createdAt: DateTime      │
└─────────────────────────┘   └────────────────────────────┘

VoteType { UPVOTE, DOWNVOTE }
```

---

## Key Design Decisions

### Decision 1: Post as Abstract Base Class
**Rationale**: Questions and answers share voting, comments, and scoring behavior.

### Decision 2: Vote Map by User ID
**Rationale**: O(1) lookup for existing vote, prevents duplicates.

### Decision 3: Reputation as User Attribute
**Rationale**: Central tracking, updated on vote/accept events.

---

## Complexity Analysis

| Operation | Complexity |
|-----------|------------|
| Vote | O(1) |
| Get score | O(1) with cache |
| Search by tag | O(n) or O(1) with index |
| Get answers | O(k) k = answer count |

---

## Thread Safety (v3)

- AtomicInteger for vote scores
- ConcurrentHashMap for votes
- Synchronized reputation updates
