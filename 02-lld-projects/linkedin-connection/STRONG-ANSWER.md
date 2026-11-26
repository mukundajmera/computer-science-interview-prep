# Strong Answer: Linkedin Connection

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Linkedin Connection system, I'll start by clarifying the core functional and non-functional requirements. We need to handle core social graph operations (adding/removing connections, sending/accepting requests), ensuring efficient state transitions and extensibility."

### Explicit Clarifications
- **Scope Context**: The focus is on the graph topology, connection lifecycle, and recommendations rather than profile multimedia management or live feed aggregation.
- **Handling Invalid Data**: The design must reject empty user IDs, self-connections, and references to non-existent users gracefully without crashing.
- **Idempotency**: Duplicate connection requests or endorsing an already endorsed skill will be silently ignored or safely return early.

## 2. Entity Modeling & Public APIs (10 mins)
**Say:** "Let's define the core domain entities and the public API contract for our system."

### Core Entities
The primary domain entities are:
- `User`: Encapsulates user identity, active connections, pending connection requests, and skills.
- `ConnectionRequest`: A state machine mapping an invitation (sender, receiver, state, timestamp).
- `Skill`: Represents an endorsable competency tied to a user.

### Public APIs
Our `NetworkService` facade exposes operations implemented in both Java (11+) and Python (3.8+). The core APIs include:
- `registerUser(User)` -> boolean
- `sendConnectionRequest(from, to, msg)` -> ConnectionRequest
- `acceptRequest(requestId)` -> boolean
- `rejectRequest(requestId)` -> boolean
- `getMutualConnections(user1, user2)` -> Set<User>
- `getConnectionDegree(user1, user2)` -> int
- `endorseSkill(endorser, user, skill)` -> boolean

### Implementation Contracts

#### Standard Flow
`NetworkService.sendConnectionRequest(from, to)` succeeds, creating a `ConnectionRequest` with `PENDING` status. Calling `NetworkService.acceptRequest(requestId)` transitions it to `ACCEPTED` and atomically establishes symmetric bidirectional connections.

**Java snippet (`v3-optimized/NetworkService.java`):**
```java
public boolean acceptRequest(String requestId) {
    ConnectionRequest request = pendingRequests.get(requestId);
    if (request == null) return false;
    
    // Check maximum capacity limit boundary
    if (request.getReceiver().getConnectionCount() >= 30000) {
        // Atomic rollback: Request remains pending, no connections added
        return false; 
    }
    
    if (request.accept()) {
        pendingRequests.remove(requestId);
        return true;
    }
    return false;
}
```

**Python snippet (`v3-optimized/network_service.py`):**
```python
def accept_request(self, request_id: str) -> bool:
    request = self._pending_requests.get(request_id)
    if not request:
        return False
        
    # Check boundary
    if request.receiver.get_connection_count() >= 30000:
        # Rollback on failure: no state changed
        return False
        
    if request.accept():
        del self._pending_requests[request_id]
        return True
    return False
```

#### Edge Cases: Invalid and Duplicate Requests
Attempting to register a null/empty user immediately raises an error, avoiding state corruption. 

**Java snippet (`v3-optimized/User.java`):**
```java
public User(String userId, String name, String email) {
    if (userId == null || userId.isEmpty()) {
        throw new IllegalArgumentException("User ID cannot be null or empty");
    }
    this.userId = userId;
    // ... initialization ...
}
```

**Python snippet (`v3-optimized/user.py`):**
```python
def __init__(self, user_id: str, name: str, email: str, 
             headline: str = "", company: str = ""):
    if not user_id:
        raise ValueError("User ID cannot be null or empty")
    self._user_id = user_id
    # ... initialization ...
```

Calling `sendConnectionRequest("A", "A")` returns an error, avoiding self-connections. Sending a duplicate connection request when a pending request already exists safely returns early.

