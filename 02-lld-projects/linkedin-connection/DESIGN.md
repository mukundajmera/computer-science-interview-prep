# Design for LinkedIn Connection System

Complete class design with diagrams, relationships, and key decisions.

---

## Mermaid Class Diagram

```mermaid
classDiagram
    class NetworkService {
        <<Singleton>>
        -static NetworkService instance
        -Map~String, User~ users
        -Map~String, ConnectionRequest~ pendingRequests
        -RecommendationStrategy recommendationStrategy
        +static getInstance() NetworkService
        +registerUser(User) void
        +sendConnectionRequest(String, String, String) ConnectionRequest
        +acceptRequest(String) boolean
        +rejectRequest(String) boolean
        +getConnections(String) Set~User~
        +getMutualConnections(String, String) Set~User~
        +getConnectionDegree(String, String) int
        +getRecommendations(String, int) List~User~
        +endorseSkill(String, String, String) boolean
    }

    class User {
        -String userId
        -String name
        -String email
        -String headline
        -String company
        -Set~User~ connections
        -Map~String, Skill~ skills
        -List~ConnectionRequest~ sentRequests
        -List~ConnectionRequest~ receivedRequests
        +addConnection(User) void
        +removeConnection(User) void
        +isConnectedTo(User) boolean
        +getConnectionCount() int
        +getMutualConnections(User) Set~User~
        +addSkill(String) Skill
        +getSkillEndorsements(String) int
    }

    class ConnectionRequest {
        -String requestId
        -User sender
        -User receiver
        -String message
        -RequestStatus status
        -LocalDateTime createdAt
        +accept() void
        +reject() void
        +withdraw() void
        +isPending() boolean
        +isExpired() boolean
    }

    class Skill {
        -String name
        -List~Endorsement~ endorsements
        +addEndorsement(User) void
        +getEndorsementCount() int
        +isEndorsedBy(User) boolean
    }

    class Endorsement {
        -User endorser
        -LocalDateTime endorsedAt
        +getEndorser() User
        +getEndorsedAt() LocalDateTime
    }

    class RecommendationStrategy {
        <<interface>>
        +getRecommendations(User, List~User~, int) List~User~
    }

    class MutualConnectionsStrategy {
        +getRecommendations(User, List~User~, int) List~User~
    }

    class SharedSkillsStrategy {
        +getRecommendations(User, List~User~, int) List~User~
    }

    class SameCompanyStrategy {
        +getRecommendations(User, List~User~, int) List~User~
    }

    class RequestStatus {
        <<enumeration>>
        PENDING
        ACCEPTED
        REJECTED
        WITHDRAWN
        EXPIRED
    }

    NetworkService --> RecommendationStrategy : uses
    NetworkService "1" --> "n" User : manages
    NetworkService "1" --> "n" ConnectionRequest : tracks
    RecommendationStrategy <|.. MutualConnectionsStrategy
    RecommendationStrategy <|.. SharedSkillsStrategy
    RecommendationStrategy <|.. SameCompanyStrategy
    User "n" --> "n" User : connections
    User "1" *-- "n" Skill : has
    Skill "1" *-- "n" Endorsement : has
    ConnectionRequest --> User : sender
    ConnectionRequest --> User : receiver
    Endorsement --> User : endorser
```

## Entity-Relationship Diagram

```mermaid
erDiagram
    USER ||--o{ CONNECTION : has
    USER ||--o{ CONNECTION_REQUEST : sends
    USER ||--o{ CONNECTION_REQUEST : receives
    USER ||--o{ USER_SKILL : has
    SKILL ||--o{ USER_SKILL : assigned_to
    USER_SKILL ||--o{ ENDORSEMENT : receives
    USER ||--o{ ENDORSEMENT : gives
    USER ||--o{ MESSAGE : sends
    USER ||--o{ MESSAGE : receives

    USER {
        string user_id PK
        string name
        string email UK
        string headline
        string company
        string industry
        string location
        timestamp created_at
    }

    CONNECTION {
        string connection_id PK
        string user_id_1 FK
        string user_id_2 FK
        timestamp connected_at
    }

    CONNECTION_REQUEST {
        string request_id PK
        string sender_id FK
        string receiver_id FK
        string message
        string status
        timestamp created_at
        timestamp responded_at
    }

    SKILL {
        string skill_id PK
        string name UK
        string category
    }

    USER_SKILL {
        string user_skill_id PK
        string user_id FK
        string skill_id FK
        int endorsement_count
    }

    ENDORSEMENT {
        string endorsement_id PK
        string user_skill_id FK
        string endorser_id FK
        timestamp endorsed_at
    }

    MESSAGE {
        string message_id PK
        string sender_id FK
        string receiver_id FK
        string content
        boolean is_read
        timestamp sent_at
    }
```

