# 🏗️ LLD Projects Quiz

> **52 questions to test your low-level design knowledge**
> 
> ⏱️ Time: 60 minutes | ⭐⭐⭐⭐ Difficulty

---

## Section 1: Design Decisions (15 questions)

*Choose the best design approach for each LLD scenario.*

---

### Question 1 ⭐⭐
**Parking Lot System:** How should you handle concurrent booking of the same parking spot by multiple users?

**A)** Use synchronized methods on the ParkingSpot class
**B)** Optimistic locking with version numbers
**C)** Pessimistic locking with database row locks
**D)** First-come-first-served with no locking

---

### Question 2 ⭐⭐
**LRU Cache:** What data structure combination provides O(1) for both get and put operations?

**A)** Array + Binary Search Tree
**B)** HashMap + Doubly Linked List
**C)** HashMap + Array
**D)** Linked List + Stack

---

### Question 3 ⭐⭐
**Elevator System:** Which pattern best models an elevator's behavior (idle, moving up, moving down, door open)?

**A)** Strategy Pattern
**B)** State Pattern
**C)** Command Pattern
**D)** Observer Pattern

---

### Question 4 ⭐⭐
**Rate Limiter:** For memory-efficient rate limiting at scale, which algorithm would you choose?

**A)** Fixed Window Counter
**B)** Sliding Window Log
**C)** Token Bucket
**D)** Sliding Window Counter

---

### Question 5 ⭐⭐
**Chess Game:** How should you model the relationship between Board and Pieces?

**A)** Board inherits from Piece
**B)** Piece inherits from Board
**C)** Board has composition of Pieces
**D)** Board has aggregation of Pieces

---

### Question 6 ⭐⭐⭐
**Hotel Reservation:** For preventing double booking of rooms, what's the recommended approach?

**A)** Check availability then book in two separate transactions
**B)** Use database unique constraint on (room_id, date)
**C)** Lock the entire rooms table during booking
**D)** Use eventual consistency with conflict resolution

---

### Question 7 ⭐⭐⭐
**Library Management:** How would you model the relationship between Library and Book?

**A)** Aggregation - books can exist without library
**B)** Composition - books cannot exist without library
**C)** Inheritance - Book extends Library
**D)** Association - no ownership relationship

---

### Question 8 ⭐⭐⭐
**Vending Machine:** What's the best way to handle state transitions (idle → coin inserted → item selected → dispensing)?

**A)** If-else statements in a single class
**B)** Switch statement with enum states
**C)** State pattern with separate state classes
**D)** Strategy pattern with different behaviors

---

### Question 9 ⭐⭐⭐
**Tic-Tac-Toe:** How would you efficiently check for a winner after each move?

**A)** Scan entire board after each move
**B)** Track row, column, and diagonal counts per player
**C)** Use AI minimax algorithm
**D)** Store all winning combinations and compare

---

### Question 10 ⭐⭐⭐
**ATM System:** Which pattern would you use for the transaction flow (authenticate → select operation → process → dispense)?

**A)** Chain of Responsibility
**B)** State Pattern
**C)** Template Method
**D)** Strategy Pattern

---

### Question 11 ⭐⭐⭐
**Splitwise:** How would you optimize debt simplification among a group of friends?

**A)** Store all individual transactions
**B)** Use graph-based debt simplification algorithm
**C)** Calculate net balance per person
**D)** Both B and C

---

### Question 12 ⭐⭐⭐⭐
**File System:** How would you model files and directories using design patterns?

**A)** Decorator Pattern
**B)** Composite Pattern
**C)** Flyweight Pattern
**D)** Bridge Pattern

---

### Question 13 ⭐⭐⭐⭐
**Movie Ticket Booking:** To prevent race conditions when booking seats, what's the most reliable approach?

**A)** Optimistic locking with retry
**B)** Pessimistic locking on seat rows
**C)** Distributed lock with Redis
**D)** All of the above can work, choice depends on scale

---

### Question 14 ⭐⭐⭐⭐
**Ride Sharing:** For efficient driver-rider matching, what data structure would you use?

**A)** Simple array of available drivers
**B)** Geospatial index (R-tree or Quadtree)
**C)** Hash map with location as key
**D)** Priority queue sorted by distance

---

### Question 15 ⭐⭐⭐⭐
**Snake and Ladder:** How would you model the game board with snakes and ladders?

