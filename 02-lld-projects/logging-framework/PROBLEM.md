# Logging Framework - Problem Statement

## Problem Description
Design and implement an in-memory Logging Framework similar to standard architectural patterns found in Log4j or SLF4J. The framework should allow applications to log messages with various severity levels and route them to multiple destinations (e.g., Console, File, or In-Memory).

## Functional Requirements
- **Log Levels:** Support a standard set of log levels (e.g., TRACE, DEBUG, INFO, WARN, ERROR, FATAL).
- **Hierarchical Logger Naming:** Loggers should support hierarchical naming (e.g., `com.myapp.service`).
- **Level Inheritance:** If a logger doesn't have an explicitly set level, it should inherit the level from its closest parent logger.
- **Pluggable Appenders:** Support multiple destinations for logs, such as Console, File, and In-Memory.
- **Additivity:** Log messages should propagate to parent logger appenders unless configured otherwise.
- **Asynchronous Logging:** Support an asynchronous logging pipeline (e.g., using a ring buffer or blocking queue) to avoid blocking the main application threads.
- **Formatting:** Allow formatting of log events using a pattern layout.

## Non-Functional Requirements
- **Performance:** Logging must add minimal latency to the application.
- **Thread Safety:** Loggers and appenders must be thread-safe as they will be accessed by multiple application threads concurrently.
- **Reliability:** The framework must not crash the application due to logging errors.
- **Extensibility:** Easy to add new appenders or formatters.

## Constraints
- Standard library only (no external frameworks like Log4j, SLF4J).
- In-memory implementation for demonstration.

## Clarifying Questions
- Q: What happens if the asynchronous queue is full?
  A: For this implementation, we can block or drop logs depending on the configured policy, but simple blocking or dropping is acceptable for the basic version.
- Q: Do we need dynamic configuration reloading?
  A: Not required for the core implementation.

## Core Entities
- **Logger:** The primary entry point for applications to log messages.
- **LoggerFactory:** Creates and manages the hierarchy of loggers.
- **LogLevel:** Enumeration of log severity.
- **LogEvent:** Represents a single logging occurrence with timestamp, level, message, and thread info.
- **Appender:** Destination for the log messages.
- **Formatter / Layout:** Formats the LogEvent into a string.
- **AsyncLogProcessor:** Manages asynchronous dispatch of log events to appenders.
