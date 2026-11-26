# OS & Concurrency Answers

## Question 1

1. **A** - A process context switch requires flushing the Translation Lookaside Buffer (TLB) and swapping page tables, while threads share the same memory space.

**Explanation:** A process context switch requires swapping virtual memory spaces, including page tables and flushing the TLB (Translation Lookaside Buffer), which induces a high rate of cache misses. Threads share the same virtual memory space, so their switch only saves/restores CPU registers and stack pointers without TLB flushing.

---

## Question 2

2. **B** - Dedicated threads consume significant memory for individual stacks and incur high context-switching overhead, whereas an event loop uses a single thread to monitor many connections asynchronously.

**Explanation:** A thread-per-connection model requires a dedicated memory stack per connection and incurs severe context-switching overhead for the OS scheduler at high scale. Event loops like `epoll` allow a single thread to monitor thousands of descriptors efficiently, waking up only when data is ready.

---

## Question 3

3. **B** - It caches the translation of virtual memory addresses to physical memory addresses to avoid expensive page table walks in main memory.

**Explanation:** The TLB is a specialized hardware cache within the Memory Management Unit (MMU) that stores recent translations of virtual memory to physical memory addresses, drastically speeding up memory access by avoiding a full page table walk on every lookup.

---

## Question 4

4. **B** - A process attempts to access a virtual memory page that is not currently mapped in physical RAM; handled by the OS interrupting the process, fetching the page from disk, updating the page table, and resuming execution.

**Explanation:** A page fault occurs when a valid virtual address is accessed, but its physical page is currently absent from RAM (often swapped out). The OS traps the fault, loads the page from persistent storage into RAM, updates the mapping, and restarts the instruction.

---

## Question 5

5. **A** - A Mutex has the concept of 'ownership' and must be unlocked by the same thread that locked it, whereas a Semaphore can be signaled by any thread.

**Explanation:** The defining characteristic of a Mutex is ownership: only the thread that acquired the lock can release it, making it suited for mutual exclusion. A Semaphore is a signaling mechanism (counter) and can be incremented (released) by a completely different thread, making it useful for coordination (like producer-consumer).

---

## Question 6

6. **B** - Deadlock; solved by ensuring all threads acquire the necessary locks in the exact same predefined global order.

**Explanation:** Acquiring multiple locks can lead to deadlocks if two threads acquire locks in opposite orders, waiting on each other indefinitely. The standard mitigation is strict lock ordering: always acquiring locks in a consistent, globally defined sequence (e.g., sorted by memory address).

---

## Question 7

7. **B** - A low-priority thread holds a lock needed by a high-priority thread, but is preempted by a medium-priority thread, effectively delaying the high-priority thread; inheritance temporarily boosts the low-priority thread to the high-priority level until the lock is released.

**Explanation:** Priority inversion happens when a high-priority task is blocked waiting on a low-priority task that holds a lock, and a medium task preempts the low one, effectively making the medium task run before the high one. Priority inheritance solves this by temporarily raising the lock holder's priority to match the waiter's.

---

## Question 8

8. **C** - A Spinlock continuously polls the lock status in a tight loop using CPU cycles, while a Mutex yields the CPU and puts the thread to sleep until the lock is available.

**Explanation:** A Spinlock burns CPU cycles actively checking if the lock is free, which avoids context-switching overhead but wastes CPU time if the wait is long. A Mutex puts the thread to sleep (yielding the CPU to other tasks) and wakes it up when the lock is free, incurring context-switch overhead but saving CPU cycles during long waits.

---

## Question 9

9. **B** - It guarantees visibility, meaning changes to the variable by one thread are immediately visible to others, and prevents the compiler from reordering operations around it or caching it in registers.

**Explanation:** `volatile` establishes a memory barrier. It prevents compilers from caching the variable in registers or optimizing away reads/writes, and it prevents CPU instruction reordering. This ensures that when thread A writes to the variable, thread B immediately sees the updated value in main memory. It does not provide atomicity for compound operations like `i++`.

---

## Question 10

10. **A** - A hardware-supported instruction that compares a memory location to an expected value, and if they match, updates it to a new value atomically, often used as the basis for lock-free data structures.