**A)** 2D array with snake/ladder objects
**B)** HashMap mapping start position to end position
**C)** Linked list of board cells
**D)** Graph with weighted edges

---

## Section 2: Class Relationships (10 questions)

*Identify the correct relationship between classes.*

---

### Question 16 ⭐⭐
What is the relationship between ParkingLot and ParkingFloor?

**A)** Composition - floors cannot exist without the parking lot
**B)** Aggregation - floors can exist independently
**C)** Association - simple reference
**D)** Inheritance - ParkingFloor extends ParkingLot

---

### Question 17 ⭐⭐
What is the relationship between Order and OrderItem in an e-commerce system?

**A)** Aggregation
**B)** Composition
**C)** Association
**D)** Dependency

---

### Question 18 ⭐⭐
Which inheritance hierarchy is correct for a Vehicle class?

**A)** Car extends Engine extends Vehicle
**B)** Vehicle extends Car, Vehicle extends Motorcycle
**C)** Car extends Vehicle, Motorcycle extends Vehicle
**D)** Vehicle extends Transport, Car extends Transport

---

### Question 19 ⭐⭐⭐
In a Library system, how would you implement the Observer pattern for due date notifications?

**A)** Book notifies Member when due date approaches
**B)** Member polls Library for due books
**C)** Library notifies subscribed Members about due books
**D)** Loan object notifies both Library and Member

---

### Question 20 ⭐⭐⭐
What is the relationship between User and Account in a banking system?

**A)** One-to-One
**B)** One-to-Many
**C)** Many-to-Many
**D)** Inheritance

---

### Question 21 ⭐⭐⭐
In a Chess game, what relationship should exist between Game and Move?

**A)** Aggregation - moves exist independently
**B)** Composition - moves belong to specific game
**C)** Association - no ownership
**D)** Inheritance - Move extends Game

---

### Question 22 ⭐⭐⭐
How should you model the relationship between Thread and Comment in a forum?

**A)** Thread contains Comments (Composition)
**B)** Comment references Thread (Association)
**C)** Comments can exist without Thread (Aggregation)
**D)** Both A and B apply together

---

### Question 23 ⭐⭐⭐⭐
In an Elevator system, what's the relationship between ElevatorController and Elevator?

**A)** Composition - controller owns elevators
**B)** Aggregation - elevators exist independently
**C)** One-to-Many association
**D)** Mediator pattern relationship

---

### Question 24 ⭐⭐⭐⭐
For a Payment processing system with multiple payment methods, which design is correct?

**A)** Payment class with type field and switch statements
**B)** Abstract Payment with CreditCard, PayPal subclasses
**C)** PaymentStrategy interface with implementations
**D)** Both B and C are valid approaches

---

### Question 25 ⭐⭐⭐⭐
In a Notification system supporting Email, SMS, Push, what pattern maintains Open/Closed Principle?

**A)** Single NotificationService with multiple methods
**B)** NotificationChannel interface with implementations
**C)** Decorator pattern wrapping base notification
**D)** Factory creating different notification types

---

## Section 3: Trade-offs & Scaling (15 questions)

*Analyze design trade-offs for scaling and performance.*

---

### Question 26 ⭐⭐
**Movie Booking:** To prevent double booking, which locking strategy would you use for a high-traffic system?

**A)** Optimistic locking - allows more concurrent reads
**B)** Pessimistic locking - guarantees no conflicts
**C)** No locking - handle duplicates in application
**D)** Optimistic with pessimistic fallback

---

### Question 27 ⭐⭐
**Shopping Cart:** How would you handle concurrent inventory updates when multiple users buy the same item?

**A)** Lock inventory row during checkout
**B)** Reserve inventory on add-to-cart
**C)** Check and decrement inventory atomically at checkout
**D)** Allow overselling and handle backorders

---

### Question 28 ⭐⭐⭐
**Ride Sharing:** For matching drivers to riders efficiently at scale, what's the best approach?

**A)** Query all available drivers and sort by distance
**B)** Use geospatial index with bounded radius search
**C)** Partition city into grid cells
**D)** B and C combined

---

### Question 29 ⭐⭐⭐
**Chess Game:** To store complete move history for undo/redo and replay, which pattern would you use?

**A)** Memento Pattern
**B)** Command Pattern
**C)** Both Memento and Command
**D)** State Pattern

---

