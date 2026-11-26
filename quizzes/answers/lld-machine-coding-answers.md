# 🧠 LLD & Machine Coding Excellence Quiz - Answers

> **Answer key for the LLD & Machine Coding Excellence Quiz with technical explanations and code snippets.**

---

### Question 1
**Answer:** B) To quickly locate the bucket containing the least frequently used elements when the cache reaches capacity and an eviction is necessary.

**Explanation:**
In an O(1) LFU cache, we typically maintain two structures: a map of `key -> Node` and a map of `frequency -> DoublyLinkedList`. When the cache is full, we must evict the Least Frequently Used item. Iterating through all keys to find the minimum frequency would be O(N). By maintaining a `minFrequency` variable that updates dynamically, we can instantly access the correct `DoublyLinkedList` in O(1) time.
*   **A is incorrect** because it does not limit access counts.
*   **C is incorrect** because sorting the cache takes O(N log N) time, violating the O(1) requirement.
*   **D is incorrect** because it does not track historical averages.

```java
// O(1) eviction logic
public void evict() {
    DoublyLinkedList minFreqList = freqMap.get(minFrequency);
    Node lruNode = minFreqList.removeTail();
    keyMap.remove(lruNode.key);
    // ... update sizes ...
}
```

### Question 2
**Answer:** C) To avoid false sharing by ensuring that concurrently modified sequence variables reside on different CPU cache lines.

**Explanation:**
False sharing occurs when independent variables reside on the same CPU cache line (typically 64 bytes). If thread A modifies the producer sequence and thread B modifies the consumer sequence, the hardware cache coherency protocol will invalidate the entire cache line for both cores, causing a severe performance penalty known as "cache line bouncing". Padding forces the sequences onto separate cache lines.
*   **A is incorrect** because padding does not increase buffer capacity.
*   **B is incorrect** because padding variables do not prevent garbage collection.
*   **D is incorrect** because padding is unrelated to 32-bit JVM backward compatibility.

### Question 3
**Answer:** C) The State pattern encapsulates state-specific behavior into separate classes, adhering to the Open/Closed Principle and avoiding massive `switch` statements as complexity grows.

**Explanation:**
The State pattern represents states as distinct classes implementing a common interface. When behavior depends on the state, delegating the action to the current state object is cleaner than a monolithic `switch` block. This adheres to the Open/Closed Principle because adding a new state requires creating a new class rather than modifying existing `switch` statements.
*   **A is incorrect** because the State pattern typically uses slightly more memory due to object instances.
*   **B is incorrect** because logic is distributed among state classes, not centralized.
*   **D is incorrect** because the State pattern does not handle distributed consensus.

### Question 4
**Answer:** B) Another thread might see a partially constructed object due to instruction reordering.

**Explanation:**
Without `volatile`, the Java Memory Model allows instruction reordering. The steps to construct an object are: 1. Allocate memory, 2. Initialize object, 3. Assign reference. The compiler might reorder this to: 1. Allocate, 2. Assign reference, 3. Initialize. If thread A executes steps 1 and 2, thread B might check `instance != null` (which is true) and return a partially constructed object, leading to erratic behavior.
*   **A is incorrect** because monitor exceptions relate to incorrect `wait()`/`notify()` usage.
*   **C is incorrect** because it is unrelated to garbage collection.
*   **D is incorrect** because the `synchronized` block prevents deadlocks here, it just creates a race condition if `volatile` is missing.

### Question 5
**Answer:** B) `ReentrantLock` allows for more flexible locking semantics, such as `tryLock()` with timeouts, interruptible lock acquisition, and fairness policies.

**Explanation:**
`ReentrantLock` provides advanced features not available with intrinsic `synchronized` blocks. `tryLock(timeout)` prevents indefinite blocking. `lockInterruptibly()` allows a waiting thread to be interrupted. Fairness policies (`new ReentrantLock(true)`) ensure the longest-waiting thread acquires the lock next, preventing starvation.
*   **A is incorrect** because under low contention, `synchronized` is highly optimized and often faster.
*   **C is incorrect** because `ReentrantLock` cannot automatically prevent deadlocks (you still have to order locks correctly).
*   **D is incorrect** because `synchronized` blocks can be used anywhere.

### Question 6
**Answer:** B) Lock the `Account` objects in a globally consistent order (e.g., sorting by account ID) before performing the transfer.

**Explanation:**
Deadlocks typically occur due to "circular wait" (e.g., Thread 1 locks A then B; Thread 2 locks B then A). By enforcing a strict global ordering (always lock the account with the smaller ID first), circular wait is impossible. This is a classic solution to the Dining Philosophers problem.
*   **A is incorrect** because `sleep()` with backoff is a heuristic livelock mitigation, not a robust deadlock prevention.
*   **C is incorrect** because a global lock creates a severe bottleneck, limiting concurrency to one transfer at a time.
*   **D is incorrect** because peer-to-peer voting is overly complex for a single-node memory model.