**Explanation:** Compare-and-Swap (CAS) is a primitive hardware instruction that reads a value, compares it to an expected old value, and writes a new value if and only if the current value matches the expectation. It is executing atomically at the hardware level, forming the foundation of non-blocking/lock-free algorithms.

---

## Question 11

11. **C** - A thread reads value A, another thread changes it to B, then back to A. The first thread then performs a CAS expecting A, succeeds because the value looks unchanged, but misses the intermediate state changes which might have invalidated pointers (like in a linked list).

**Explanation:** The ABA problem occurs when CAS succeeds because a memory location's value matches the expected 'A', but it fails to detect that the value was changed to 'B' and back to 'A' in the interim. This can corrupt lock-free data structures, like stacks, where the pointer 'A' now represents a completely different node lifecycle. It is often solved with hazard pointers or version tags.

---

## Question 12

12. **B** - `select` and `poll` require the kernel to iterate over all monitored file descriptors on every call to find ready ones (O(N)), while `epoll` uses an event-based approach where the kernel maintains the set and only returns the descriptors that are actually ready (O(1) active).

**Explanation:** `select` and `poll` force the application to pass the entire list of descriptors to the kernel every time, and the kernel linearly scans them. `epoll` registers the descriptors once and uses hardware interrupts/callbacks to populate a ready list. The application only receives the descriptors that actually have events, making it scale efficiently to millions of connections.

---

## Question 13

13. **A** - LT notifies you continuously as long as there is data to read; ET notifies you only once when the state changes from unreadable to readable, requiring you to read all available data until a blocking error occurs.

**Explanation:** Level-Triggered (the default) acts like `poll`: it keeps alerting you as long as the file descriptor is ready (e.g., buffer has data). Edge-Triggered alerts you exactly once when a new event arrives. If you don't read the buffer completely until `EAGAIN` in ET mode, you might never get notified again for the remaining data.

---

## Question 14

14. **C** - A mechanism where each thread has its own isolated instance of a variable, useful for maintaining per-thread state (like a database connection or random number generator) without requiring synchronization.

**Explanation:** Thread-Local Storage assigns a unique memory location to a specific variable for every thread that accesses it. This avoids race conditions and synchronization overhead entirely because threads do not share the data, making it ideal for thread-specific context like transaction IDs or un-synchronized random seeds.

---

## Question 15

15. **B** - It allows a thread to safely put itself to sleep and release an associated Mutex while waiting for a specific condition to become true, to be woken up later by another thread signaling the variable.

**Explanation:** Condition variables are used in conjunction with a mutex to wait for state changes. A thread acquires the mutex, checks a condition, and if false, waits on the condition variable (which atomically releases the mutex and sleeps). Another thread changes the state and signals the condition variable, waking up the sleeper, which re-acquires the mutex before proceeding.

---

## Question 16

16. **B** - To handle 'Spurious Wakeups', where the OS wakes a waiting thread even if the condition hasn't been signaled, or if another thread grabbed the resource between the signal and the wakeup.

**Explanation:** Operating systems can occasionally wake up threads waiting on condition variables without a matching signal (spurious wakeups). Additionally, even if signaled correctly, another thread might have raced in and altered the condition before the woken thread re-acquired the mutex. A `while(condition_is_false)` loop ensures the thread goes back to sleep if the state isn't actually ready.

---

## Question 17

17. **C** - Multiple threads can acquire the read lock simultaneously if no writer holds the lock, but the write lock is exclusive (no other readers or writers).

**Explanation:** A Read-Write lock optimizes for read-heavy workloads. It allows concurrent access for multiple readers (shared lock), but enforces strict mutual exclusion for writers (exclusive lock) against both other writers and readers. This prevents data tearing while maximizing read throughput.

---

## Question 18

18. **B** - When two independent variables accessed by different threads reside on the same CPU cache line. When one thread writes to its variable, it invalidates the entire cache line for the other CPU, causing severe performance degradation despite no logical data sharing.

**Explanation:** CPUs fetch memory in chunks called cache lines (typically 64 bytes). If thread A on core 1 modifies variable X, and thread B on core 2 modifies variable Y, and X and Y are adjacent in memory (on the same cache line), the cores will constantly invalidate each other's cache lines in hardware, causing a 'ping-pong' effect and ruining performance, even though no actual logical data sharing or lock contention exists.