### Question 30 ⭐⭐⭐
**URL Shortener (LLD):** How would you generate unique short codes efficiently?

**A)** Auto-increment ID converted to base62
**B)** Random string with collision check
**C)** MD5 hash of URL truncated
**D)** All are valid with different trade-offs

---

### Question 31 ⭐⭐⭐
**Rate Limiter:** For distributed rate limiting across multiple servers, what's the challenge?

**A)** Clock synchronization between servers
**B)** Centralized counter becomes bottleneck
**C)** Network latency affects accuracy
**D)** All of the above

---

### Question 32 ⭐⭐⭐
**Hotel Booking:** For checking room availability across a date range, what's the most efficient approach?

**A)** Store booking for each day individually
**B)** Store start and end dates, query with range overlap
**C)** Use interval tree data structure
**D)** B is simpler, C is more efficient for complex queries

---

### Question 33 ⭐⭐⭐⭐
**Splitwise:** For a group expense app, what's the trade-off between real-time balance calculation vs stored balances?

**A)** Real-time: consistent but slow for large groups
**B)** Stored: fast reads but needs sync on writes
**C)** Hybrid: cache balances, invalidate on new expense
**D)** All are valid depending on access patterns

---

### Question 34 ⭐⭐⭐⭐
**LRU Cache:** When the cache needs to be distributed across multiple servers, what's the main challenge?

**A)** Ensuring LRU order across servers
**B)** Consistent hashing for key distribution
**C)** Cache coherence and invalidation
**D)** All of the above

---

### Question 35 ⭐⭐⭐⭐
**Parking Lot:** For a smart parking system with sensor updates, would you prefer push or pull architecture?

**A)** Pull - clients poll for spot availability
**B)** Push - sensors send updates on change
**C)** Push with SSE/WebSocket to clients
**D)** Hybrid - push to server, clients pull/subscribe

---

### Question 36 ⭐⭐⭐⭐
**E-commerce Cart:** Should cart be stored in session (memory) or database?

**A)** Session - fast but lost on logout
**B)** Database - persistent but slower
**C)** Redis - fast and persistent
**D)** Depends on business requirements

---

### Question 37 ⭐⭐⭐⭐
**Elevator System:** For multiple elevators, what algorithm optimizes wait time?

**A)** FCFS - First Come First Served
**B)** SSTF - Shortest Seek Time First
**C)** SCAN/LOOK algorithm
**D)** Destination dispatch grouping

---

### Question 38 ⭐⭐⭐⭐
**Library Management:** For tracking book availability, would you use eager or lazy loading of book status?

**A)** Eager - load status with book details always
**B)** Lazy - load status only when needed
**C)** Eager for list views, lazy for detail views
**D)** Depends on typical access patterns

---

### Question 39 ⭐⭐⭐⭐
**Movie Ticket System:** Should you show only available seats or all seats with status?

**A)** Only available - simpler UI, less data
**B)** All with status - better UX, more data
**C)** All seats with real-time updates
**D)** Depends on expected concurrency

---

### Question 40 ⭐⭐⭐⭐
**Food Delivery:** For restaurant search, what's the trade-off between pre-computed rankings vs real-time calculation?

**A)** Pre-computed - faster but stale
**B)** Real-time - fresh but slow
**C)** Hybrid - pre-computed base, real-time adjustments
**D)** All valid, choice depends on freshness requirements

---

## Section 4: Concurrency Deep Dives (8 questions)

*Focused drills on correctness, coordination, and scarcity in LLD systems.*

---

### Question 41 ⭐⭐⭐
**Movie Ticket Booking:** Which boundary must be atomic to prevent seat double-booking under concurrency?

**A)** Only payment callback  
**B)** Only booking record insert  
**C)** Seat availability check + lock transition together  
**D)** Only seat-map read rendering

---

### Question 42 ⭐⭐⭐
**Rate Limiter:** What is the concurrency-safe approach for updating request counters?

**A)** Read count, then update later in separate call  
**B)** Atomic read-modify-write for each key update  
**C)** Cache count on client and sync every minute  
**D)** Randomly sample requests to reduce contention

---

### Question 43 ⭐⭐⭐
**Inventory-like transfer flow:** Which strategy best minimizes deadlocks with two shared resources?

**A)** Lock in whichever order requests arrive  
**B)** Acquire both locks in deterministic order  
**C)** Lock one resource and retry indefinitely  
**D)** Remove locks and rely on conflict logs

