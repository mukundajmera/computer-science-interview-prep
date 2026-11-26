# OS & Concurrency Quiz

A quiz focused on os-concurrency.

Time: 35 minutes
Difficulty: Medium-Hard

---

## Section 1: Core Concepts

### Question 1
Why is a process context switch generally more expensive than a thread context switch?

A) A process context switch requires flushing the Translation Lookaside Buffer (TLB) and swapping page tables, while threads share the same memory space.
B) A process context switch requires a full system reboot if it fails, whereas thread switching is fault-tolerant.
C) A process context switch must re-authenticate the user permissions, while threads bypass security checks.
D) A process context switch involves physical disk I/O to swap out the process image, while a thread context switch only uses CPU cache.

### Question 2
In the context of the C10K problem, why do non-blocking I/O with an event loop (e.g., using `epoll` or `kqueue`) scale better than creating a dedicated thread per connection?

A) `epoll` uses CPU vector instructions to compress network payloads, significantly reducing memory bandwidth usage.
B) Dedicated threads consume significant memory for individual stacks and incur high context-switching overhead, whereas an event loop uses a single thread to monitor many connections asynchronously.
C) Event loops bypass the TCP/IP stack in the OS kernel directly, while thread-per-connection requires full system calls for every packet received.
D) Non-blocking I/O creates hardware-level interrupts for each incoming request, completely avoiding CPU usage until data is fully assembled.

### Question 3
What is the primary purpose of a Translation Lookaside Buffer (TLB) in virtual memory management?

A) It caches disk sectors to speed up the reading of executable files.
B) It caches the translation of virtual memory addresses to physical memory addresses to avoid expensive page table walks in main memory.
C) It buffers network packets before translating them into standard operating system signals.
D) It stores frequently used thread stack pointers for rapid thread context switching.

### Question 4
Which of the following scenarios is a Page Fault, and how is it typically handled?

A) A hardware failure in the RAM stick; handled by terminating the process to prevent corruption.
B) A process attempts to access a virtual memory page that is not currently mapped in physical RAM; handled by the OS interrupting the process, fetching the page from disk, updating the page table, and resuming execution.
C) Two threads simultaneously writing to the same memory address without a mutex; handled by the CPU throwing a concurrency exception.
D) A process exceeding its CPU quota; handled by the OS scheduler preempting the process and moving it to a wait queue.

### Question 5
What distinguishes a Mutex from a Binary Semaphore in concurrent programming?

A) A Mutex has the concept of 'ownership' and must be unlocked by the same thread that locked it, whereas a Semaphore can be signaled by any thread.
B) A Semaphore uses spin-waiting exclusively, while a Mutex always puts the thread to sleep immediately.
C) A Mutex can allow multiple threads to enter a critical section if configured properly, while a Semaphore strictly limits access to one.
D) A Semaphore can only be used between processes, while a Mutex can only be used between threads in the same process.

### Question 6
What is the primary danger of using multiple locks, and what is the standard strategy to prevent it?

A) Starvation; solved by assigning a random priority to each thread during execution.
B) Deadlock; solved by ensuring all threads acquire the necessary locks in the exact same predefined global order.
C) Livelock; solved by increasing the CPU frequency dynamically when contention is detected.
D) Priority Inversion; solved by using lock-free data structures exclusively.

### Question 7
What is Priority Inversion, and how does Priority Inheritance solve it?

A) High-priority threads run too often, starving low-priority ones; inheritance lowers the priority of all threads gradually.
B) A low-priority thread holds a lock needed by a high-priority thread, but is preempted by a medium-priority thread, effectively delaying the high-priority thread; inheritance temporarily boosts the low-priority thread to the high-priority level until the lock is released.
C) Threads inherit the priority of their parent process at creation, permanently locking them out of system resources; inheritance dynamically adjusts this based on CPU usage.
D) Hardware interrupts preempt OS threads unexpectedly; inheritance forces hardware to respect OS software priorities.

### Question 8
What is the primary difference between a Spinlock and a Mutex?

A) A Spinlock can be acquired across a network, while a Mutex is strictly local to the machine.
B) A Mutex continuously polls the lock status in a tight loop using CPU cycles, while a Spinlock uses OS system calls to put the thread to sleep.
C) A Spinlock continuously polls the lock status in a tight loop using CPU cycles, while a Mutex yields the CPU and puts the thread to sleep until the lock is available.
D) A Mutex is implemented entirely in hardware, while a Spinlock relies on software algorithms like Peterson's algorithm.

### Question 9
In Java or C++, what does the `volatile` keyword guarantee in the context of multithreading?

