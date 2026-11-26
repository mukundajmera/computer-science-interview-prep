# Stock Exchange Matching Engine - Strong Answer

## Example Communication

> **Say:** "Given the ultra-low latency requirement of under 100 microseconds, we cannot use a traditional database or distributed locking in the critical path. Every network hop or disk I/O will violate our SLA. Therefore, the core matching engine must be a single-threaded process running entirely in-memory."

> **Say:** "To achieve High Availability without distributed locks, we will use an Event Sourcing pattern with a Sequencer. The Sequencer assigns a strict monotonic ID to every inbound order. Since our matching logic is deterministic, we can run a Hot Standby node that processes this exact same sequence. If the Primary fails, the Standby is already at the exact same state and can take over instantly."

> **Say:** "For the Limit Order Book data structure, we need to optimize for three operations: adding an order, matching an order at the top of the book, and cancelling an order. I'll use a `TreeMap` to maintain sorted price levels, which gives $O(\log N)$ insertion. Each price level will hold a `DoublyLinkedList` of orders for $O(1)$ FIFO matching. Finally, a `HashMap` mapping Order IDs to the linked list nodes allows $O(1)$ cancellations, which is critical since market makers cancel the vast majority of their orders."

> **Say:** "To avoid Java Garbage Collection pauses, which can cause latency spikes of several milliseconds, we will pre-allocate all order objects in a Ring Buffer or Object Pool at startup. We'll use fixed-point integers for all monetary values to prevent floating-point precision loss."
