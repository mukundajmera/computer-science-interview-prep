# Logging Framework - Design

## System Architecture
The application retrieves a `Logger` from the `LoggerFactory`. When a logging method (e.g., `info()`) is called, the logger checks if the event's level is enabled. If it is, a `LogEvent` is created and either sent directly to the `Appender`s (synchronous) or added to an `AsyncLogProcessor` queue (asynchronous).

## Class Diagram

```mermaid
classDiagram
    class LoggerFactory {
        - Map loggers
        - Logger rootLogger
        + getLogger(String name)
    }
    
    class Logger {
        - String name
        - LogLevel level
        - Logger parent
        - List Appender appenders
        - boolean additive
        + info(String msg)
        + debug(String msg)
        - log(LogLevel level, String msg)
        + getEffectiveLevel()
    }
    
    class LogEvent {
        - String loggerName
        - LogLevel level
        - String message
        - long timestamp
        - String threadName
    }
    
    class LogLevel {
        <<enumeration>>
        TRACE, DEBUG, INFO, WARN, ERROR, FATAL
    }
    
    class Appender {
        <<interface>>
        + append(LogEvent event)
    }
    
    class ConsoleAppender {
        + append(LogEvent event)
    }
    
    class InMemoryAppender {
        - List logs
        + append(LogEvent event)
    }
    
    class AsyncLogProcessor {
        - BlockingQueue queue
        - Thread worker
        + submit(LogEvent event, List appenders)
        + stop()
    }
    
    LoggerFactory --> Logger : manages
    Logger --> Logger : parent
    Logger --> LogLevel
    Logger --> Appender
    Logger ..> LogEvent : creates
    ConsoleAppender ..|> Appender
    InMemoryAppender ..|> Appender
    AsyncLogProcessor --> LogEvent : processes
```

## Sequence Diagram: Async Logging Pipeline

```mermaid
sequenceDiagram
    participant App as Application Thread
    participant L as Logger
    participant ALP as AsyncLogProcessor
    participant Q as BlockingQueue
    participant WT as Worker Thread
    participant A as Appender

    App->>L: info("User login")
    L->>L: check getEffectiveLevel()
    L->>L: create LogEvent
    L->>ALP: submit(event, appenders)
    ALP->>Q: put(event)
    ALP-->>L: return
    L-->>App: return
    
    WT->>Q: take()
    Q-->>WT: return event
    WT->>A: append(event)
```

## Design Patterns Used
- **Chain of Responsibility:** Hierarchy tree for level inheritance and appender additivity.
- **Factory:** `LoggerFactory` to create and manage logger singletons per name.
- **Strategy:** `Appender` interface allows plugging in different logging destinations.
- **Producer-Consumer:** Used in `AsyncLogProcessor`.

## Cross-links
- [Problem Statement](PROBLEM.md)
- [Approach](APPROACH.md)