---

## Question 19

19. **C** - Aligning data structures and inserting padding (e.g., dummy variables) to ensure independent variables land on separate cache lines.

**Explanation:** The standard solution to false sharing is memory padding or alignment. By inserting empty bytes between independent variables frequently accessed by different threads, you force them onto separate CPU cache lines, eliminating the hardware-level cache invalidation conflict.

---

## Question 20

20. **C** - The OS procedure of saving the state (registers, program counter) of a currently running process or thread and loading the state of the next one to run.

**Explanation:** A context switch is the core mechanism of multitasking. The OS scheduler preempts a running thread/process, saves its exact CPU state (registers, instruction pointer, stack pointer) into a control block, and loads the saved state of a different thread/process so it can resume execution.

---

## Question 21

21. **C** - Creating and destroying OS threads is expensive in terms of CPU and memory. A pool reuses a fixed set of existing threads to execute tasks, avoiding initialization overhead and preventing resource exhaustion.

**Explanation:** Thread creation involves allocating a stack and invoking OS system calls, which is slow. A thread pool pre-allocates threads. When a task arrives, an idle thread executes it, and then returns to the pool. This avoids the latency of thread creation and bounds the maximum number of threads, preventing out-of-memory errors and excessive context switching under heavy load.

---

## Question 22

22. **B** - In Non-blocking I/O, the OS tells the app *when* a socket is ready, and the app must then synchronously perform the read/write. In Asynchronous I/O, the OS performs the read/write in the background and notifies the app when the buffer is fully transferred.

**Explanation:** `epoll` is a readiness model: it tells you 'descriptor X is ready to read', but calling `read()` still blocks briefly to copy data from kernel to user space. True asynchronous I/O (Proactor pattern, e.g., `io_uring`) is a completion model: you submit a buffer to the kernel, the kernel does the network wait and the data copy in the background, and alerts you when the data is fully in your user-space buffer.

---

## Question 23

23. **C** - By mapping contiguous virtual memory addresses to arbitrary, non-contiguous fixed-size physical frames, meaning the OS doesn't need to find large contiguous chunks of physical RAM.

**Explanation:** External fragmentation occurs when free memory is scattered in small chunks, making it impossible to allocate a large contiguous block. Paging breaks physical memory into fixed-size frames and virtual memory into pages. A large contiguous virtual allocation can be backed by scattered physical frames, completely eliminating external fragmentation.

---

## Question 24

24. **A** - A hardware instruction that enforces ordering constraints on memory operations, ensuring that reads/writes issued before the barrier are completed before those issued after it, preventing reordering by the CPU or compiler.

**Explanation:** Modern CPUs and compilers heavily reorder instructions to optimize pipelines. A memory barrier (fence) is a low-level instruction that forces serialization: it guarantees that all memory operations initiated before the barrier are globally visible before any memory operations initiated after the barrier are executed. This is critical for lock-free programming.

---

## Question 25

25. **B** - A state where a group of processes are blocked permanently because each is waiting for a resource held by another. Conditions: Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait.

**Explanation:** A deadlock is a permanent stall. It requires four simultaneous conditions (Coffman conditions): 1) Mutual Exclusion (resources cannot be shared), 2) Hold and Wait (holding a resource while requesting another), 3) No Preemption (resources cannot be forcefully taken), and 4) Circular Wait (a chain of processes, each waiting for the next).

---

## Question 26

26. **A** - When a large number of threads simultaneously wake up to process a single event, but only one can successfully handle it, causing wasted CPU cycles and lock contention. It is often mitigated by using `epoll` with the `EPOLLEXCLUSIVE` flag or by having a single thread accept connections and distribute them.

**Explanation:** The Thundering Herd problem occurs when many threads (or processes) are blocked waiting for an event (like a new TCP connection on a shared listening socket). When the event occurs, the OS wakes up all waiting threads. Since only one can accept the connection, the others fail and go back to sleep, wasting significant CPU resources and causing high context-switching overhead. Modern OS features like `EPOLLEXCLUSIVE` in Linux allow waking up only one thread per event, solving this problem efficiently.

---
