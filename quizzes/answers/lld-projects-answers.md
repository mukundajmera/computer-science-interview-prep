# 🏗️ LLD Projects Quiz - Answer Key

> **Detailed explanations for all 52 questions**

---

## Section 1: Design Decisions

### Question 1
**Answer: C) Pessimistic locking with database row locks**

For parking spot booking, pessimistic locking is preferred because:
- High contention for same spots during peak hours
- Transaction is short (booking confirmation)
- Prevents race conditions completely

*Trade-offs:*
- Optimistic locking would require frequent retries during high contention
- Synchronized methods don't work in distributed systems
- No locking leads to double booking

---

### Question 2
**Answer: B) HashMap + Doubly Linked List**

This combination provides O(1) for both operations:
- HashMap: O(1) key lookup to find node
- Doubly Linked List: O(1) move to front and remove from tail

*Trade-offs:*
- Array requires O(n) for maintaining order
- BST gives O(log n) which is slower
- Single linked list requires O(n) for deletion

---

### Question 3
**Answer: B) State Pattern**

Elevator behavior changes based on state (idle, moving up, moving down, door open). Each state handles requests differently.

*Reasoning:*
- State encapsulates state-specific behavior
- Transitions are clear and maintainable
- Eliminates complex if-else chains

---

### Question 4
**Answer: C) Token Bucket**

Token Bucket is memory efficient:
- Stores only token count and last refill time (2 values)
- Fixed memory regardless of request history
- Allows controlled bursts

*Trade-offs:*
- Sliding Window Log stores every request timestamp (O(n) memory)
- Fixed Window has boundary burst problems
- Token Bucket balances efficiency and accuracy

---

### Question 5
**Answer: C) Board has composition of Pieces**

Pieces are created for a specific board and have no meaning without it. When board is destroyed, pieces are destroyed too.

*Reasoning:*
- Pieces belong to one specific game board
- Aggregation would imply pieces exist independently
- This is classic whole-part composition

---

### Question 6
**Answer: B) Use database unique constraint on (room_id, date)**

Database-level constraint is the most reliable:
- Enforced at database level, cannot be bypassed
- Atomic check and insert
- Works across distributed application instances

*Trade-offs:*
- Check-then-book has race condition window
- Table lock is too coarse
- Eventual consistency risks overbooking

---

### Question 7
**Answer: A) Aggregation - books can exist without library**

Books are physical entities that can be transferred between libraries or exist in warehouses. They have independent lifecycles.

*Reasoning:*
- Book isn't destroyed when removed from library
- Same book can belong to different libraries over time
- Composition would mean book is created/destroyed with library

---

### Question 8
**Answer: C) State pattern with separate state classes**

State pattern is ideal for vending machines:
- Each state encapsulates its behavior
- State transitions are explicit
- Easy to add new states or modify transitions

*Trade-offs:*
- If-else becomes unmaintainable with many states
- Switch statements violate Open/Closed Principle
- Strategy swaps algorithms, not contextual behavior

---

### Question 9
**Answer: B) Track row, column, and diagonal counts per player**

Maintain count arrays:
- rowCount[3] for each player
- colCount[3] for each player  
- diagonalCount, antiDiagonalCount

After each move, check if any count equals board size.

*Trade-offs:*
- Full board scan is O(n²) per move
- This approach is O(1) per move with O(n) space
- Storing winning combinations works but less elegant

---

### Question 10
**Answer: B) State Pattern**

ATM transaction flow has clear states:
- No Card → Card Inserted → PIN Verified → Transaction Selected → Processing

*Reasoning:*
- Behavior depends on current authentication state
- Chain of Responsibility is for request passing
- Template Method is for algorithm skeleton

---

### Question 11
**Answer: D) Both B and C**

Optimal approach combines:
- Net balance per person (quick settlement calculation)
- Graph-based simplification (minimize transactions)

