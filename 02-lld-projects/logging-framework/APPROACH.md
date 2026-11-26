# Logging Framework - Approach

## Entity Identification
The core of the system revolves around `Logger` instances created by a `LoggerFactory`. Each `Logger` contains an explicit `LogLevel` (or inherits it) and a list of `Appender`s. The `Appender` relies on a `Formatter` to turn a `LogEvent` into a final string or payload.

## Logger Hierarchy Tree & Level Inheritance
Loggers are typically identified by dot-separated names (e.g., `com.app.service`). This naturally forms a tree structure where `com` is the parent of `com.app`, which is the parent of `com.app.service`. 
When a logger's level is queried, the system checks the logger itself; if unset, it traverses up the tree to find the nearest ancestor with an explicitly set level. The `root` logger always has a default level (e.g., `INFO`).

## Appender Additivity Propagation
By default, log events are passed not only to the current logger's appenders but also to the appenders of all its ancestors. This is known as additivity. The traversal stops if a logger sets its `additivity` flag to false.

## Synchronous vs Asynchronous Logging
- **Synchronous Logging:** The thread making the log call executes the appender logic (e.g., disk I/O, network call). This blocks the application thread, potentially reducing throughput.
- **Asynchronous Logging:** The application thread places the `LogEvent` into a thread-safe queue (or ring buffer) and returns immediately. A separate background worker thread (or pool of threads) consumes events from the queue and dispatches them to the appenders.

## Ring Buffer / Producer-Consumer Model
For the asynchronous processor, a bounded blocking queue (acting as a basic ring buffer pattern) is used.
- **Producer:** Application threads generating logs.
- **Consumer:** A dedicated logging thread continuously taking events from the queue and writing them out.
- **Graceful Shutdown:** During shutdown, the processor must be signaled to stop accepting new logs and to flush all pending logs before terminating.