---

### Question 44 ⭐⭐⭐
**Job Scheduler:** When worker queues hit capacity, what is the strongest interview answer?

**A)** Keep queue unbounded for simplicity  
**B)** Drop requests silently  
**C)** Use bounded queue with explicit backpressure policy  
**D)** Spawn unlimited workers temporarily

---

### Question 45 ⭐⭐⭐
**Worker lifecycle:** Which shutdown model avoids stranded work and hung threads?

**A)** Hard-kill worker threads immediately  
**B)** Exit workers when queue appears empty once  
**C)** Coordinated stop signal with drain/timeout policy  
**D)** Disable retries and continue dispatch

---

### Question 46 ⭐⭐⭐⭐
**Semaphore-based permit gate:** What is mandatory to avoid permit leaks?

**A)** Release only on success path  
**B)** Release in `finally`/defer block regardless of path  
**C)** Skip release for timeout cases  
**D)** Periodically reset all permits

---

### Question 47 ⭐⭐⭐⭐
**Scarcity management:** What is the recommended behavior when permit acquisition times out?

**A)** Block forever until capacity returns  
**B)** Return explicit failure and caller backoff guidance  
**C)** Auto-upgrade to unlimited capacity  
**D)** Re-run request with highest priority

---

### Question 48 ⭐⭐⭐⭐
**Shared mutable state design:** When should thread confinement be preferred over shared locks?

**A)** Never; shared locks are always simpler  
**B)** When operations can be partitioned by key/owner safely  
**C)** Only in single-threaded demos  
**D)** Only when memory usage is low

---

## Section 5: New Project Drills (4 questions)

*Targeted checks for Connect Four and Amazon Locker design decisions.*

---

### Question 49 ⭐⭐
**Connect Four:** Which separation keeps the design easiest to evolve across v1/v2/v3?

**A)** Keep board mutation and turn orchestration in one `Game` class
**B)** Put all logic in `Board` and keep `Game` as DTO
**C)** Keep `Board` responsible for grid rules and `Game` for lifecycle/turn state
**D)** Move all validation into the player object

---

### Question 50 ⭐⭐⭐
**Connect Four v2:** What is the cleanest undo design?

**A)** Recompute the entire game from scratch after each undo
**B)** Track immutable move history and clear only the last placed cell
**C)** Allow undo only before anyone has won
**D)** Keep a mutable singleton move object and overwrite fields

---

### Question 51 ⭐⭐⭐
**Amazon Locker v2:** Why is allocation policy extraction important?

**A)** It avoids writing tests
**B)** It lets exact and fallback selection evolve without rewriting `Locker`
**C)** It guarantees O(1) allocation
**D)** It removes the need for compartment states

---

### Question 52 ⭐⭐⭐⭐
**Amazon Locker v3:** What is the strongest reason to inject a clock for reservation/token flows?

**A)** Faster production performance
**B)** Better UI rendering
**C)** Deterministic expiry testing without sleeps or flaky timing
**D)** Smaller object graph

---

## 📋 Answer Sheet

Mark your answers:

```
Section 1: Design Decisions
1.  [  ]    6.  [  ]    11. [  ]
2.  [  ]    7.  [  ]    12. [  ]
3.  [  ]    8.  [  ]    13. [  ]
4.  [  ]    9.  [  ]    14. [  ]
5.  [  ]    10. [  ]    15. [  ]

Section 2: Class Relationships
16. [  ]    21. [  ]
17. [  ]    22. [  ]
18. [  ]    23. [  ]
19. [  ]    24. [  ]
20. [  ]    25. [  ]

Section 3: Trade-offs & Scaling
26. [  ]    31. [  ]    36. [  ]
27. [  ]    32. [  ]    37. [  ]
28. [  ]    33. [  ]    38. [  ]
29. [  ]    34. [  ]    39. [  ]
30. [  ]    35. [  ]    40. [  ]

Section 4: Concurrency Deep Dives
41. [  ]    44. [  ]    47. [  ]
42. [  ]    45. [  ]    48. [  ]
43. [  ]    46. [  ]

Section 5: New Project Drills
49. [  ]    51. [  ]
50. [  ]    52. [  ]
```

**Score:** _____ / 52

**Check answers in:** `answers/lld-projects-answers.md`

---

<p align="center">
  <b>Good luck! 🍀</b>
</p>