**Schema Notes:**
- `CONNECTION` is symmetric (user_id_1 < user_id_2 constraint)
- `USER_SKILL` caches endorsement count for performance
- `ENDORSEMENT` requires endorser to be 1st-degree connection
- BFS on `CONNECTION` table for degrees of separation

---

## Class Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          NetworkService                                  │
│                           <<Singleton>>                                  │
├─────────────────────────────────────────────────────────────────────────┤
│ - instance: NetworkService                                               │
│ - users: Map<String, User>                                              │
│ - pendingRequests: Map<String, ConnectionRequest>                        │
│ - recommendationStrategy: RecommendationStrategy                         │
├─────────────────────────────────────────────────────────────────────────┤
│ + getInstance(): NetworkService                                          │
│ + registerUser(user): void                                               │
│ + sendConnectionRequest(senderId, receiverId, msg): ConnectionRequest   │
│ + acceptRequest(requestId): boolean                                      │
│ + rejectRequest(requestId): boolean                                      │
│ + getConnections(userId): Set<User>                                     │
│ + getMutualConnections(userId1, userId2): Set<User>                     │
│ + getConnectionDegree(userId1, userId2): int                            │
│ + getRecommendations(userId, count): List<User>                         │
│ + endorseSkill(endorserId, userId, skillName): boolean                  │
└───────────────────────────────────────┬─────────────────────────────────┘
                                        │ manages
                                        ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              User                                        │
├─────────────────────────────────────────────────────────────────────────┤
│ - userId: String                                                         │
│ - name: String                                                           │
│ - email: String                                                          │
│ - headline: String                                                       │
│ - company: String                                                        │
│ - connections: Set<User>                                                │
│ - skills: Map<String, Skill>                                            │
│ - sentRequests: List<ConnectionRequest>                                  │
│ - receivedRequests: List<ConnectionRequest>                              │
├─────────────────────────────────────────────────────────────────────────┤
│ + addConnection(user): void                                              │
│ + removeConnection(user): void                                           │
│ + isConnectedTo(user): boolean                                           │
│ + getConnectionCount(): int                                              │
│ + getMutualConnections(user): Set<User>                                 │
│ + addSkill(skillName): Skill                                            │
│ + getSkillEndorsements(skillName): int                                  │
└─────────────────────────────────────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│                         ConnectionRequest                                │
├─────────────────────────────────────────────────────────────────────────┤
│ - requestId: String                                                      │
│ - sender: User                                                           │
│ - receiver: User                                                         │
│ - message: String                                                        │
│ - status: RequestStatus                                                  │
│ - createdAt: LocalDateTime                                              │
├─────────────────────────────────────────────────────────────────────────┤
│ + accept(): void                                                         │
│ + reject(): void                                                         │
│ + withdraw(): void                                                       │
│ + isPending(): boolean                                                   │
│ + isExpired(): boolean                                                   │
└─────────────────────────────────────────────────────────────────────────┘


┌───────────────────────────┐     ┌────────────────────────────────────────┐
│          Skill            │     │           Endorsement                  │
├───────────────────────────┤     ├────────────────────────────────────────┤
│ - name: String            │     │ - endorser: User                       │
│ - endorsements: List      │     │ - endorsedAt: LocalDateTime            │
├───────────────────────────┤     ├────────────────────────────────────────┤
│ + addEndorsement(User)    │     │ + getEndorser(): User                  │
│ + getEndorsementCount()   │     │ + getEndorsedAt(): LocalDateTime       │
│ + isEndorsedBy(User)      │     │                                        │
└───────────────────────────┘     └────────────────────────────────────────┘


