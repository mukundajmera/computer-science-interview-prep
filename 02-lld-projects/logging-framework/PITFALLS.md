# Logging Framework - Common Pitfalls

## 1. String Interpolation Before Level Check
- **Signal:** Passing expensive string concatenations or method calls directly to log methods (e.g., `logger.debug("Data: " + serialize(largeObject))`).
- **Root Cause:** The expression is evaluated before the logging framework decides if the `DEBUG` level is enabled.
- **Mitigation:** Use parameterized logging (e.g., `logger.debug("Data: {}", largeObject)`) or explicitly check the level first (`if (logger.isDebugEnabled()) { ... }`).
- **Validation:** Check CPU profiling during high-traffic trace-level operations.

## 2. Deadlock During Logger Reconfiguration
- **Signal:** Application threads freeze when logging configuration is dynamically reloaded.
- **Root Cause:** Acquiring multiple locks in different orders when updating appender lists or levels across the logger hierarchy.
- **Mitigation:** Use concurrent data structures (e.g., `CopyOnWriteArrayList` for appenders, volatile references for levels) to avoid holding explicit locks during standard logging operations.

## 3. Unbounded Queue Causing OOM
- **Signal:** OutOfMemoryError during traffic spikes.
- **Root Cause:** The async logging queue is unbounded, and producers are much faster than the slow I/O consumer thread.
- **Mitigation:** Use a bounded blocking queue with a defined policy for when the queue is full (e.g., drop latest, drop oldest, or block producer temporarily).
- **Validation:** Stress test logging with a high concurrency load and measure memory usage.

## 4. Missing Graceful Shutdown
- **Signal:** Logs from the last few seconds of application life are lost.
- **Root Cause:** Background threads are marked as daemon threads or forcefully killed without flushing the queue.
- **Mitigation:** Register JVM shutdown hooks or expose an explicit `stop()` method that flushes the remaining queue before allowing the thread to die.
