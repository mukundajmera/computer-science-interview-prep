# 🎤 LLD Interview Q&A

Focused follow-up bank for low-level design rounds.

---

## 40+ Graded Interview Questions

### Q1: How would you handle duplicate ad click events in real-time aggregation?
**Weak Answer:** "I would just sum everything up as it comes in."

**Strong Answer:** "I would use an exactly-once or at-least-once with deduplication window strategy, and leverage a distinct event ID constraint or hyperloglog for counts."
```java
// Example for ad-click-aggregator
public class AdClickAggregatorService {
    public void processEvent(Event e) {
        // Implementation
    }
}
```
**Reference:** [ad-click-aggregator](./ad-click-aggregator/README.md)

---

### Q2: How do you map packages to available lockers optimally?
**Weak Answer:** "I would loop through all lockers until I find an empty one."

**Strong Answer:** "I would use a spatial or size-based allocation strategy mapping `PackageSize` to `LockerSize`, maintaining an indexed collection of available lockers."
```java
// Example for amazon-locker
public class LockerAllocationStrategy {
    public Locker allocate(Package pkg) {
        // Implementation
    }
}
```
**Reference:** [amazon-locker](./amazon-locker/README.md)

---

### Q3: How would you enforce rate limiting per tenant in the API Gateway?
**Weak Answer:** "I would write an if condition checking if the request count is > 100."

**Strong Answer:** "I would use a Token Bucket or Leaky Bucket algorithm backed by Redis for distributed rate limiting per API key."
```java
// Example for api-gateway
public class RateLimiterFilter {
    public boolean isAllowed(Request req) {
        // Implementation
    }
}
```
**Reference:** [api-gateway](./api-gateway/README.md)

---

### Q4: How do you handle money dispensing transactions if the machine crashes mid-operation?
**Weak Answer:** "I would just deduct the money first and then dispense."

**Strong Answer:** "I would implement a two-phase commit or transactional state machine to ensure the user's account is only debited upon successful physical dispense."
```java
// Example for atm-system
public class TransactionManager {
    public void execute(Transaction t) {
        // Implementation
    }
}
```
**Reference:** [atm-system](./atm-system/README.md)

---

### Q5: How do you prevent double booking of the same car?
**Weak Answer:** "I would search the database for overlapping bookings."

**Strong Answer:** "I would implement an inventory lock or constraint using a unique constraint on `(car_id, booking_date)` to prevent overlapping reservations."
```java
// Example for car-rental
public class BookingService {
    public Reservation book(Car c, Date d) {
        // Implementation
    }
}
```
**Reference:** [car-rental](./car-rental/README.md)

---

### Q6: How would you design the validation of complex piece movements like castling?
**Weak Answer:** "I would put all the move rules in one big function."

**Strong Answer:** "I would use the Strategy pattern for piece movements and a specialized `MoveValidator` that checks the board state, including castling prerequisites like king/rook movement history."
```java
// Example for chess-game
public class MoveValidator {
    public boolean isValid(Move m) {
        // Implementation
    }
}
```
**Reference:** [chess-game](./chess-game/README.md)

---

### Q7: How do you manage the state transitions from Open to Half-Open?
**Weak Answer:** "I would use a timer in a loop to check when to change state."

**Strong Answer:** "I would use the State pattern where the `OpenState` uses an expiration threshold to transition to `HalfOpenState` upon the next incoming request."
```java
// Example for circuit-breaker
public class CircuitBreakerState {
    public void onSuccess() {
        // Implementation
    }
}
```
**Reference:** [circuit-breaker](./circuit-breaker/README.md)

---

### Q8: How would you optimally detect a win condition after every move?
**Weak Answer:** "I would scan the entire board after every single move."

**Strong Answer:** "I would only check the row, column, and diagonals intersecting the most recently placed piece, which reduces the check to O(1) space."
```java
// Example for connect-four
public class WinChecker {
    public boolean checkWin(int r, int c) {
        // Implementation
    }
}
```
**Reference:** [connect-four](./connect-four/README.md)