*Trade-offs:*
- Individual transactions needed for audit trail
- Net balance alone doesn't minimize transactions
- Graph algorithm finds minimum edges to settle all debts

---

### Question 12
**Answer: B) Composite Pattern**

Files and directories form a tree structure:
- File is leaf node
- Directory is composite containing files or directories
- Both implement common FileSystemItem interface

*Reasoning:*
- Uniform treatment of files and directories
- Recursive operations (size, search) work naturally
- Tree traversal algorithms apply

---

### Question 13
**Answer: D) All of the above can work; choice depends on concurrency patterns and deployment**

Different approaches suit different scenarios:
- **Optimistic locking**: Good for moderate concurrency, requires retry logic
- **Pessimistic locking**: Best for high contention on a single database, simpler but blocks
- **Distributed lock (e.g., via Redis)**: Typically needed only when the application and/or database is deployed across multiple nodes/regions and you must coordinate access across them

*Trade-offs:* For a typical movie-ticket booking system with a single primary database, database-level pessimistic/optimistic locking is usually sufficient and simpler; distributed locks add infrastructure complexity and are mainly justified when you already run a distributed setup (multiple app servers/regions and/or multiple database instances).

---

### Question 14
**Answer: B) Geospatial index (R-tree or Quadtree)**

Geospatial indexing enables:
- Efficient "nearest K drivers within R radius" queries
- O(log n) spatial lookups
- Range-based and proximity queries

*Trade-offs:*
- Simple array requires O(n) scan every query
- HashMap doesn't support range queries
- Priority queue needs full recalculation on location changes

---

### Question 15
**Answer: B) HashMap mapping start position to end position**

Simple and efficient:
```
{2: 38, 5: 14, ...}  // ladders
{16: 6, 47: 26, ...}  // snakes
```

*Trade-offs:*
- 2D array wastes space for sparse snakes/ladders
- Linked list requires O(n) lookup
- Graph is overkill for simple position mapping

---

## Section 2: Class Relationships

### Question 16
**Answer: A) Composition - floors cannot exist without the parking lot**

ParkingFloor is part of a specific ParkingLot:
- Created when parking lot is built
- Destroyed when parking lot is demolished
- Cannot belong to multiple parking lots

---

### Question 17
**Answer: B) Composition**

OrderItem belongs to exactly one Order:
- Created with the order
- Deleted when order is deleted
- No meaning outside its order context

---

### Question 18
**Answer: C) Car extends Vehicle, Motorcycle extends Vehicle**

Proper inheritance hierarchy:
- Vehicle is the base class (abstraction)
- Car and Motorcycle are specializations
- IS-A relationship: Car IS-A Vehicle

---

### Question 19
**Answer: C) Library notifies subscribed Members about due books**

Observer pattern implementation:
- Library (Subject) tracks due books
- Members (Observers) subscribe to notifications
- Library notifies all subscribers when books are due

---

### Question 20
**Answer: B) One-to-Many**

Banking relationship (assuming no joint accounts):
- One User can have multiple Accounts (savings, checking, loan)
- Each Account belongs to exactly one User
- If the system must support joint accounts, the relationship becomes Many-to-Many (Users ↔ Accounts), typically modeled via an intermediate entity like `AccountHolder`

---

### Question 21
**Answer: B) Composition - moves belong to specific game**

Moves are integral to a game:
- Created during the game
- Have no meaning outside game context
- Deleted when game record is deleted

---

### Question 22
**Answer: D) Both A and B apply together**

Combined relationship:
- Thread CONTAINS Comments (composition - thread owns comments)
- Comment REFERENCES Thread (association - needs to navigate back)
- Comments can't exist without parent thread

---

### Question 23
**Answer: D) Mediator pattern relationship**

ElevatorController acts as Mediator:
- Coordinates between multiple elevators
- Handles request distribution
- Prevents direct elevator-to-elevator communication

---

### Question 24
**Answer: D) Both B and C are valid approaches**