┌─────────────────────────────────────────────────────────────────────────┐
│               RecommendationStrategy <<interface>>                       │
├─────────────────────────────────────────────────────────────────────────┤
│ + getRecommendations(user: User, allUsers: List<User>, count: int)      │
│   : List<User>                                                          │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         ▼                       ▼                       ▼
┌──────────────────┐ ┌─────────────────────┐ ┌──────────────────────┐
│ MutualConnections│ │  SharedSkills       │ │ SameCompany          │
│ Strategy         │ │  Strategy           │ │ Strategy             │
└──────────────────┘ └─────────────────────┘ └──────────────────────┘
```

---

## Enumerations

### RequestStatus
```
RequestStatus {
    PENDING,
    ACCEPTED,
    REJECTED,
    WITHDRAWN,
    EXPIRED
}
```

---

## Core Classes

### User
- **Attributes**:
  - `userId: String` - Unique identifier
  - `name: String` - Display name
  - `email: String` - Email address
  - `headline: String` - Professional headline
  - `company: String` - Current company
  - `connections: Set<User>` - 1st degree connections
  - `skills: Map<String, Skill>` - User's skills
- **Methods**:
  - `addConnection(User): void` - Add 1st degree connection
  - `removeConnection(User): void` - Remove connection
  - `isConnectedTo(User): boolean` - Check if connected
  - `getMutualConnections(User): Set<User>` - Find mutual connections
- **Patterns Used**: None (data class)

### ConnectionRequest
- **Attributes**:
  - `requestId: String` - Unique request ID
  - `sender: User` - Who sent the request
  - `receiver: User` - Who receives the request
  - `message: String` - Optional message
  - `status: RequestStatus` - Current status
  - `createdAt: LocalDateTime` - When created
- **Methods**:
  - `accept(): void` - Accept and create connection
  - `reject(): void` - Reject the request
  - `isExpired(): boolean` - Check if expired (30 days)

### Skill
- **Attributes**:
  - `name: String` - Skill name
  - `endorsements: List<Endorsement>` - Who endorsed
- **Methods**:
  - `addEndorsement(User): void` - Add endorser
  - `getEndorsementCount(): int` - Count endorsements
  - `isEndorsedBy(User): boolean` - Check if endorsed by user

### NetworkService (Facade + Singleton)
- **Attributes**:
  - `instance: NetworkService` - Singleton instance
  - `users: Map<String, User>` - All registered users
  - `pendingRequests: Map<String, ConnectionRequest>` - Active requests
  - `recommendationStrategy: RecommendationStrategy` - Current strategy
- **Methods**:
  - `getInstance()` - Get singleton
  - `sendConnectionRequest(...)` - Create and send request
  - `acceptRequest(...)` - Accept pending request
  - `getConnections(...)` - Get user's connections
  - `getMutualConnections(...)` - Find common connections
  - `getConnectionDegree(...)` - Calculate degrees of separation
  - `getRecommendations(...)` - Get suggested connections
  - `endorseSkill(...)` - Endorse a skill
- **Patterns Used**: Singleton, Facade

### RecommendationStrategy (Interface)
- **Methods**:
  - `getRecommendations(User, List<User>, int): List<User>`
- **Implementations**:
  - `MutualConnectionsStrategy` - Rank by mutual connection count
  - `SharedSkillsStrategy` - Rank by common skills
  - `SameCompanyStrategy` - Prioritize same company
- **Patterns Used**: Strategy

---

## Key Design Decisions

### Decision 1: Bidirectional Connections
**Rationale**:
- LinkedIn model requires mutual agreement
- Both users must see each other in connections
- Simplifies friend lookup

**Implementation**:
- When request accepted, add to both users' connection sets
- When removed, remove from both

---

### Decision 2: Graph Representation with Adjacency List
**Rationale**:
- Each User stores Set<User> connections
- O(1) connection lookup
- O(n) for finding all connections
- Memory efficient for sparse graphs

**Trade-off**:
- Not ideal for global graph queries
- But optimal for user-centric operations

---

### Decision 3: Strategy Pattern for Recommendations
**Rationale**:
- Multiple recommendation algorithms possible
- Easy to A/B test different strategies
- Can combine strategies

**Alternative**:
- Hardcoded algorithm (simpler but inflexible)

---

### Decision 4: BFS for Connection Degree
**Rationale**:
- Find shortest path between users
- Degree = path length
- BFS guarantees shortest path in unweighted graph

**Complexity**:
- O(V + E) where V = users, E = connections
- Optimize with bidirectional BFS for large graphs

---

## Complexity Analysis

### Time Complexity

| Operation | Complexity | Notes |
|-----------|------------|-------|
| Add connection | O(1) | HashSet add |
| Check if connected | O(1) | HashSet contains |
| Get all connections | O(n) | Return set copy |
| Mutual connections | O(min(n,m)) | Set intersection |
| Connection degree (BFS) | O(V+E) | Breadth-first search |
| Recommendations | O(V*C) | V=users, C=connections |

### Space Complexity

| Component | Complexity | Notes |
|-----------|------------|-------|
| Users storage | O(U) | U = total users |
| Connections | O(C) | C = total connections |
| Pending requests | O(R) | R = pending requests |
| BFS visited | O(V) | During degree calculation |

---

## Thread Safety (v3)

### Critical Sections:
1. **Connection modification** - Adding/removing connections
2. **Request state changes** - Accept/reject race conditions
3. **Endorsement updates** - Concurrent endorsements
4. **User registration** - Duplicate user prevention

### Synchronization Strategy:
```java
// ConcurrentHashMap for user storage
private final ConcurrentHashMap<String, User> users = new ConcurrentHashMap<>();

// Lock per user for connection modifications
private final ConcurrentHashMap<String, ReentrantLock> userLocks = new ConcurrentHashMap<>();

// Synchronized request status updates
public synchronized void accept() {
    if (status == RequestStatus.PENDING) {
        status = RequestStatus.ACCEPTED;
        // Create bidirectional connection
    }
}
```

---

## Extension Points

| Feature | Where to Add | Pattern |
|---------|--------------|---------|
| Block user | User class | State pattern |
| Connection notes | ConnectionRequest | Decorator |
| Multiple strategies | NetworkService | Composite strategy |
| Connection strength | Connection class | Attribute |
| Privacy settings | User class | Strategy |