---

### Q9: How would you design the card shuffling algorithm?
**Weak Answer:** "I would use a random number generator to pick cards."

**Strong Answer:** "I would use the Fisher-Yates shuffle algorithm to ensure an unbiased permutation of the deck in O(n) time."
```java
// Example for deck-of-cards
public class DeckManager {
    public void shuffle() {
        // Implementation
    }
}
```
**Reference:** [deck-of-cards](./deck-of-cards/README.md)

---

### Q10: How do you mitigate write contention for a global distributed counter?
**Weak Answer:** "I would use a single database row and lock it."

**Strong Answer:** "I would use counter sharding, maintaining an array of counters and incrementing a random shard, then aggregating them on read."
```java
// Example for distributed-counter
public class ShardedCounter {
    public void increment() {
        // Implementation
    }
}
```
**Reference:** [distributed-counter](./distributed-counter/README.md)

---

### Q11: How do you push configuration updates to thousands of clients?
**Weak Answer:** "I would have them poll the database every second."

**Strong Answer:** "I would use an event-driven publish/subscribe mechanism or long-polling (SSE) to notify subscribed clients when specific config keys change."
```java
// Example for dynamic-config-service
public class ConfigNotifier {
    public void notify(String key) {
        // Implementation
    }
}
```
**Reference:** [dynamic-config-service](./dynamic-config-service/README.md)

---

### Q12: What algorithm would you use to assign an elevator to a request?
**Weak Answer:** "I would just assign the closest elevator."

**Strong Answer:** "I would use a scan algorithm (like the LOOK algorithm) to serve requests in the current direction before changing direction to minimize average wait time."
```java
// Example for elevator-system
public class ElevatorDispatcher {
    public void dispatch(Request r) {
        // Implementation
    }
}
```
**Reference:** [elevator-system](./elevator-system/README.md)

---

### Q13: How do you represent a nested directory structure in memory?
**Weak Answer:** "I would use a flat list and parse strings."

**Strong Answer:** "I would use the Composite design pattern to treat files and directories uniformly as `FileSystemNode` objects."
```java
// Example for file-system
public class DirectoryNode {
    public void add(FileSystemNode n) {
        // Implementation
    }
}
```
**Reference:** [file-system](./file-system/README.md)

---

### Q14: How would you avoid massive switch-case statements for state transitions?
**Weak Answer:** "I would use if-else chains instead."

**Strong Answer:** "I would encapsulate each state as a separate class using the State pattern or define transitions in a configuration map/table."
```java
// Example for finite-state-machine
public class StateTransitionTable {
    public State next(State curr, Event e) {
        // Implementation
    }
}
```
**Reference:** [finite-state-machine](./finite-state-machine/README.md)

---

### Q15: How would you calculate ETA dynamically for food delivery?
**Weak Answer:** "I would just add 30 minutes to current time."

**Strong Answer:** "I would combine the restaurant prep time and the courier's route distance using a routing API and adjust based on real-time traffic updates."
```java
// Example for food-delivery-system
public class ETACalculator {
    public int calculate(Order o) {
        // Implementation
    }
}
```
**Reference:** [food-delivery-system](./food-delivery-system/README.md)

---

### Q16: How do you handle room pricing that changes dynamically by season?
**Weak Answer:** "I would hardcode prices for each month."

**Strong Answer:** "I would implement a dynamic pricing strategy using the Strategy pattern that takes temporal rules and current occupancy into account."
```java
// Example for hotel-management-system
public class PricingStrategy {
    public double getPrice(Room r, Date d) {
        // Implementation
    }
}
```
**Reference:** [hotel-management-system](./hotel-management-system/README.md)

---

### Q17: How do you handle subscriber errors so they don't crash the event bus?
**Weak Answer:** "I would wrap the event bus in a try-catch."

