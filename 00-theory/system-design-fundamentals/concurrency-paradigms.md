# Concurrency Paradigms

Concurrency paradigms dictate how computation tasks coordinate and communicate. Choosing the right paradigm influences a system's fault tolerance, scaling potential, and developer reasoning model. 

---

## 1. Shared Memory with Mutex / Atomics / STM

In the Shared Memory paradigm, concurrent threads or processes coordinate by reading and writing to shared memory locations. 

### Key Concepts
*   **Mutexes & Locks:** Primitive synchronization mechanisms (e.g., `synchronized` in Java) that enforce mutual exclusion. Only one thread can enter a critical section at a time, preventing race conditions but potentially causing deadlocks or thread contention.
*   **Atomics:** CPU-level instructions (like Compare-And-Swap) that allow lock-free updates to shared variables. Good for high-contention, low-complexity state (e.g., counters).
*   **Software Transactional Memory (STM):** An abstraction where memory reads and writes are batched in transactions. Similar to database transactions, if a conflict occurs, the transaction is automatically rolled back and retried (optimistic concurrency control).

### Trade-offs
*   **Pros:** Intuitive for developers familiar with sequential execution; highly performant when contention is low.
*   **Cons:** Hard to reason about at scale (race conditions, deadlocks). Scaling beyond a single machine requires distributed locks or shifting to a different paradigm.

---

## 2. Actor Model (Erlang/OTP, Akka)

The Actor Model treats "Actors" as the fundamental, independent unit of computation.

### Key Concepts
*   **Share-Nothing & Mailboxes:** Actors encapsulate state and behavior. They do not share memory. Instead, they communicate exclusively via asynchronous message passing. Every actor has a mailbox to queue incoming messages, processing them sequentially.
*   **Supervision Trees:** Error handling is hierarchical. If an actor crashes, its supervisor decides whether to restart it, resume it, or escalate the failure (the "let it crash" philosophy).
*   **Location Transparency:** Sending a message to a local actor is semantically identical to sending it to an actor on a remote server. This makes the system inherently distributable.

### Trade-offs
*   **Pros:** Excellent fault isolation, natural horizontal scaling, avoids deadlocks inherently by removing shared locks.
*   **Cons:** Mailboxes can overflow if producers outpace consumers (weak backpressure mechanisms in pure actor models); high memory overhead per actor.

---

## 3. Communicating Sequential Processes (CSP - Go channels)

CSP models concurrency via independent processes that exchange data over explicit, first-class channels. 

### Key Concepts
*   **Channels:** Pipes through which data is sent and received. Processes don't know who is on the other side of the channel, decoupling producers from consumers.
*   **Rendezvous (Synchronous Communication):** Unbuffered channels require both sender and receiver to be ready simultaneously, creating an implicit synchronization point.
*   **Channel Multiplexing with `select`:** A powerful construct (like `select` in Go) allows a process to wait on multiple channels simultaneously, proceeding as soon as one is ready to send or receive.

### Trade-offs
*   **Pros:** Clear reasoning about data flow; built-in backpressure (sending blocks if a channel is full or unread); channels are first-class citizens.
*   **Cons:** Can still lead to deadlocks (e.g., circular channel dependencies); not as prescriptive about fault tolerance compared to Actor supervision trees.

---

## 4. Reactive Streams (Project Reactor, RxJava)

Reactive Streams standardizes asynchronous, non-blocking stream processing.

### Key Concepts
*   **Asynchronous Non-blocking Push-Pull:** Data flows from publishers to subscribers asynchronously without blocking threads.
*   **Dynamic Backpressure (`Subscriber.request(n)`):** A defining feature. The subscriber tells the publisher exactly how many items it is ready to process. The publisher pushes *up to* `n` items, preventing the consumer from being overwhelmed.
*   **Declarative Pipelines:** Operations (map, filter, flatMap) are chained, abstracting the underlying thread scheduling.

### Trade-offs
*   **Pros:** Highly efficient use of hardware (few threads can handle many concurrent streams); robust and explicit backpressure guarantees.
*   **Cons:** Steep learning curve; debugging can be difficult as stack traces cross thread boundaries and execution happens deferred from the pipeline declaration.

---

## Comprehensive Comparison Matrix

| Feature | Shared Memory | Actor Model | CSP (Channels) | Reactive Streams |
| :--- | :--- | :--- | :--- | :--- |
| **Communication** | Shared state | Asynchronous messages | Synchronous/Asynchronous channels | Data streams / Events |
| **Memory Overhead** | Low (raw variables) | Moderate (mailboxes & actor state) | Low to Moderate (goroutines & channels) | Moderate (stream subscriptions) |
| **Thread Binding** | Usually 1:1 with OS threads | M:N (Many actors to few OS threads) | M:N (Many processes/goroutines to few OS threads) | Agnostic (Event loop or thread pools) |
| **Fault Isolation** | Poor (One thread crash can corrupt shared state) | Excellent (Supervision trees) | Moderate (Requires explicit error handling/channels) | Moderate (Error channels in pipelines) |
| **Backpressure** | Manual (Semaphores, bounded queues) | Weak (Implicitly relies on unbounded mailboxes) | Strong (Built-in via bounded/unbuffered channels) | Very Strong (Dynamic `request(n)`) |
| **Domain Fit** | High performance local computation, System level programming | High availability, distributed stateful systems (e.g., IoT, Gaming) | Concurrency orchestration, data pipelines, workers | High-throughput UI, microservice orchestration, real-time analytics |

---

## Cross-References
* [Synchronous vs Asynchronous](./sync-vs-async.md)
* [Concurrency in LLD](./concurrency-in-lld.md)
