# Design Approach for LinkedIn Connection System

A step-by-step thought process for designing the connection system.

---

## Step 1: Identify Core Entities

Extract nouns from the problem statement:

| Noun | Entity? | Reasoning |
|------|---------|-----------|
| User | ✅ Yes | Core actor with profile data |
| Connection | ✅ Yes | Relationship between users |
| Request | ✅ Yes | Pending invitation |
| Profile | ❌ No | Part of User |
| Skill | ✅ Yes | Endorsable competency |
| Endorsement | ✅ Yes | Skill validation |
| Network | ❌ No | Aggregate concept |

**Final Entities**: User, Connection, ConnectionRequest, Skill, Endorsement, NetworkService

---

## Step 2: Define Relationships

```
User (1) ──has──> (n) Connection
User (1) ──sends──> (n) ConnectionRequest
User (1) ──receives──> (n) ConnectionRequest
User (1) ──has──> (n) Skill
Skill (1) ──has──> (n) Endorsement
Endorsement (1) ──from──> (1) User (endorser)
```

### Relationship Types:

| Relationship | Type | Description |
|--------------|------|-------------|
| User → Connection | Association | Bidirectional link |
| User → Request | Composition | Request tied to users |
| User → Skill | Composition | Skills belong to user |
| Skill → Endorsement | Composition | Endorsements for skill |

---

## Step 3: Choose Design Patterns

### Pattern Analysis:

| Pattern | Apply? | Justification |
|---------|--------|---------------|
| **Observer** | ✅ Yes | Notify users of requests, endorsements |
| **Strategy** | ✅ Yes | Different recommendation algorithms |
| **Facade** | ✅ Yes | Simple API for complex network operations |
| **Singleton** | ✅ Yes | Single network service instance |

### Pattern Application:

1. **Observer Pattern** - ConnectionObserver
   - Notify when connection request received
   - Notify when request accepted/rejected
   - Notify when endorsed

2. **Strategy Pattern** - RecommendationStrategy
   - MutualConnectionsStrategy
   - SharedSkillsStrategy
   - SameCompanyStrategy

3. **Facade Pattern** - NetworkService
   - Hide complexity of graph operations
   - Simple interface for connection management

---

## Step 4: Design Classes

### Core Classes:

#### User
- **Attributes**:
  - `userId: String`
  - `name: String`
  - `email: String`
  - `headline: String`
  - `company: String`
  - `connections: Set<User>`
  - `skills: List<Skill>`
- **Methods**:
  - `addConnection(user): void`
  - `removeConnection(user): void`
  - `getConnectionDegree(user): int`
  - `getMutualConnections(user): Set<User>`

#### Connection
- **Attributes**:
  - `user1: User`
  - `user2: User`
  - `connectedAt: DateTime`
- **Methods**:
  - `getOtherUser(user): User`
  - `getDuration(): Duration`

#### ConnectionRequest
- **Attributes**:
  - `requestId: String`
  - `sender: User`
  - `receiver: User`
  - `message: String`
  - `status: RequestStatus`
  - `createdAt: DateTime`
- **Methods**:
  - `accept(): void`
  - `reject(): void`
  - `isExpired(): boolean`

#### Skill
- **Attributes**:
  - `name: String`
  - `endorsements: List<Endorsement>`
- **Methods**:
  - `addEndorsement(endorser): void`
  - `getEndorsementCount(): int`

#### NetworkService (Facade)
- **Attributes**:
  - `users: Map<String, User>`
  - `requests: Map<String, ConnectionRequest>`
  - `recommendationStrategy: RecommendationStrategy`
- **Methods**:
  - `sendConnectionRequest(from, to, message): ConnectionRequest`
  - `acceptRequest(requestId): void`
  - `rejectRequest(requestId): void`
  - `getConnections(userId): Set<User>`
  - `getMutualConnections(userId1, userId2): Set<User>`
  - `getRecommendations(userId): List<User>`
  - `getConnectionDegree(userId1, userId2): int`
  - `endorseSkill(endorserId, userId, skillName): void`

---

## Step 5: Handle Edge Cases

### Input Validation:
- Self-connection (user connecting to themselves)
- Duplicate connection request
- Already connected users
- Non-existent users

### Business Logic:
- Expired connection request
- Endorsing non-connection
- Maximum connections limit
- Withdrawn request handling
- Blocked user handling

### Concurrency (v3):
- Simultaneous accept/reject of same request
- Race condition in mutual connection query
- Concurrent endorsement updates

---

## Step 6: Optimization Opportunities

### Data Structures:
| Operation | Naive | Optimized |
|-----------|-------|-----------|
| Find if connected | O(n) | O(1) with HashSet |
| Mutual connections | O(n²) | O(n) with set intersection |
| 2nd degree connections | O(n²) | BFS with visited set |
| Recommendations | O(n³) | Precomputed scores |

### Caching:
- Cache connection counts
- Cache mutual connection counts for frequent pairs
- Cache recommendation lists (invalidate on connection change)

### Indexing:
- `Map<String, User>` - Users by ID
- `Map<String, Set<User>>` - Connections per user
- `Map<String, List<ConnectionRequest>>` - Pending requests per user

---

## Step 7: Version Progression

### v1-basic
- User class with connections
- ConnectionRequest with accept/reject
- Simple connection list
- Basic validation

### v2-extended
- Mutual connections calculation
- Connection recommendations (mutual-based)
- Skills and endorsements
- Observer notifications

### v3-optimized
- Thread-safe collections
- BFS for n-degree connections
- Optimized recommendation algorithm
- Concurrent request handling

---

## Code Organization

```
linkedin-connection/
├── java/
│   ├── v1-basic/
│   │   ├── User.java
│   │   ├── ConnectionRequest.java
│   │   ├── NetworkService.java
│   │   └── LinkedInDemo.java
│   ├── v2-extended/
│   │   ├── [All v1 enhanced]
│   │   ├── Skill.java
│   │   ├── Endorsement.java
│   │   └── RecommendationStrategy.java
│   └── v3-optimized/
│       └── [Thread-safe versions]
└── python/
    └── [Same structure]
```

---

## Interview Discussion Points

1. **Why Graph for Connections?**
   - Natural representation of social network
   - Enables BFS/DFS for path finding
   - Efficient mutual connection queries

2. **Bidirectional vs Unidirectional?**
   - LinkedIn uses bidirectional (both agree)
   - Twitter uses unidirectional (follow)
   - Trade-off: complexity vs use case fit

3. **Scaling to millions of users?**
   - Partition graph by user ID
   - Cache hot connection data
   - Precompute recommendations offline