```java
// Deadlock avoidance via lock ordering
public void transfer(Account a, Account b, double amount) {
    Account first = a.getId() < b.getId() ? a : b;
    Account second = a.getId() < b.getId() ? b : a;
    
    synchronized(first) {
        synchronized(second) {
            a.withdraw(amount);
            b.deposit(amount);
        }
    }
}
```

### Question 7
**Answer:** C) To decouple file metadata (size, blocks, permissions) from file hierarchy and names, enabling features like hard links.

**Explanation:**
Inodes store file metadata and data pointers but do not contain filenames. Dentries map names to Inodes and maintain the directory hierarchy. This separation is crucial for hard links: multiple Dentries in different directories can point to the exact same Inode, sharing the underlying data.
*   **A is incorrect** because Inodes do not perform compression.
*   **B is incorrect** because while they store permissions, that's not the primary reason for separation.
*   **D is incorrect** because Inodes point to scattered data blocks, not contiguous memory.

### Question 8
**Answer:** B) Two Stacks: an Undo stack to record executed commands and a Redo stack to hold undone commands.

**Explanation:**
The standard implementation uses two stacks. When a command executes, it is pushed onto the Undo stack. When `undo()` is called, it pops from the Undo stack, executes reverse logic, and pushes onto the Redo stack. When `redo()` is called, it pops from the Redo stack, executes forward logic, and pushes back onto the Undo stack. Any new action clears the Redo stack.
*   **A is incorrect** because HashMaps do not provide natural LIFO ordering.
*   **C is incorrect** because priority queues reorder based on comparators, breaking temporal history.
*   **D is incorrect** because a size 1 buffer only allows one level of undo.

### Question 9
**Answer:** C) The Least Recently Used (LRU) item among those with the minimum frequency.

**Explanation:**
Standard LFU cache implementations resolve frequency ties by using an LRU policy. The `DoublyLinkedList` mapped to `minFrequency` maintains access order. The tail of this list represents the least recently accessed item among the tied group, which is chosen for eviction.
*   **A is incorrect** because LFU does not consider byte size.
*   **B is incorrect** because this is MRU, which is contrary to standard cache policies.
*   **D is incorrect** because random eviction is a separate algorithm entirely.

### Question 10
**Answer:** C) By pre-allocating a fixed-size array and using wrapping read/write sequence indices (modulo arithmetic).

**Explanation:**
A Ring Buffer uses a fixed-size array pre-allocated at startup. It maintains a read pointer and a write pointer. As items are added or removed, pointers increment and wrap around to the start using modulo arithmetic (e.g., `index = sequence & (size - 1)` if size is a power of two). This provides zero-allocation, O(1) performance.
*   **A is incorrect** because dynamic resizing requires O(N) copying.
*   **B is incorrect** because background threads are not needed for this core logic.
*   **D is incorrect** because page tables are an OS concept, not application-level array indexing.

### Question 11
**Answer:** B) Throwing an `IllegalStateException` inside a state transition method if the current state is invalid for the requested action.

**Explanation:**
In an FSM, state transitions must be rigorously validated. If a requested transition is not defined (e.g., transitioning directly from CREATED to SHIPPED), the standard Java practice is to throw an `IllegalStateException` to fail fast and loudly.
*   **A is incorrect** because interceptors are generally overkill for simple Enum logic.
*   **C is incorrect** because setting state to null leads to NullPointerExceptions.
*   **D is incorrect** because `AtomicState` is not a standard Java class.

### Question 12
**Answer:** B) Reflection attacks and serialization-induced multiple instantiations.

**Explanation:**
Joshua Bloch famously recommended the Enum Singleton in *Effective Java*. The JVM guarantees that an Enum is initialized exactly once, inherently protecting against reflection attacks (which can bypass private constructors) and serialization issues (which deserialize into new instances unless `readResolve` is implemented).
*   **A is incorrect** because Enums can still hold large structures that leak memory.
*   **C is incorrect** because Enums can theoretically deadlock if static initializers are circular.
*   **D is incorrect** because the ABA problem relates to atomic variables, not instantiation.

### Question 13
**Answer:** B) It requires a manual `unlock()` in a `finally` block, increasing the risk of lock leaks if not coded carefully.

