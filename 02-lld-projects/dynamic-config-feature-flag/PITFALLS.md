# Pitfalls: Dynamic Configuration & Feature Flag Service

## 1. Non-Deterministic Percentage Rollouts
**The Trap:** Using a random number generator (e.g., `Math.random()` or `random.random()`) during the `evaluate()` call to determine if a user falls into the rollout bucket.
**The Consequence:** A user might refresh the page and suddenly lose access to a feature, then regain it on the next refresh. This creates a terrible user experience and invalidates A/B test data.
**The Fix:** Use a stable string hashing algorithm (like MD5) on the combination of the `userId` and the `flagKey` to deterministically map a user to a bucket between 0 and 99.

## 2. Unstable Hashing in Python
**The Trap:** Using Python's built-in `hash()` function for deterministic rollouts.
**The Consequence:** Since Python 3.3, string hashing is randomized (salted) per process for security reasons (`PYTHONHASHSEED`). A user might hash to bucket 5 in one container, but bucket 95 in another container, or change buckets completely upon deployment.
**The Fix:** Always use a stable cryptographic hash from `hashlib`, such as `hashlib.md5(f"{flag}_{user}".encode()).hexdigest()`.

## 3. Read Bottlenecks via Coarse Locking
**The Trap:** Wrapping the entire `evaluate()` method or the internal dictionary in a single massive `synchronized` block or `Lock` to handle updates safely.
**The Consequence:** In a highly concurrent web server, thousands of threads evaluating flags per second will block each other, causing massive latency spikes and degrading application performance.
**The Fix:** Optimize for reads. Use concurrent data structures (like `ConcurrentHashMap` in Java) and immutable flag configuration objects so updates can be applied atomically via reference swapping without blocking readers.

## 4. ConcurrentModificationException in Observers
**The Trap:** Iterating over a standard `List` of observers during a flag update, while another thread is simultaneously trying to `subscribe` or `unsubscribe` from that flag.
**The Consequence:** The application throws an exception and crashes the update thread, failing to notify subsequent observers.
**The Fix:** Use thread-safe collections for observer lists, such as `CopyOnWriteArrayList` in Java, which handles concurrent iteration safely.

## 5. Over-engineering the Rule Engine
**The Trap:** Trying to build a Turing-complete language or writing a complex lexer/parser for the rule engine.
**The Consequence:** Wasted time, fragile code, and massive complexity.
**The Fix:** Stick to the Composite pattern with basic logical operators (AND/OR) and simple comparators (Equals, GreaterThan). Rely on simple data structures (like a JSON-like map) to represent the rules in memory.

## 6. Missing Default Fallbacks
**The Trap:** Throwing an exception or returning `null` if a flag doesn't exist or a context attribute is missing.
**The Consequence:** If the configuration server goes down or a flag is accidentally deleted, the application crashes or throws NullPointerExceptions.
**The Fix:** Every `evaluate` call should require a hardcoded `defaultValue` that the system defaults to gracefully on any error or missing state.
