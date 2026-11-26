# Logging Framework - Follow-Up Questions

## Follow-up questions
1. **How would you implement Mapped Diagnostic Context (MDC)?**
   - Use `ThreadLocal` storage to keep a map of contextual data (e.g., request ID, user ID). The `LogEvent` captures a copy of this map at creation time so it can be formatted appropriately, even if processed asynchronously by a different thread.

2. **How would you handle logging failures (e.g., disk full)?**
   - Introduce an internal error reporting mechanism or fallback appender (like standard error). The application itself should not crash due to an `IOException` in an appender.

## Variants and extensions
- **Rolling File Appender:** Implement an appender that writes to a file and rotates the file based on size (e.g., > 10MB) or time (e.g., daily).
- **Zero-Allocation Logging:** For ultra-low latency systems, avoid creating new `LogEvent` objects. Use an LMAX Disruptor ring buffer where events are pre-allocated and updated in place, requiring a garbage-free path.

## Interviewer probes to prepare
- "What happens to the latency of `logger.info()` if the asynchronous queue is entirely full?"
- "If `com.app` has a FileAppender and `com.app.service` has a ConsoleAppender, how many times is a log printed, and where, when logging to `com.app.service`?"
- "How do you ensure thread safety when modifying the `Logger`'s level at runtime?"

## Cross-links
- [Design](DESIGN.md)
- [Pitfalls](PITFALLS.md)