A) It guarantees that a block of code will execute atomically without interruption.
B) It guarantees visibility, meaning changes to the variable by one thread are immediately visible to others, and prevents the compiler from reordering operations around it or caching it in registers.
C) It automatically applies a distributed lock to the variable if the application spans multiple physical servers.
D) It ensures that the variable is stored in persistent disk storage rather than volatile RAM.

### Question 10
What is an Atomic Compare-and-Swap (CAS) operation?

A) A hardware-supported instruction that compares a memory location to an expected value, and if they match, updates it to a new value atomically, often used as the basis for lock-free data structures.
B) A software algorithm that compares two files on disk and swaps their contents if a hash mismatch is detected.
C) An OS-level feature that compares two running processes and swaps their CPU cores to optimize thermal distribution.
D) A network protocol that verifies the checksum of a packet before swapping it into the application buffer.

### Question 11
What is the ABA problem in lock-free concurrency, typically associated with CAS?

A) A thread acquires lock A, then lock B, while another acquires B then A, causing a deadlock.
B) A memory leak where threads abandon objects without freeing them, exhausting available memory.
C) A thread reads value A, another thread changes it to B, then back to A. The first thread then performs a CAS expecting A, succeeds because the value looks unchanged, but misses the intermediate state changes which might have invalidated pointers (like in a linked list).
D) A compiler optimization bug where variables named A and B are incorrectly assigned to the same CPU register.

### Question 12
How does `epoll` in Linux improve upon the older `select` and `poll` system calls for event-driven networking?

A) `epoll` automatically decrypts TLS traffic in the kernel, saving user-space CPU cycles.
B) `select` and `poll` require the kernel to iterate over all monitored file descriptors on every call to find ready ones (O(N)), while `epoll` uses an event-based approach where the kernel maintains the set and only returns the descriptors that are actually ready (O(1) active).
C) `epoll` creates a new kernel thread for every incoming connection, providing true hardware parallelism compared to `select`.
D) `epoll` bypasses the network interface card (NIC) driver, communicating directly with the hardware via DMA.

### Question 13
In the context of `epoll`, what is the difference between Level-Triggered (LT) and Edge-Triggered (ET) modes?

A) LT notifies you continuously as long as there is data to read; ET notifies you only once when the state changes from unreadable to readable, requiring you to read all available data until a blocking error occurs.
B) LT is used for disk I/O, while ET is exclusively used for network sockets.
C) LT triggers an OS panic if a buffer overflows, while ET silently drops excess packets.
D) LT is synchronous and blocking, while ET implies fully asynchronous disk writes.

### Question 14
What is Thread-Local Storage (TLS) and when is it most appropriate to use?

A) A highly secure encrypted memory region used to store TLS/SSL certificates.
B) Memory that is globally shared across all threads but requires no locks because it is immutable.
C) A mechanism where each thread has its own isolated instance of a variable, useful for maintaining per-thread state (like a database connection or random number generator) without requiring synchronization.
D) A specialized CPU cache layer that synchronizes automatically with the L3 cache.

### Question 15
What is the purpose of a Condition Variable?

A) It automatically restarts a thread if it crashes due to a null pointer exception.
B) It allows a thread to safely put itself to sleep and release an associated Mutex while waiting for a specific condition to become true, to be woken up later by another thread signaling the variable.
C) It acts as a boolean flag that is guaranteed to be atomic across CPU architectures without memory barriers.
D) It evaluates arbitrary boolean expressions at compile time to optimize lock removal.

### Question 16
Why is it necessary to check a Condition Variable in a `while` loop rather than a simple `if` statement?

A) `if` statements are not thread-safe and can be optimized away by the compiler.
B) To handle 'Spurious Wakeups', where the OS wakes a waiting thread even if the condition hasn't been signaled, or if another thread grabbed the resource between the signal and the wakeup.
C) Because condition variables only support loop structures in POSIX standards.
D) To ensure that the CPU cache is flushed repeatedly until the condition is met.

### Question 17
In a Read-Write Lock (Readers-Writer Lock), what is the concurrency rule?

A) Readers and writers can access the resource simultaneously to maximize throughput, resolving conflicts via CAS.
B) Only one thread can read or write at a time; it is synonymous with a Mutex.
C) Multiple threads can acquire the read lock simultaneously if no writer holds the lock, but the write lock is exclusive (no other readers or writers).
D) Writers have permanent priority; a read lock will fail instantly if any writer is queued.

### Question 18
What is False Sharing in multi-core programming?