Both designs satisfy Open/Closed Principle:
- **Abstract class hierarchy**: Uses inheritance for payment types
- **Strategy interface**: Uses composition for swappable payment strategies
- Strategy is generally preferred for flexibility

---

### Question 25
**Answer: B) NotificationChannel interface with implementations**

Interface-based design:
- NotificationChannel interface with send() method
- EmailChannel, SMSChannel, PushChannel implementations
- New channels added without modifying existing code

---

## Section 3: Trade-offs & Scaling

### Question 26
**Answer: A) Optimistic locking with retry on conflict**

For high-traffic system:
- Most users are browsing, not booking (read-heavy)
- Optimistic locking avoids holding locks for the full transaction and detects conflicts at commit time
- Retry on occasional write conflict is acceptable for booking operations

*Trade-offs:*
- Pessimistic locking acquires locks up front, increasing lock wait times and reducing throughput under high concurrency
- High read-to-write ratio favors optimistic locking because write conflicts are relatively rare

---

### Question 27
**Answer: C) Check and decrement inventory atomically at checkout**

Atomic operation ensures consistency:
```sql
UPDATE inventory
SET count = CASE WHEN count > 0 THEN count - 1 ELSE count END
WHERE product_id = ?;
```

*Trade-offs:*
- Reservation on add-to-cart holds inventory too long
- Row locking blocks other checkouts
- Overselling creates customer service issues

---

### Question 28
**Answer: D) B and C combined**

Optimal matching strategy:
- Grid cells reduce search space
- Geospatial index enables efficient queries within cells
- Combined approach scales to city level

*Trade-offs:*
- Query all drivers doesn't scale
- Grid alone has edge-case issues
- Hybrid provides best balance

---

### Question 29
**Answer: C) Both Memento and Command**

Complete move history requires:
- **Command**: Encapsulates each move with undo capability
- **Memento**: Stores board state snapshots for replay

*Trade-offs:*
- Command alone requires reverse calculation for replay
- Memento alone doesn't provide undo granularity
- Combined gives full flexibility

---

### Question 30
**Answer: D) All are valid with different trade-offs**

Trade-offs by approach:
| Approach | Pro | Con |
|----------|-----|-----|
| Auto-increment | Predictable, sequential | Needs central counter |
| Random string | No coordination needed | Collision checks needed |
| Hash truncation | Deterministic | Collision risk |

---

### Question 31
**Answer: D) All of the above**

Distributed rate limiting challenges:
- Clock drift affects window calculations
- Shared counter creates single point of failure
- Network latency allows temporary over-limit

*Solution:* Accept some inaccuracy, use local counters with periodic sync.

---

### Question 32
**Answer: D) B is simpler, C is more efficient for complex queries**

Trade-off analysis:
- **Range overlap query**: Simple, works for basic cases
- **Interval tree**: O(log n) for complex overlapping queries

*Recommendation:* Start with B, optimize to C if needed.

---

### Question 33
**Answer: D) All are valid depending on access patterns**

Analysis:
- **Real-time**: Best for small groups, infrequent updates
- **Stored**: Best for large groups, frequent reads
- **Hybrid**: Best for mixed patterns

---

### Question 34
**Answer: D) All of the above**

Distributed LRU cache challenges:
- LRU order is hard to maintain across nodes
- Consistent hashing determines key placement
- Cache coherence requires invalidation protocol

---

### Question 35
**Answer: D) Hybrid - push to server, clients pull/subscribe**

Optimal architecture:
- Sensors push updates to server (real-time data)
- Server aggregates and processes
- Clients subscribe via WebSocket or poll REST

*Trade-offs:*
- Pure push overloads clients with updates
- Pure pull misses immediate changes

---

### Question 36
**Answer: D) Depends on business requirements**

Decision factors:
| Requirement | Best Choice |
|-------------|-------------|
| Guest checkout | Session/Cookie |
| Persistent cart | Database |
| Performance + persistence | Redis |
| Cross-device sync | Database |

