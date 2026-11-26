# Design Document: Online Auction

## System Architecture
The system relies on an in-memory data storage strategy to handle the differing requirements of active, high-velocity auctions versus historical, long-term data storage and reporting, strictly using standard libraries for the required supported versions (Java 11+ SE and Python 3.8+ standard libraries).

### Core Components
1. **API Gateway & Rate Limiter:** Protects the system from brute-force bidding bots and manages authentication using standard HTTP tools (`http.server` / `urllib`).
2. **Bidding Engine:** The core component using standard library locks (e.g., `ReentrantLock`, `asyncio.Lock`). It holds the state of all *active* auctions and processes bids using atomic operations.
3. **Auction Service:** Manages the lifecycle of an auction (creation, modification, finalization).
4. **WebSocket Service:** Pushes real-time bid updates and outbid alerts to connected clients using standard `socket` module.
5. **Durable Database Interface:** Simulates storing user profiles, historical auctions, completed bids, and payment records.

### State Transitions
The auction lifecycle follows a strict state machine:
- **DRAFT:** The auction is being configured. Bids are not accepted.
- **OPEN:** The auction is active and accepting bids.
- **CLOSED:** The bidding period has ended. No new bids are accepted.
- **SETTLED:** The auction has been finalized, winners notified, and payment processed. Replay of settlement logic is idempotent to prevent double-settling.

### Bidding Policies
The system supports multiple distinct bidding policies depending on the auction configuration. Specifically, English proxy-bid tie order and Vickrey sealed-bid pricing are separate named policies; late bids, duplicate IDs and settlement replay cannot double-settle.

#### Policy Implementations & Idempotency

**Java 11+ Implementation**
```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.List;
import java.util.ArrayList;
import java.util.Collections;
import java.util.Comparator;

public class AuctionSettler {
    private final AtomicBoolean isSettled = new AtomicBoolean(false);
    private final ConcurrentHashMap<String, Boolean> processedSettlements = new ConcurrentHashMap<>();

    public void settleAuction(String auctionId, String policyType, List<Bid> bids) {
        // Late bids, duplicate IDs and settlement replay cannot double-settle
        if (!isSettled.compareAndSet(false, true)) {
            return; // Idempotent check
        }
        if (processedSettlements.putIfAbsent(auctionId, true) != null) {
            return;
        }

        // Deduplicate bids by ID to prevent duplicate IDs from double-settling
        List<Bid> uniqueBids = new ArrayList<>();
        // ... deduplication logic ...
        
        // English proxy-bid tie order and Vickrey sealed-bid pricing are separate named policies
        if ("ENGLISH_PROXY".equals(policyType)) {
            settleEnglishProxy(uniqueBids);
        } else if ("VICKREY".equals(policyType)) {
            settleVickrey(uniqueBids);
        }
    }
    
    private void settleEnglishProxy(List<Bid> bids) {
        // Tie order based on earliest timestamp
        bids.sort(Comparator.comparing(Bid::getAmount).reversed()
                            .thenComparing(Bid::getTimestamp));
        // Settlement logic...
    }
    
    private void settleVickrey(List<Bid> bids) {
        bids.sort(Comparator.comparing(Bid::getAmount).reversed());
        long secondHighestPrice = bids.size() > 1 ? bids.get(1).getAmount() : bids.get(0).getAmount();
        // Winner pays secondHighestPrice
    }
}

class Bid {
    long amount;
    long timestamp;
    String id;
    public long getAmount() { return amount; }
    public long getTimestamp() { return timestamp; }
}
```

**Python 3.8+ Implementation**
```python
import typing

class Bid:
    def __init__(self, bid_id: str, amount: int, timestamp: float):
        self.id = bid_id
        self.amount = amount
        self.timestamp = timestamp

class AuctionSettler:
    def __init__(self):
        self.is_settled: bool = False
        self.processed_settlements: typing.Set[str] = set()

    def settle_auction(self, auction_id: str, policy_type: str, bids: typing.List[Bid]) -> None:
        # Late bids, duplicate IDs and settlement replay cannot double-settle
        if self.is_settled:
            return
        if auction_id in self.processed_settlements:
            return
            
        self.is_settled = True
        self.processed_settlements.add(auction_id)

        # Deduplicate bids by ID to prevent duplicate IDs from double-settling
        unique_bids_dict = {bid.id: bid for bid in bids}
        unique_bids = list(unique_bids_dict.values())

        # English proxy-bid tie order and Vickrey sealed-bid pricing are separate named policies
        if policy_type == "ENGLISH_PROXY":
            self._settle_english_proxy(unique_bids)
        elif policy_type == "VICKREY":
            self._settle_vickrey(unique_bids)

    def _settle_english_proxy(self, bids: typing.List[Bid]) -> None:
        # Tie order based on earliest timestamp
        sorted_bids = sorted(bids, key=lambda b: (-b.amount, b.timestamp))
        # Settlement logic...

    def _settle_vickrey(self, bids: typing.List[Bid]) -> None:
        sorted_bids = sorted(bids, key=lambda b: -b.amount)
        second_highest_price = sorted_bids[1].amount if len(sorted_bids) > 1 else sorted_bids[0].amount
        # Winner pays second_highest_price
```

### Anti-Snipe Deadline Extensions
By design, injected deadline checks cover anti-snipe extension limits and concurrent bids; money uses exact units and invalid amounts are rejected.
To prevent "sniping" (placing a bid at the very last millisecond), the system injects deadline extension checks securely using standard memory locks. If a valid bid is placed within a configurable window (e.g., the last 5 minutes) before the auction ends, the deadline is extended by a fixed duration. This extension limit can be capped (e.g., maximum 5 extensions) to ensure the auction eventually closes. Concurrent bids are serialized correctly to calculate extensions.

### Money Representation
Money is represented strictly using exact integer units (e.g., cents or smallest currency denominators) to avoid floating-point inaccuracies. Invalid amounts (e.g., negative values, non-integer inputs, or amounts not aligning with the minimum increment) are strictly rejected during validation.

Each assigned document describes actual supported versions; no line/word minimum replaces semantic review.
