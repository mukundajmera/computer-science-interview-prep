# Strong Answer: Online Auction

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Online Auction, I'll start by clarifying the core requirements, both functional and non-functional, before diving into the component architecture. We want to ensure the system is extensible, highly concurrent, and fault-tolerant."

## 2. Entity Modeling (10 mins)
**Say:** "Let's define the primary entities and their relationships. For this system, the domain models encapsulate the core business rules."
Key entities are `Auction`, `Bid`, `User`, `Item`, and `NotificationService`. The `Auction` maintains the state, end time, and the ledger of bids.

## 3. Data Structure Rationale (10 mins)
**Say:** "Choosing the right data structures is critical for meeting our latency and throughput requirements."
A `PriorityQueue` or `ConcurrentSkipListMap` stores bids sorted by amount, ensuring O(1) retrieval of the current highest bid. A `ConcurrentHashMap` tracks all globally active auctions.

## 4. Design Pattern Justifications (5 mins)
**Say:** "To keep the system modular and maintainable, I've applied specific design patterns."
The **Command Pattern** encapsulates bid submissions, allowing for queueing and auditing. The **Observer Pattern** is heavily utilized to notify all participating users in real-time when they are outbid.

## 5. Concurrency Defense & Thread-Safety Details (10 mins)
**Say:** "Given that this system will be accessed by multiple threads concurrently, ensuring thread safety without creating bottlenecks is a priority."
Bidding is intensely concurrent. I use an `AtomicReference` for the highest bid (Optimistic Concurrency) or a strict `ReentrantLock` on the `Auction` object. This ensures a new bid is only accepted if it's strictly greater than the current highest, avoiding race conditions during bid wars.

## 6. Auction Policies & Exact Money Representation (5 mins)
**Say:** "The system supports separate named policies: English proxy-bid tie order and Vickrey sealed-bid pricing. For English proxy bids, the winner pays an increment over the second highest bid. For Vickrey, the highest bidder pays the exact second highest bid. To prevent floating-point inaccuracies, money strictly uses exact units (e.g., long integer cents), and invalid amounts (zero or negative) are rejected."

## 7. Concurrency & Time-Based Extensions (5 mins)
**Say:** "We use injected deadline checks for deterministic transitions. Anti-snipe extension limits are enforced by checking an injected clock, ensuring the auction extends only if bids arrive within the final seconds, capped at a hard extension limit. Concurrent bids are serialized safely via locks."

## 8. Failure Handling & Consistency Boundaries (3 mins)
**Say:** "Systems fail, so we need to anticipate and handle failures gracefully at the lowest level."
We enforce consistency boundaries where late bids, duplicate IDs, and settlement replays cannot double-settle. Idempotency keys prevent duplicate operations, and settlement safely replays the terminal state.

## 9. Implementation Parity
### Java 11+ (Standard Library)
```java
// Simplified snippet highlighting the core logic
import java.util.*;

public class AuctionServiceV3 {
    private final Map<String, Auction> auctions = new HashMap<>();
    private final Object lock = new Object();
    
    public boolean placeBid(String auctionId, String bidderId, long amount, String idempotencyKey, double currentTime) {
        boolean isValidAmount = amount > 0;
        if (!isValidAmount) return false;
        
        synchronized (lock) {
            Auction auction = auctions.get(auctionId);
            if (auction == null || auction.state != AuctionState.OPEN) return false;
            if (currentTime > auction.endTime) return false;
            if (bidderId.equals(auction.sellerId)) return false;
            
            for (Bid bid : auction.bids) {
                if (idempotencyKey != null && !idempotencyKey.isEmpty() && idempotencyKey.equals(bid.idempotencyKey)) {
                    return true;
                }
            }
            
            // Validation and highest bid logic omitted for brevity
            
            auction.bids.add(new Bid(bidderId, amount, currentTime, idempotencyKey));
            
            // anti-snipe
            if (currentTime >= auction.endTime - auction.extensionWindow) {
                if (auction.extensionCount < auction.extensionLimit) {
                    auction.endTime += auction.extensionDuration;
                    auction.extensionCount++;
                }
            }
            
            return true;
        }
    }
}
```

### Python 3.8+ (Standard Library)
```python
import threading
from typing import Dict, Optional

class AuctionServiceV3:
    def __init__(self):
        self.auctions: Dict[str, 'Auction'] = {}
        self.lock = threading.RLock()

    def place_bid(self, auction_id: str, bidder_id: str, amount: int, idempotency_key: str, current_time: float) -> bool:
        is_valid_amount = isinstance(amount, int) and amount > 0
        if not is_valid_amount:
            return False

        with self.lock:
            auction = self.auctions.get(auction_id)
            if not auction:
                return False

            if auction.state != AuctionState.OPEN:
                return False
            
            if current_time > auction.end_time:
                return False
            
            if bidder_id == auction.seller_id:
                return False
                
            for bid in auction.bids:
                if bid.idempotency_key == idempotency_key and idempotency_key != "":
                    return True # already processed
            
            # Validation and highest bid logic omitted for brevity
            
            auction.bids.append(Bid(bidder_id=bidder_id, amount=amount, timestamp=current_time, idempotency_key=idempotency_key))
            
            # Anti-snipe check
            if current_time >= auction.end_time - auction.extension_window:
                if auction.extension_count < auction.extension_limit:
                    auction.end_time += auction.extension_duration
                    auction.extension_count += 1
            
            return True
```

## 10. Production Trade-offs (2 mins)
**Say:** "In a real production environment, this in-memory or single-node design would require certain trade-offs and adaptations."
Real-time push notifications require managing thousands of open WebSockets, which is resource-intensive. Using an in-memory priority queue is extremely fast but risks losing auction state on a crash; a persistent DB combined with a high-performance cache is mandatory for production.