**Java snippet (`v3-optimized/NetworkService.java`):**
```java
if (sender.equals(receiver)) {
    System.out.println("Cannot send connection request to yourself");
    return null;
}
for (ConnectionRequest req : sender.getSentRequests()) {
    if (req.getReceiver().equals(receiver) && req.isPending()) {
        System.out.println("Pending request already exists");
        return null; // Idempotent duplicate check
    }
}
```

**Python snippet (`v3-optimized/network_service.py`):**
```python
if sender == receiver:
    print("Cannot send connection request to yourself")
    return None

for req in sender.get_sent_requests():
    if req.receiver == receiver and req.is_pending():
        print("Pending request already exists")
        return None
```

### Version-Specific Feature Deltas
- **v1-basic**: Implements foundational entities (`User`, `ConnectionRequest`), basic connection graph topology, and request state transitions (accept/reject) without advanced queries or limits.
- **v2-extended**: Adds skills and endorsements, graph queries (`getConnectionDegree`, `getMutualConnections`), recommendation strategies, and observer notifications. 
- **v3-optimized**: Introduces thread-safe collections (`ConcurrentSkipListSet`), bounded BFS concurrency, and lock striping to handle parallel requests and high concurrency securely. Focused tests explicitly target this v3-optimized version rather than silently importing v1.

## 3. Data Structure Rationale & Correctness (10 mins)
**Say:** "Choosing the right data structures dictates the time and space complexity of our graph queries."

### Complexity & Correctness
- **In-Memory Adjacency List**: `ConcurrentHashMap<String, User>` provides `O(1)` access to users and their connection sets (`HashSet` in basic v2, `ConcurrentSkipListSet` in v3).
- **Mutual Connections**: Computed via set intersection (`O(min(N, M))`), where `N` and `M` are the degree of each user.
- **Degree Calculation**: Solved using Breadth-First Search (BFS) bounded by a maximum depth, avoiding cycle traps using a `visited` set (Time: `O(V+E)` in worst-case bounded subgraph).
- **Correctness invariant**: In both Java and Python, all bidirectional connections must be perfectly symmetrical when requests transition to `ACCEPTED`.

## 4. Design Alternatives & Trade-offs (5 mins)
**Say:** "I've explored various design patterns and component boundaries to maintain modularity."

- **Observer Pattern**: A standard approach to decouple connection request lifecycle transitions from notification emission (e.g. sending emails).
- **State Pattern vs Explicit Enums**: While a strict State pattern (separate classes for Pending, Accepted, Rejected) adds safety, our implementation uses an explicit `RequestStatus` Enum for simplicity and reduced heap allocation overhead.
- **Singleton Manager vs Dependency Injection**: `NetworkService` acts as a Singleton facade to streamline the interview codebase, although in production, dependency injection is preferred to isolate test state and avoid hidden coupling.

## 5. System Limits and Concurrency Discussion (10 mins)
**Say:** "To ensure stability in high-traffic scenarios, we must protect against race conditions and resource exhaustion."

### Concurrency and Thread Safety
- **Lock Striping**: In our `v3-optimized` implementation, concurrency defense relies on fine-grained synchronization (or lock striping by user ID) to prevent race conditions during concurrent accept/reject actions.
- **Transactions and Fault Tolerance**: Suppose a user accepts a connection, but updating the inverse connection edge fails (e.g., memory exhaustion or DB timeout in a distributed context). We must roll back the entire transaction. In our codebase, adding connections is an atomic logical transaction (`user1.addConnection(user2)` and `user2.addConnection(user1)`).
- **Capacity Limits**: A strict upper limit on connection counts per user (e.g., 30,000 max connections) must be enforced during the `acceptRequest()` flow. If the boundary is breached, the acceptance is rolled back, the request remains pending or enters a failed state, and an error is safely propagated.

## 6. Failure Handling (5 mins)
**Say:** "Systems fail, so we need to anticipate and handle failures gracefully at the lowest level."

- We handle network and application-level failures using explicit rollbacks. For example, if a node crashes during a BFS degree traversal, our bounded queue prevents unbounded memory leaks. 
- Idempotency keys (`requestId`) ensure that retried `acceptRequest()` calls over a flaky network do not mutate the graph twice.