**Strong Answer:** "I would isolate subscriber execution, potentially using an ExecutorService, and log/handle exceptions individually without disrupting other subscribers."
```java
// Example for in-memory-event-bus
public class EventDispatcher {
    public void dispatch(Event e) {
        // Implementation
    }
}
```
**Reference:** [in-memory-event-bus](./in-memory-event-bus/README.md)

---

### Q18: How do you efficiently generate news feeds for users with millions of followers (celebrities)?
**Weak Answer:** "I would use a simple pull model for everyone."

**Strong Answer:** "I would use a hybrid approach (Push/Pull), pushing posts to active followers but requiring users to pull posts from celebrities to avoid massive fanout."
```java
// Example for instagram-core
public class FeedGenerator {
    public List<Post> getFeed(User u) {
        // Implementation
    }
}
```
**Reference:** [instagram-core](./instagram-core/README.md)

---

### Q19: How do you prevent stockouts when multiple concurrent orders are placed?
**Weak Answer:** "I would just check inventory and decrement sequentially."

**Strong Answer:** "I would use optimistic concurrency control (versioning) or explicit row-level locking (`SELECT FOR UPDATE`) when decrementing stock."
```java
// Example for inventory-management
public class InventoryService {
    public boolean reserve(Item i, int q) {
        // Implementation
    }
}
```
**Reference:** [inventory-management](./inventory-management/README.md)

---

### Q20: How do you guarantee a scheduled job is executed exactly once?
**Weak Answer:** "I would just set a flag when it runs."

**Strong Answer:** "I would use a distributed lock (like ZooKeeper or Redis) combined with an idempotent execution state stored in the database."
```java
// Example for job-scheduler
public class JobExecutor {
    public void execute(Job j) {
        // Implementation
    }
}
```
**Reference:** [job-scheduler](./job-scheduler/README.md)

---

### Q21: How do you manage the growth of the memtable before it consumes too much RAM?
**Weak Answer:** "I would just keep increasing the JVM heap."

**Strong Answer:** "I would implement a size threshold to flush the active memtable to an SSTable on disk while continuing to serve reads/writes with a new active memtable."
```java
// Example for key-value-store-lsm
public class MemtableManager {
    public void flush() {
        // Implementation
    }
}
```
**Reference:** [key-value-store-lsm](./key-value-store-lsm/README.md)

---

### Q22: How do you track overdue books and calculate fines?
**Weak Answer:** "I would loop through all books every day."

**Strong Answer:** "I would run a daily cron job that queries for active loans past their due date and applies a fine strategy per user type."
```java
// Example for library-management
public class FineCalculator {
    public double calculate(Loan l) {
        // Implementation
    }
}
```
**Reference:** [library-management](./library-management/README.md)

---

### Q23: How do you find the degree of connection (1st, 2nd, 3rd) between two users?
**Weak Answer:** "I would query the database with nested loops."

**Strong Answer:** "I would model connections as a graph and use Bidirectional Breadth-First Search (BFS) for an optimized shortest path lookup."
```java
// Example for linkedin-connection
public class ConnectionFinder {
    public int getDegree(User u1, User u2) {
        // Implementation
    }
}
```
**Reference:** [linkedin-connection](./linkedin-connection/README.md)

---

### Q24: How do you stream thousands of comments per second to viewers?
**Weak Answer:** "I would have clients poll a REST endpoint."

**Strong Answer:** "I would use WebSockets or Server-Sent Events (SSE) combined with a pub/sub message broker (like Redis Pub/Sub) to push comments efficiently."
```java
// Example for live-comments
public class CommentStreamer {
    public void stream(Comment c) {
        // Implementation
    }
}
```
**Reference:** [live-comments](./live-comments/README.md)

---

### Q25: How do you ensure logging doesn't block the main application thread?
**Weak Answer:** "I would just write to System.out directly."

**Strong Answer:** "I would use an asynchronous appender with a bounded concurrent queue (like an LMAX Disruptor or ArrayBlockingQueue) and a background worker to flush to disk."
```java
// Example for logging-framework
public class AsyncAppender {
    public void append(LogEvent e) {
        // Implementation
    }
}
```
**Reference:** [logging-framework](./logging-framework/README.md)

