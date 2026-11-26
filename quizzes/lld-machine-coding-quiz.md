# 🧠 LLD & Machine Coding Excellence Quiz

> **20 questions covering LFU cache mechanics, Ring Buffer false sharing, State vs Enum FSM, Thread-safe singleton edge cases, ReentrantLock vs Synchronized, Deadlock avoidance, Inode/VFS structures, and Command pattern undo/redo.**

---

## 📊 Scoring Guide

| Score | Range | Assessment | Recommendation |
|-------|-------|------------|----------------|
| 18-20 | 90-100% | **Excellent** | Ready for advanced LLD/machine coding rounds |
| 15-17 | 75-89% | **Good** | Review weak concurrency or design pattern areas |
| 12-14 | 60-74% | **Fair** | More practice needed with advanced Java structures |
| 0-11 | 0-59% | **Needs Work** | Study foundational LLD principles first |

---

## 📝 Questions

### Question 1
In an O(1) LFU cache implementation using a HashMap of doubly linked lists, what is the primary role of the `minFrequency` variable?

A) To limit the maximum number of times an item can be accessed before eviction.
B) To quickly locate the bucket containing the least frequently used elements when the cache reaches capacity and an eviction is necessary.
C) To sort the entire cache contents whenever a `get()` operation occurs.
D) To track the historical average frequency of all evicted elements.

### Question 2
When implementing a high-throughput Ring Buffer (e.g., LMAX Disruptor style), what is the primary purpose of adding "padding" variables (e.g., `long p1, p2, p3...`) around the sequence numbers?

A) To increase the total capacity of the Ring Buffer.
B) To prevent garbage collection overhead by pre-allocating memory blocks.
C) To avoid false sharing by ensuring that concurrently modified sequence variables reside on different CPU cache lines.
D) To provide backward compatibility with 32-bit JVM architectures.

### Question 3
You are designing a complex multi-stage order processing pipeline. You need to enforce valid state transitions (e.g., CREATED -> PAID -> SHIPPED) and attach specific behavior to each state. What is the key advantage of using the State pattern over a simple Enum-based FSM with a `switch` statement?

A) The State pattern guarantees O(1) memory usage regardless of the number of states.
B) The State pattern centralizes all state transition logic into a single method, reducing cognitive load.
C) The State pattern encapsulates state-specific behavior into separate classes, adhering to the Open/Closed Principle and avoiding massive `switch` statements as complexity grows.
D) The State pattern implicitly handles distributed consensus across microservices.

### Question 4
Which of the following is a classic vulnerability of the double-checked locking singleton pattern in Java if the `volatile` keyword is NOT used on the instance variable?

A) The JVM might throw an `IllegalMonitorStateException`.
B) Another thread might see a partially constructed object due to instruction reordering.
C) The singleton will be garbage collected prematurely.
D) It creates a deadlock if two threads access `getInstance()` simultaneously.

### Question 5
In a highly concurrent machine coding round, you must implement a thread-safe custom collection. Why might you choose `ReentrantLock` over the intrinsic `synchronized` keyword?

A) `ReentrantLock` inherently provides faster execution times due to bypassing the JVM monitor.
B) `ReentrantLock` allows for more flexible locking semantics, such as `tryLock()` with timeouts, interruptible lock acquisition, and fairness policies.
C) `ReentrantLock` prevents all forms of deadlocks automatically.
D) `synchronized` blocks cannot be used within `while` loops.

### Question 6
You are implementing a financial transfer system in an LLD interview. To prevent deadlocks when transferring funds between two `Account` objects, which strategy is the most robust and standard?

A) Use `Thread.sleep()` with a random backoff if a lock is unavailable.
B) Lock the `Account` objects in a globally consistent order (e.g., sorting by account ID) before performing the transfer.
C) Synchronize the entire `transfer` method on a global lock object to ensure absolute serializability.
D) Use a decentralized peer-to-peer voting mechanism to acquire locks.

### Question 7
When designing an in-memory file system (VFS), what is the primary purpose of separating the "Inode" structure from the "Directory Entry" (Dentry) structure?

A) To compress the file contents transparently.
B) To enforce network-level security permissions.
C) To decouple file metadata (size, blocks, permissions) from file hierarchy and names, enabling features like hard links.
D) To ensure all files are stored contiguously in memory.

