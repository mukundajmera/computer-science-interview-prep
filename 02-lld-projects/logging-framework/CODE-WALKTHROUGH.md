# Logging Framework - Code Walkthrough

## 1. LogLevel and LogEvent
`LogLevel` is implemented as an Enum with relative integer values to easily compare severities (e.g., `DEBUG` < `INFO`).
`LogEvent` is an immutable value object capturing the context of the log message: the logger name, the level, the actual message, the current timestamp, and the name of the thread that generated the log.

## 2. Logger
The `Logger` class is the central component.
- **Level Checking:** The `getEffectiveLevel()` method climbs the tree using the `parent` reference until it finds a non-null level. If the current event's level is lower than the effective level, the log is ignored.
- **Additivity:** When an event is logged, it is dispatched to all `appenders` attached to the current logger. If `additive` is true, it recursively dispatches to the parent's appenders.

## 3. LoggerFactory
The `LoggerFactory` manages the tree structure. It maintains a singleton `Map` of logger names to `Logger` instances. When `getLogger("com.myapp.service")` is called, it ensures that `com`, `com.myapp`, and `com.myapp.service` loggers are created and properly linked with parent-child relationships. The `root` logger is the ultimate parent of all loggers.

## 4. Appenders
The `Appender` interface exposes an `append(LogEvent)` method.
- `ConsoleAppender`: Synchronously writes the formatted event to standard output.
- `InMemoryAppender`: Stores logs in a thread-safe list, primarily used for testing and validation.

## 5. AsyncLogProcessor
The `AsyncLogProcessor` isolates disk I/O or network calls from the main application threads. 
- It maintains a `BlockingQueue` of wrapper objects containing the `LogEvent` and its target `Appender`s.
- A background worker thread loops, reading from the queue and calling `append()` on the respective appenders.
- **Graceful Shutdown:** The `stop()` method sets a volatile flag and interrupts the thread (or poisons the queue), allowing it to flush the remaining queue elements before terminating to prevent log loss on application exit.
