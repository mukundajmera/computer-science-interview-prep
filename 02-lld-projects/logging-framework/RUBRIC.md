# Logging Framework - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | Strong signal |
| :--- | :--- | :--- |
| **Hierarchy Management** | 20% | Correct implementation of dot-separated logger names, parent-child linking, and effective level inheritance. |
| **Concurrency & Async** | 30% | Correct usage of BlockingQueue, thread safety in Logger/Appender state, and safe producer-consumer background worker. |
| **Additivity Propagation** | 15% | Properly traverses parents to invoke appenders unless additivity flag halts it. |
| **Design Patterns** | 15% | Clear separation of concerns using Factory, Strategy (Appenders), and Chain of Responsibility. |
| **Graceful Shutdown** | 20% | Ensures no logs are dropped during application shutdown; background thread flushes pending events. |

## Performance Bands

- **Strong Hire:** Implements all core features flawlessly, including hierarchical loggers and level inheritance. Asynchronous processing is robust, properly handles thread safety, and includes a graceful shutdown mechanism. Can discuss Disruptor pattern or MDC.
- **Hire:** Implements the core hierarchy and async processing. May have minor bugs in additivity or shutdown sequence, but understands and can fix them when prompted. 
- **Lean Hire:** Missing one or two features (e.g., additivity, or hierarchical parent linking is flat instead of tree-based). Asynchronous logging is somewhat naive but functionally works.
- **No Hire:** Synchronous I/O blocks worker threads significantly. Broken logger hierarchy inheritance. Significant memory leaks or thread safety issues (e.g., unsynchronized shared state leading to race conditions).

## Cross-links
- [Problem](PROBLEM.md)
- [Design](DESIGN.md)
- [Pitfalls](PITFALLS.md)