### Question 8
You are implementing an Undo/Redo feature for a text editor using the Command pattern. What is the most common data structure pairing to manage the command history?

A) A single HashMap storing commands by timestamp.
B) Two Stacks: an Undo stack to record executed commands and a Redo stack to hold undone commands.
C) A PriorityQueue sorted by the complexity of the command.
D) A circular Ring Buffer of size 1.

### Question 9
In an O(1) LFU Cache, when a new item is inserted and the cache is at capacity, which item is evicted if multiple items share the minimum frequency?

A) The item with the highest total byte size.
B) The item that was inserted most recently.
C) The Least Recently Used (LRU) item among those with the minimum frequency.
D) A randomly selected item from the cache.

### Question 10
How does a Ring Buffer achieve O(1) enqueues and dequeues without allocating new nodes?

A) By dynamically resizing the underlying array whenever it fills up.
B) By using a background thread to pre-allocate nodes into a global pool.
C) By pre-allocating a fixed-size array and using wrapping read/write sequence indices (modulo arithmetic).
D) By relying on the OS virtual memory page table for implicit wrapping.

### Question 11
When using an Enum-based Finite State Machine in Java, what is a valid technique to prevent illegal state transitions?

A) Implementing a global `Interceptor` pattern.
B) Throwing an `IllegalStateException` inside a state transition method if the current state is invalid for the requested action.
C) Setting the instance variable to `null` briefly during the transition.
D) Inheriting from `java.util.concurrent.atomic.AtomicState`.

### Question 12
In the context of the Singleton pattern, what does the Enum Singleton approach in Java uniquely protect against out-of-the-box?

A) Memory leaks caused by large inner structures.
B) Reflection attacks and serialization-induced multiple instantiations.
C) Deadlocks during initialization.
D) The ABA problem in concurrent collections.

### Question 13
What is a key disadvantage of `ReentrantLock.tryLock(timeout, unit)`?

A) It permanently blocks the thread if the timeout is reached.
B) It requires a manual `unlock()` in a `finally` block, increasing the risk of lock leaks if not coded carefully.
C) It cannot be used with multiple condition variables.
D) It is deprecated in Java 11.

### Question 14
In a multithreaded environment, the condition `Lock-Ordering` is used to prevent which of the four Coffman conditions for deadlock?

A) Mutual Exclusion
B) Hold and Wait
C) No Preemption
D) Circular Wait

### Question 15
In an in-memory file system design, what pattern is typically used to represent the hierarchical structure of files and directories uniformly?

A) The Observer pattern.
B) The Composite pattern.
C) The Flyweight pattern.
D) The Strategy pattern.

### Question 16
In the Command pattern used for undo/redo operations, what method must a concrete `Command` class implement in addition to `execute()`?

A) `undo()`
B) `commit()`
C) `rollbackTransactions()`
D) `log()`

### Question 17
Why is `HashMap` lookup technically O(1) average case, but potentially O(N) worst case?

A) Because the JVM must dynamically recompile the bytecode during the first lookup.
B) Hash collisions can cause multiple items to map to the same bucket, degrading performance to O(N) if stored in a linked list.
C) The hash function requires O(N) time to compute based on the string length.
D) Iterating over the map's keyset is always O(N).

### Question 18
What is the ABA problem in lock-free concurrency, which can affect custom Ring Buffer implementations?

A) A thread observes value A, it changes to B, then back to A, causing a compare-and-swap (CAS) operation to falsely succeed despite the intermediate change.
B) A deadlock where thread A waits on thread B, and B waits on A.
C) A cache miss in the CPU L3 cache.
D) The inability to allocate memory sequentially.

### Question 19
If you need a Singleton to lazily initialize a heavy resource in a thread-safe manner without synchronization overhead on every access, which pattern is best?

A) Eager initialization.
B) The Initialization-on-demand holder idiom (nested static class).
C) ThreadLocal singleton.
D) Volatile enum singleton.

### Question 20
When simulating a file system, how do you efficiently handle searching for files by name with wildcard support (e.g., `*.txt`) across nested directories?

A) Store all files in a single flat HashMap.
B) Implement a specialized Trie or use recursive DFS/BFS traversal with regex matching.
C) Rely entirely on the OS `find` command via `Runtime.exec()`.
D) Keep a separate sorted array of all file names and use binary search.