---

### Q26: What data structures would you use to achieve O(1) operations for an LRU Cache?
**Weak Answer:** "I would use an ArrayList and a HashMap."

**Strong Answer:** "I would use a combination of a HashMap for O(1) lookups and a Doubly Linked List for O(1) evictions and promotions."
```java
// Example for lru-cache
public class LRUCache {
    public void put(Key k, Value v) {
        // Implementation
    }
}
```
**Reference:** [lru-cache](./lru-cache/README.md)

---

### Q27: How do you efficiently evaluate thousands of price alerts against a real-time stock ticker?
**Weak Answer:** "I would iterate through all alerts for every price tick."

**Strong Answer:** "I would organize alerts using an interval tree or bucketed map indexed by ticker symbol to only evaluate relevant alerts."
```java
// Example for market-alert-engine
public class AlertEvaluator {
    public void evaluate(Tick t) {
        // Implementation
    }
}
```
**Reference:** [market-alert-engine](./market-alert-engine/README.md)

---

### Q28: How do you find the earliest available time slot for multiple participants?
**Weak Answer:** "I would check every hour of the day for all people."

**Strong Answer:** "I would merge the busy intervals of all participants, invert the intervals, and then find the first gap that fits the required duration."
```java
// Example for meeting-room-scheduler
public class ScheduleFinder {
    public TimeSlot find(List<User> users) {
        // Implementation
    }
}
```
**Reference:** [meeting-room-scheduler](./meeting-room-scheduler/README.md)

---

### Q29: How do you ensure consumer offsets are committed reliably in a message queue?
**Weak Answer:** "I would just commit after reading."

**Strong Answer:** "I would provide at-least-once semantics by committing the offset explicitly only after the consumer has fully processed the message."
```java
// Example for message-queue
public class OffsetManager {
    public void commit(long offset) {
        // Implementation
    }
}
```
**Reference:** [message-queue](./message-queue/README.md)

---

### Q30: How do you hold a seat for a user during the checkout process?
**Weak Answer:** "I would just mark it sold."

**Strong Answer:** "I would assign the seat a 'Locked' state with a TTL (e.g., 10 minutes) using Redis; if payment fails, the lock expires and the seat becomes available."
```java
// Example for movie-ticket-booking
public class SeatLockManager {
    public boolean lock(Seat s) {
        // Implementation
    }
}
```
**Reference:** [movie-ticket-booking](./movie-ticket-booking/README.md)

---

### Q31: How would you design the cache to easily swap between LRU and LFU policies?
**Weak Answer:** "I would write an if-else statement for each cache operation."

**Strong Answer:** "I would use the Strategy pattern to define a common `EvictionPolicy` interface, allowing the cache to dynamically switch policies at runtime."
```java
// Example for multi-policy-cache
public class CacheContext {
    public void setPolicy(EvictionPolicy p) {
        // Implementation
    }
}
```
**Reference:** [multi-policy-cache](./multi-policy-cache/README.md)

---

### Q32: How do you handle user preferences for receiving notifications across multiple channels (Email, SMS)?
**Weak Answer:** "I would just hardcode checks for each channel."

**Strong Answer:** "I would load the user's `NotificationPreference` and use a factory or strategy pattern to route the message to the appropriate channel adapters."
```java
// Example for notification-service
public class NotificationRouter {
    public void route(Message m) {
        // Implementation
    }
}
```
**Reference:** [notification-service](./notification-service/README.md)

---

### Q33: How do you handle rapid bidding in the last 10 seconds of an auction?
**Weak Answer:** "I would just use standard database updates."

**Strong Answer:** "I would buffer bids in an in-memory datastore like Redis to handle high write throughput, and apply optimistic locking to reject lower bids."
```java
// Example for online-auction
public class BidProcessor {
    public boolean placeBid(Bid b) {
        // Implementation
    }
}
```
**Reference:** [online-auction](./online-auction/README.md)