---

### Question 37
**Answer: D) Destination dispatch grouping**

Modern optimization:
- Groups passengers by destination floor
- Assigns to optimal elevator
- Reduces total wait + travel time

*Trade-offs:*
- FCFS is unfair to some users
- SSTF can cause starvation
- SCAN is good but destination dispatch is better

---

### Question 38
**Answer: D) Depends on typical access patterns**

Decision factors:
- List view showing many books → eager load status
- Detail view of single book → can lazy load
- Search results → eager load essentials

---

### Question 39
**Answer: D) Depends on expected concurrency**

Trade-off analysis:
- Low concurrency → show all, simpler UX
- High concurrency → real-time updates prevent frustration
- Very high → show only available to reduce conflicts

---

### Question 40
**Answer: D) All valid, choice depends on freshness requirements**

Trade-off analysis:
- **Pre-computed**: Fast, stale rankings acceptable
- **Real-time**: Fresh but slow for every request
- **Hybrid**: Pre-computed base with real-time adjustments (restaurant open/closed, surge pricing)

---

## Section 4: Concurrency Deep Dives

### Question 41
**Answer: C) Seat availability check + lock transition together**

The race is between visibility and ownership transition.  
Checking availability and locking must happen in the same critical section.

---

### Question 42
**Answer: B) Atomic read-modify-write for each key update**

Counter decisions are correctness-sensitive shared writes.  
Split read/update phases can over-admit under contention.

---

### Question 43
**Answer: B) Acquire both locks in deterministic order**

Deterministic lock ordering removes circular-wait opportunities and is the standard deadlock mitigation for multi-resource updates.

---

### Question 44
**Answer: C) Use bounded queue with explicit backpressure policy**

Bounded queues make overload behavior explicit and controllable.  
Unbounded queues delay failure until latency and memory collapse.

---

### Question 45
**Answer: C) Coordinated stop signal with drain/timeout policy**

Graceful shutdown should stop intake and finish/timeout in-flight work predictably.  
Hard kills and implicit exits lose work and state integrity.

---

### Question 46
**Answer: B) Release in `finally`/defer block regardless of path**

Permit release must happen on success, failure, and timeout paths.  
This keeps scarcity accounting correct and prevents long-tail starvation.

---

### Question 47
**Answer: B) Return explicit failure and caller backoff guidance**

Timeout should fail fast with clear retry guidance.  
Infinite waiting under contention destroys latency SLOs.

---

### Question 48
**Answer: B) When operations can be partitioned by key/owner safely**

Thread confinement removes shared-write contention for partitionable workloads.  
Locks remain useful, but confinement often yields simpler correctness and throughput.

---

## Section 5: New Project Drills

### Question 49
**Answer: C) Keep `Board` responsible for grid rules and `Game` for lifecycle/turn state**

This split preserves SRP and makes v2/v3 changes additive:
- `Board`: placement gravity, column validity, win checks
- `Game`: turn ownership, terminal states, winner, move history orchestration

---

### Question 50
**Answer: B) Track immutable move history and clear only the last placed cell**

Undo should be local and deterministic:
- O(1) rollback of the most recent move
- Clear ownership of what gets reverted
- Works cleanly with future replay/session features

---

### Question 51
**Answer: B) It lets exact and fallback selection evolve without rewriting `Locker`**

Policy extraction protects core orchestration from branching explosion:
- Swap exact/fallback/zone-aware selectors
- Test selection behavior independently
- Keep locker lifecycle logic stable

---

### Question 52
**Answer: C) Deterministic expiry testing without sleeps or flaky timing**

Injectable clocks make reservation and token TTL behavior reproducible:
- No real-time waiting in tests
- Clear control of boundary conditions
- Stable CI execution

---

<p align="center">
  <b>Score Interpretation</b><br>
  47-52: Excellent | 39-46: Good | 31-38: Fair | 0-30: Review needed
</p>
