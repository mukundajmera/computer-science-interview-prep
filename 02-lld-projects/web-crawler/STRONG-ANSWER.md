# Strong Answer: Web Crawler LLD

**Pacing Target:** 45 minutes

## 1. Introduction & Requirements Gathering (0-5 minutes)

**Say:** "To design the Web Crawler low-level components, I will focus on modeling the core entities, defining the interfaces, and ensuring thread-safe operations under high concurrency. I'll begin by outlining the core data models, then progress to the architecture, and finally address execution flow and boundaries. Our primary goal is to ensure deterministic crawl outcomes, durability of metadata, and safe frontier processing."

By establishing these constraints early, we frame the discussion around concrete engineering trade-offs. The high-level requirements dictate an injected offline graph with cycles where the crawler visits each normalized permitted URL exactly once, utilizing exact visited confirmation to prevent Bloom-filter false-positive loss.

## 2. Entity Modeling & Core Components (5-15 minutes)

**Say:** "Let's discuss the entity modeling. The core entities I have identified include URLFrontier, WorkerQueue, HTMLParser, DNSResolver, DocumentStore, and PolicyEngine. Each of these entities is designed to encapsulate both state and behavior, following object-oriented principles. For instance, we ensure that mutable state within these models is properly encapsulated and accessed only via synchronized methods or concurrent wrappers where necessary."

When modeling these entities, the system relies on clear separation of concerns. We map these objects directly to domain concepts to maintain a strong ubiquitous language. The relationships between these entities are carefully managed using robust data access layers. We also define clear boundaries and interfaces so that different subdomains can interact without tight coupling.

## 3. Design Pattern Justifications (15-25 minutes)

**Say:** "In terms of design patterns, I've incorporated the Producer-Consumer Pattern for the URL extraction and downloading pipeline, Strategy Pattern for distinct crawl policies (e.g., depth-first vs. breadth-first), and Singleton for global duplicate tracking. This choice allows for maximum extensibility."

Using Producer-Consumer Pattern for the URL extraction and downloading pipeline, Strategy Pattern for distinct crawl policies, and Singleton for global duplicate tracking provides us with the necessary flexibility. This ensures the design remains resilient against changing requirements and enables comprehensive unit testing through dependency injection.

## 4. Thread-Safety Details (25-30 minutes)

**Say:** "Handling concurrency is critical. For thread-safety, concurrent duplicate URL detection requires a thread-safe exact visited confirmation layer coupled with a memory-efficient Bloom Filter. Exact visited confirmation acts as the definitive truth, preventing Bloom-filter false-positive loss."

Additionally, immutable data structures are used where possible for read-heavy operations, minimizing the need for explicit locking. For state that must be mutated concurrently, we utilize mechanisms like `ConcurrentHashMap` and `ReentrantLock` with timeout policies.

## 5. Fetch Execution and Boundaries (30-35 minutes)

**Say:** "When executing fetches, we enforce strict boundaries to prevent exhaustive resource consumption. Robots/politeness policy, per-host concurrency, redirect depth, malformed URLs, and cancellation enforce bounded queues and no real outbound requests."

The crawler executes requests against an injected offline graph. Real outbound requests are forbidden. The fetch is wrapped in severe safety nets, including limits on redirect hops and dropping invalid formats immediately to enforce bounded queues.

## 6. Execution Flow Analysis (35-40 minutes)

**Say:** "The execution flow involves a FetcherWorker acquiring tasks from the URLFrontier, checking robots and canonicalizing URLs, and performing graph traversal on the injected offline graph. Deduping and enqueueing extracted links follows strict visited confirmation."

The execution flow ensures that the crawler visits each normalized permitted URL exactly once. The combination of a memory-efficient Bloom Filter coupled with exact visited confirmation allows the system to remain highly performant while maintaining deterministic accuracy for the injected offline graph.

## 7. Evolution across versions (40-45 minutes)

**Say:** "Finally, the implementation evolves across versions. v1-basic focuses on the single-thread frontier and basic deduplication. v2-extended introduces the pluggable URL normalizer, politeness policies, and robots.txt handling. v3-optimized introduces the concurrent fetch pipeline, thread-safe partitioned queues, exact visited confirmation, and bounds handling."

This progression demonstrates the transition from a simple, unconstrained implementation to a robust, thread-safe, and bounded concurrent system. It highlights the importance of managing memory and concurrency efficiently in a highly scalable web crawler.
