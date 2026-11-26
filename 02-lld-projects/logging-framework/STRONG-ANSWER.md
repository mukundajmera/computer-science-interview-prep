# Strong Answer: Logging Framework

**Pacing Target:** 45 minutes

## 1. Introduction and Requirements Gathering (5 mins)
**Say:** "To design the Logging Framework, I'll start by clarifying the core requirements, both functional and non-functional, before diving into the component architecture. We want to ensure the system is extensible, highly concurrent, and fault-tolerant."

## 2. Entity Modeling (10 mins)
**Say:** "Let's define the primary entities and their relationships. For this system, the domain models encapsulate the core business rules."
The main entities are `Logger`, `Appender`, `Formatter`, `LogEvent`, `LogLevel`, `LoggerFactory`, and `AsyncLogProcessor`. 
- **`Logger`**: Receives events and filters them based on effective log levels.
- **`LoggerFactory`**: Manages the singleton instances of Loggers and establishes the logger hierarchy (e.g. `com.myapp`).
- **`Appender`**: Dictates the output destination (Console, Memory, File).
- **`AsyncLogProcessor`**: Processes log events asynchronously in the background.

## 3. Explicit Reference Contracts & Edge Cases (10 mins)
**Say:** "Systems fail and edge cases occur, so we need to anticipate and handle boundaries cleanly based on an explicitly defined contract."
- **Normal use-case**: `Logger.info("msg")` evaluates the log level, builds a `LogEvent`, gathers target appenders through the logger hierarchy, and submits it to the `AsyncLogProcessor` queue which consumes and delegates to appenders.
- **Empty/invalid input**: Requesting a logger with a null, empty, or `"root"` (case-insensitive) name explicitly falls back to returning the `root` logger. Null/empty messages are logged exactly as passed (empty/null strings) without failure.
- **Duplicate operations**: If the exact same appender is added multiple times to a logger (`Logger.addAppender(Appender)`), it will be blindly registered in the collection and processed twice, as duplicate checks are not performed. 
- **Capacity boundary**: The bounded async queue holds up to 10,000 tasks. In v1 Java, it blocks indefinitely if full. In Python v1/v3, it uses a 1.0-second timeout, dropping the log if the timeout is exceeded. In Java v3, it uses `queue.offer()` with a 1-second timeout before dropping.
- **One failure rollback**: If an `Appender` crashes with an exception during append (e.g., Disk Full), the asynchronous worker loop explicitly catches the exception and prints an error (`System.err.println` / `print(f"Appender failed: {e}")`) without crashing the core processing thread, ensuring subsequent logs continue uninterrupted.

## 4. Data Structure Rationale & Design Patterns (5 mins)
**Say:** "Choosing the right data structures is critical for meeting our latency and throughput requirements."
We utilize a concurrent Map in `LoggerFactory` for fast O(1) retrieval of loggers and bounded blocking queues (`ArrayBlockingQueue` or `LinkedBlockingQueue`) for the asynchronous processor. The `AsyncLogProcessor` handles enqueuing in `O(1)` time, while space complexity is `O(N)` based on the number of loggers and max queue size.
Key design patterns include:
- **Chain of Responsibility**: For log level and appender additivity inheritance.
- **Factory**: For providing singleton loggers.
- **Strategy**: For dynamically interchangeable appenders and formatters.

## 5. Feature Evolution and Version Deltas (5 mins)
**Say:** "As requirements expand, our framework can gracefully support additional features."
- **v1-basic**: Includes core components like Console/In-Memory appenders and basic async processing.
- **v2-extended**: Adds features like a `RollingFileAppender` (for size-based file rotation) and a `CompositeAppender`.
- **v3-optimized**: Implements a highly optimized async processor that batches queue drains to minimize contention and improve throughput.
Focused tests in the codebase target each explicit version rather than silently importing `v1-basic`.