---

### Q34: How do you safely execute untrusted user code?
**Weak Answer:** "I would just compile and run it in a try-catch block."

**Strong Answer:** "I would execute the code in isolated Docker containers or sandboxed processes with strict resource limits (CPU/Memory/Network) and timeouts."
```java
// Example for online-code-judge
public class CodeSandbox {
    public Result execute(Code c) {
        // Implementation
    }
}
```
**Reference:** [online-code-judge](./online-code-judge/README.md)

---

### Q35: How do you handle pricing rules like 'Buy 2 Get 1 Free'?
**Weak Answer:** "I would hardcode the logic in the calculate function."

**Strong Answer:** "I would use the Decorator or Rule pattern to apply sequential discount rules to the cart total, making it extensible."
```java
// Example for online-shopping-cart
public class DiscountEngine {
    public double apply(Cart c) {
        // Implementation
    }
}
```
**Reference:** [online-shopping-cart](./online-shopping-cart/README.md)

---

### Q36: How do you efficiently find the nearest available parking spot?
**Weak Answer:** "I would iterate over every spot on every floor."

**Strong Answer:** "I would maintain a Min-Heap or ordered sets per vehicle type/floor to retrieve the optimal available spot in O(1) or O(log n) time."
```java
// Example for parking-lot
public class SpotFinder {
    public Spot find(VehicleType t) {
        // Implementation
    }
}
```
**Reference:** [parking-lot](./parking-lot/README.md)

---

### Q37: How do you route payments when a specific third-party provider is down?
**Weak Answer:** "I would just fail the transaction."

**Strong Answer:** "I would use a Chain of Responsibility or a Fallback Strategy combined with a Circuit Breaker to reroute to the next available gateway."
```java
// Example for payment-gateway-router
public class PaymentRouter {
    public Result route(Payment p) {
        // Implementation
    }
}
```
**Reference:** [payment-gateway-router](./payment-gateway-router/README.md)

---

### Q38: How do you handle crawling a product page whose HTML layout frequently changes?
**Weak Answer:** "I would write specific regexes for every site."

**Strong Answer:** "I would abstract the parsing logic into modular `SiteAdapter` strategies, enabling rapid updates without affecting the core crawling engine."
```java
// Example for price-tracking-service
public class PageParser {
    public ProductData parse(Document d) {
        // Implementation
    }
}
```
**Reference:** [price-tracking-service](./price-tracking-service/README.md)

---

### Q39: How would you design a distributed sliding window rate limiter?
**Weak Answer:** "I would use a basic counter in memory."

**Strong Answer:** "I would use Redis Sorted Sets (ZSET), storing timestamps as scores, to efficiently count requests within the current sliding window."
```java
// Example for rate-limiter
public class SlidingWindowLimiter {
    public boolean allow(Request r) {
        // Implementation
    }
}
```
**Reference:** [rate-limiter](./rate-limiter/README.md)

---

### Q40: How do you manage table assignments for varying group sizes?
**Weak Answer:** "I would just pick any open table."

**Strong Answer:** "I would model table combinations, using an algorithm to find the optimal contiguous table arrangement that minimizes wasted seats."
```java
// Example for restaurant-management
public class TableManager {
    public List<Table> assign(int groupSize) {
        // Implementation
    }
}
```
**Reference:** [restaurant-management](./restaurant-management/README.md)

---

### Q41: How do you match riders with drivers efficiently?
**Weak Answer:** "I would loop through all drivers globally."

**Strong Answer:** "I would partition drivers using Geohash or Quadtrees (e.g., Uber's H3) to restrict the matching radius and find nearby drivers quickly."
```java
// Example for ride-sharing-system
public class Matcher {
    public Driver match(Rider r) {
        // Implementation
    }
}
```
**Reference:** [ride-sharing-system](./ride-sharing-system/README.md)

---