A) Two threads erroneously using the same pointer to write to independent databases.
B) When two independent variables accessed by different threads reside on the same CPU cache line. When one thread writes to its variable, it invalidates the entire cache line for the other CPU, causing severe performance degradation despite no logical data sharing.
C) A security vulnerability where one process can read the virtual memory of another through branch prediction analysis.
D) When an event loop incorrectly routes a network packet to two different worker threads.

### Question 19
What mechanism is typically used to prevent False Sharing?

A) Using a distributed locking mechanism like ZooKeeper.
B) Compressing the variables into a single integer using bitwise operations.
C) Aligning data structures and inserting padding (e.g., dummy variables) to ensure independent variables land on separate cache lines.
D) Forcing all threads to run sequentially on a single core.

### Question 20
What is a Context Switch?

A) The process of switching a program's GUI from dark mode to light mode.
B) The hardware mechanism of shifting CPU execution from real mode to protected mode.
C) The OS procedure of saving the state (registers, program counter) of a currently running process or thread and loading the state of the next one to run.
D) The act of redirecting standard output from the console to a file.

### Question 21
Why is using thread pools generally preferred over creating a new thread for every task in high-throughput server applications?

A) Thread pools automatically convert multithreaded code into single-threaded asynchronous code.
B) Thread pools bypass OS scheduling entirely, relying on the JVM or Python interpreter for faster execution.
C) Creating and destroying OS threads is expensive in terms of CPU and memory. A pool reuses a fixed set of existing threads to execute tasks, avoiding initialization overhead and preventing resource exhaustion.
D) Thread pools eliminate the need for mutexes and synchronization between tasks.

### Question 22
What is the primary characteristic of an Asynchronous I/O model (like `io_uring` or Windows IOCP) compared to Non-blocking I/O (like `epoll`)?

A) Asynchronous I/O uses TCP, while Non-blocking I/O strictly uses UDP.
B) In Non-blocking I/O, the OS tells the app *when* a socket is ready, and the app must then synchronously perform the read/write. In Asynchronous I/O, the OS performs the read/write in the background and notifies the app when the buffer is fully transferred.
C) Asynchronous I/O requires a dedicated GPU for memory transfers.
D) Non-blocking I/O is faster because it bypasses the kernel completely, while Asynchronous I/O requires kernel intervention.

### Question 23
How does Paging solve external memory fragmentation?

A) By periodically halting all processes and compacting physical RAM to group free space together.
B) By requiring applications to request exact memory sizes in multiples of 1 Megabyte.
C) By mapping contiguous virtual memory addresses to arbitrary, non-contiguous fixed-size physical frames, meaning the OS doesn't need to find large contiguous chunks of physical RAM.
D) By using a garbage collector to delete unused objects in the kernel.

### Question 24
What is a Memory Barrier (or Memory Fence)?

A) A hardware instruction that enforces ordering constraints on memory operations, ensuring that reads/writes issued before the barrier are completed before those issued after it, preventing reordering by the CPU or compiler.
B) An OS security feature that prevents user-mode processes from accessing kernel-mode memory addresses.
C) A physical resistor on the motherboard that limits the bandwidth between the CPU and RAM.
D) A software firewall rule that drops packets aiming to exploit buffer overflow vulnerabilities.

### Question 25
What characterizes a Deadlock, and what are the four Coffman conditions necessary for it to occur?

A) A state where processes loop infinitely without making progress. Conditions: High CPU usage, network timeout, memory leak, user interrupt.
B) A state where a group of processes are blocked permanently because each is waiting for a resource held by another. Conditions: Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait.
C) A state where a thread accesses freed memory. Conditions: Pointers, dynamic allocation, missing locks, manual garbage collection.
D) A hardware failure where two CPU cores try to access the bus simultaneously. Conditions: Overclocking, voltage drop, cache miss, thermal throttling.

### Question 26
What is the "Thundering Herd" problem in concurrent programming, and how is it typically mitigated in socket programming?

A) When a large number of threads simultaneously wake up to process a single event, but only one can successfully handle it, causing wasted CPU cycles and lock contention. It is often mitigated by using `epoll` with the `EPOLLEXCLUSIVE` flag or by having a single thread accept connections and distribute them.
B) When a single thread spawns too many child processes, exhausting the OS process table. It is mitigated by strictly limiting the maximum number of file descriptors using `ulimit`.
C) When multiple servers on a network broadcast UDP packets simultaneously, causing a network storm. It is mitigated by switching to TCP which provides congestion control.
D) When garbage collection pauses all application threads simultaneously, causing a massive latency spike. It is mitigated by using a concurrent garbage collector like G1 or ZGC.