**Explanation:**
Unlike the `synchronized` keyword, which automatically releases monitors when a block is exited (even via exception), `ReentrantLock` requires explicit `unlock()` calls. This must be placed in a `finally` block to ensure release. Failure to do so leads to permanent deadlocks or lock leaks.
*   **A is incorrect** because `tryLock` explicitly *avoids* permanent blocking.
*   **C is incorrect** because `ReentrantLock` supports multiple `Condition` variables.
*   **D is incorrect** because it is not deprecated.

### Question 14
**Answer:** D) Circular Wait

**Explanation:**
The four Coffman conditions for deadlock are: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. Imposing a strict global ordering on resource acquisition (e.g., always locking R1 before R2) guarantees that a dependency cycle (Circular Wait) cannot form.
*   **A is incorrect** because Mutual Exclusion is a requirement for locks.
*   **B is incorrect** because Hold and Wait is prevented by acquiring all locks simultaneously.
*   **C is incorrect** because No Preemption means locks cannot be forcibly taken away.

### Question 15
**Answer:** B) The Composite pattern.

**Explanation:**
The Composite pattern is used to treat individual objects (Files) and compositions of objects (Directories) uniformly. Both `File` and `Directory` implement a common `Node` or `Entry` interface, allowing directories to contain files and other directories transparently, enabling recursive operations like calculating total size.
*   **A is incorrect** because Observer handles publish/subscribe events.
*   **C is incorrect** because Flyweight minimizes memory via sharing, not hierarchy representation.
*   **D is incorrect** because Strategy encapsulates algorithms.

### Question 16
**Answer:** A) `undo()`

**Explanation:**
For the Command pattern to support undo operations, the command object must store enough state to reverse its action and expose an `undo()` method.
*   **B is incorrect** because `commit` is typically associated with transactions.
*   **C is incorrect** because `rollbackTransactions` is too specific.
*   **D is incorrect** because `log` is orthogonal to the undo mechanism.

### Question 17
**Answer:** B) Hash collisions can cause multiple items to map to the same bucket, degrading performance to O(N) if stored in a linked list.

**Explanation:**
If a poor hash function is used, or in pathological cases, multiple keys hash to the same bucket index. In standard implementations (prior to Java 8's tree bin optimization), these are stored in a linked list. Finding the correct key requires traversing this list, taking O(N) time where N is the number of items in that bucket.
*   **A is incorrect** because bytecode compilation does not alter asymptotic complexity.
*   **C is incorrect** because hash function computation is typically bounded by string length, treated as O(1) relative to map size.
*   **D is incorrect** because iterating keys is O(N), but we are asking about lookup.

### Question 18
**Answer:** A) A thread observes value A, it changes to B, then back to A, causing a compare-and-swap (CAS) operation to falsely succeed despite the intermediate change.

**Explanation:**
The ABA problem occurs when a thread reads a value (A), gets preempted, and another thread changes A to B and back to A. When the first thread resumes, its CAS instruction sees A and succeeds, incorrectly assuming the state never changed. This is often solved using versioned pointers or `AtomicStampedReference`.
*   **B is incorrect** because this describes a deadlock.
*   **C is incorrect** because this describes cache invalidation.
*   **D is incorrect** because this is memory fragmentation.

### Question 19
**Answer:** B) The Initialization-on-demand holder idiom (nested static class).

**Explanation:**
The "Holder idiom" leverages Java's classloader mechanism. The nested static class `Holder` is not loaded into memory until its `INSTANCE` field is accessed. The JVM guarantees that class initialization is thread-safe. This provides lazy initialization with zero synchronization overhead on `getInstance()` calls.
*   **A is incorrect** because eager initialization is not lazy.
*   **C is incorrect** because ThreadLocal creates one instance per thread, not a global singleton.
*   **D is incorrect** because Enum singleton is typically eager (initialized when the enum class is loaded).

```java
public class LazySingleton {
    private LazySingleton() {}
    
    private static class Holder {
        private static final LazySingleton INSTANCE = new LazySingleton();
    }
    
    public static LazySingleton getInstance() {
        return Holder.INSTANCE; // Thread-safe lazy init
    }
}
```

### Question 20
**Answer:** B) Implement a specialized Trie or use recursive DFS/BFS traversal with regex matching.

**Explanation:**
To search across a directory tree, recursive traversal (DFS) or breadth-first search (BFS) is required. During traversal, names can be matched against the wildcard pattern (e.g., converted to a regex). For highly optimized repeated prefix/suffix searches, a Trie data structure can be used.
*   **A is incorrect** because a flat HashMap destroys the hierarchical context.
*   **C is incorrect** because `Runtime.exec` violates the premise of an *in-memory* or custom LLD implementation.
*   **D is incorrect** because maintaining a sorted array across a mutating file tree is expensive O(N) insertion.
