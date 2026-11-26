export interface MilestoneItem {
  id: string;
  title: string;
  href: string;
  description: string;
  estimatedHours: number;
}

export interface LearningTrack {
  id: "junior" | "mid" | "senior" | "staff";
  title: string;
  subtitle: string;
  targetRole: string;
  description: string;
  durationWeeks: number;
  milestones: {
    category: string;
    items: MilestoneItem[];
  }[];
}

export const LEARNING_PATHS: LearningTrack[] = [
  {
    id: "junior",
    title: "Junior SDE (SDE I)",
    subtitle: "Foundations & Clean Object-Oriented Code",
    targetRole: "New Grads, SDE I, Frontend/Backend transitioning to full-stack",
    durationWeeks: 6,
    description: "Build rock-solid foundations in object-oriented analysis, core CS fundamentals, essential GoF design patterns, and classic low-level design interview problems.",
    milestones: [
      {
        category: "1. Core CS & Big-O Foundations",
        items: [
          {
            id: "jun-th-big-o",
            title: "Time & Space Complexity Analysis",
            href: "/theory",
            description: "Master asymptotic analysis, amortized time complexity, and recursion stack memory bounds.",
            estimatedHours: 4,
          },
          {
            id: "jun-th-ds-basics",
            title: "Fundamental Data Structures",
            href: "/theory",
            description: "Review arrays, linked lists, stacks, queues, hash tables, and binary trees.",
            estimatedHours: 6,
          },
        ],
      },
      {
        category: "2. Essential Design Patterns",
        items: [
          {
            id: "jun-pat-factory",
            title: "Factory Method & Abstract Factory",
            href: "/patterns/creational/factory-method",
            description: "Decouple object creation logic from client consumers.",
            estimatedHours: 3,
          },
          {
            id: "jun-pat-strategy",
            title: "Strategy Pattern",
            href: "/patterns/behavioral/strategy",
            description: "Encapsulate interchangeable business algorithms cleanly.",
            estimatedHours: 3,
          },
          {
            id: "jun-pat-observer",
            title: "Observer Pattern",
            href: "/patterns/behavioral/observer",
            description: "Build decoupled event-driven pub-sub notifications.",
            estimatedHours: 3,
          },
          {
            id: "jun-pat-singleton",
            title: "Singleton & Thread Safety",
            href: "/patterns/creational/singleton",
            description: "Manage global resource access safely with thread-safe lazy loading.",
            estimatedHours: 2,
          },
        ],
      },
      {
        category: "3. Beginner LLD Interview Problems",
        items: [
          {
            id: "jun-lld-parking",
            title: "Parking Lot System",
            href: "/lld/parking-lot",
            description: "Multi-level vehicle parking, spot sizing, and hourly ticket calculations.",
            estimatedHours: 5,
          },
          {
            id: "jun-lld-tictactoe",
            title: "Tic-Tac-Toe Game",
            href: "/lld/tic-tac-toe",
            description: "State modeling, board coordinates, winning conditions, and AI strategies.",
            estimatedHours: 4,
          },
          {
            id: "jun-lld-vending",
            title: "Vending Machine",
            href: "/lld/vending-machine",
            description: "State pattern lifecycle: idle, coin-inserted, dispensing, out-of-stock.",
            estimatedHours: 4,
          },
          {
            id: "jun-lld-snake",
            title: "Snake and Ladder",
            href: "/lld/snake-and-ladder",
            description: "Modular board entities, extensible obstacles, and multi-player turns.",
            estimatedHours: 4,
          },
        ],
      },
    ],
  },
  {
    id: "mid",
    title: "Mid-Level SDE (SDE II)",
    subtitle: "High-Frequency LLD & Distributed System Building Blocks",
    targetRole: "Software Engineers with 2–5 years targeting Tier-1 tech SDE II roles",
    durationWeeks: 8,
    description: "Transition from local object-oriented modeling to scalable, multi-threaded systems and foundational distributed system building blocks.",
    milestones: [
      {
        category: "1. Concurrency & Advanced LLD Patterns",
        items: [
          {
            id: "mid-lld-elevator",
            title: "Elevator System (SCAN Scheduling)",
            href: "/lld/elevator-system",
            description: "Concurrent request queues, load-balanced dispatching, and directional SCAN heuristics.",
            estimatedHours: 6,
          },
          {
            id: "mid-lld-movie",
            title: "Movie Ticket Booking",
            href: "/lld/movie-ticket-booking",
            description: "Distributed seat locking, concurrency deduplication, and transaction timeouts.",
            estimatedHours: 6,
          },
          {
            id: "mid-lld-ratelimit",
            title: "Rate Limiter (Token Bucket / Sliding Window)",
            href: "/lld/rate-limiter",
            description: "Atomic counters, sliding logs, token replenishment, and HTTP 429 backoff.",
            estimatedHours: 6,
          },
          {
            id: "mid-lld-cache",
            title: "Multi-Policy In-Memory Cache (LRU / LFU)",
            href: "/lld/multi-policy-cache",
            description: "O(1) doubly linked lists, frequency buckets, and thread-safe read/write eviction.",
            estimatedHours: 5,
          },
        ],
      },
      {
        category: "2. Core HLD Building Blocks",
        items: [
          {
            id: "mid-hld-sharding",
            title: "Database Sharding & Consistent Hashing",
            href: "/hld-concepts",
            description: "Virtual nodes, ring partitioning, rebalancing data, and scatter-gather queries.",
            estimatedHours: 6,
          },
          {
            id: "mid-hld-caching",
            title: "Caching Strategies & Cache Invalidation",
            href: "/hld-concepts",
            description: "Cache-aside, write-through, write-behind, and thundering herd mitigation.",
            estimatedHours: 5,
          },
          {
            id: "mid-hld-mq",
            title: "Message Queues & Event Streaming",
            href: "/hld-concepts",
            description: "At-least-once vs exactly-once delivery, consumer groups, and partition ordering.",
            estimatedHours: 6,
          },
        ],
      },
      {
        category: "3. Foundational HLD Case Studies",
        items: [
          {
            id: "mid-hld-url",
            title: "URL Shortener (TinyURL)",
            href: "/hld/url-shortener",
            description: "Base62 encoding, pre-generated ID services, and read-heavy caching.",
            estimatedHours: 6,
          },
          {
            id: "mid-hld-newsfeed",
            title: "Social News Feed (Twitter/Facebook)",
            href: "/hld/news-feed-system",
            description: "Fanout-on-write vs fanout-on-read, Redis sorted sets, and celebrity user handling.",
            estimatedHours: 7,
          },
        ],
      },
    ],
  },
  {
    id: "senior",
    title: "Senior SDE (SDE III)",
    subtitle: "High-Scale Distributed Systems, Consensus & Fault Tolerance",
    targetRole: "Senior Engineers (5+ years) targeting Staff/Senior interview loops",
    durationWeeks: 10,
    description: "Master consensus protocols, global distributed transactions, resilient streaming pipelines, payment architectures, and GenAI RAG systems.",
    milestones: [
      {
        category: "1. Consensus & Distributed Data Foundations",
        items: [
          {
            id: "sen-th-raft",
            title: "Raft Consensus Protocol",
            href: "/theory",
            description: "Leader election, log replication, commit safety, and network split-brain handling.",
            estimatedHours: 8,
          },
          {
            id: "sen-th-trans",
            title: "Distributed Transactions: 2PC vs Saga",
            href: "/theory",
            description: "Two-Phase Commit coordinator bottlenecks vs choreographed/orchestrated Sagas.",
            estimatedHours: 7,
          },
          {
            id: "sen-th-hash",
            title: "Advanced Hash Tables in Low-Latency Storage",
            href: "/theory",
            description: "Robin Hood probing, Hopscotch bitmaps, Cuckoo displacement, and Swiss Table SIMD.",
            estimatedHours: 6,
          },
        ],
      },
      {
        category: "2. Complex HLD Case Studies",
        items: [
          {
            id: "sen-hld-payment",
            title: "Distributed Payment Gateway & Double-Entry Ledger",
            href: "/hld/payment-system-hld",
            description: "Idempotency keys, reconciliation engines, settlement pipelines, and ACID ledgering.",
            estimatedHours: 8,
          },
          {
            id: "sen-hld-video",
            title: "Video Streaming Platform (YouTube / Netflix)",
            href: "/hld/video-streaming",
            description: "Adaptive bitrate streaming (HLS/DASH), CDN edge caching, and chunked video transcode.",
            estimatedHours: 8,
          },
          {
            id: "sen-hld-collab",
            title: "Collaborative Document Editor (Google Docs)",
            href: "/hld/collaborative-doc-editor",
            description: "Operational Transformation (OT) vs CRDTs, WebSocket broadcast, and state reconciliation.",
            estimatedHours: 8,
          },
        ],
      },
      {
        category: "3. GenAI System Design",
        items: [
          {
            id: "sen-genai-rag",
            title: "Production RAG Architecture",
            href: "/genai",
            description: "Vector chunking strategies, dense retrieval, re-ranking pipelines, and evaluation metrics.",
            estimatedHours: 7,
          },
          {
            id: "sen-genai-cache",
            title: "Semantic Caching & LLM Gateway",
            href: "/genai",
            description: "Cosine similarity thresholds, prompt caching, token budgets, and fallback routing.",
            estimatedHours: 6,
          },
        ],
      },
    ],
  },
  {
    id: "staff",
    title: "Staff & Principal Engineer",
    subtitle: "Multi-Region Active-Active, Failure Domains & System Architecture",
    targetRole: "Staff+, Principal Engineers, Technical Architects, VP/Directors of Engineering",
    durationWeeks: 12,
    description: "Lead enterprise-scale technical decisions: active-active multi-region replication, zero-downtime database migrations, storage engine internals, and autonomous agent orchestration.",
    milestones: [
      {
        category: "1. Global Multi-Region & High Availability",
        items: [
          {
            id: "stf-hld-multi-region",
            title: "Active-Active Multi-Region Database Architecture",
            href: "/hld-concepts",
            description: "Cross-region conflict resolution (LWW vs CRDTs), replication lag, and geo-DNS routing.",
            estimatedHours: 10,
          },
          {
            id: "stf-hld-disaster",
            title: "Disaster Recovery & Failure Domain Isolation",
            href: "/hld-concepts",
            description: "Blast radius containment, cell-based architectures, and chaos engineering practices.",
            estimatedHours: 8,
          },
        ],
      },
      {
        category: "2. Storage Internals & Custom Infrastructure",
        items: [
          {
            id: "stf-lld-lsm",
            title: "LSM-Tree & WAL In-Memory Engine",
            href: "/lld/key-value-store-lsm",
            description: "MemTable, SSTable immutability, compaction heuristics (leveled vs size-tiered), and bloom filters.",
            estimatedHours: 8,
          },
          {
            id: "stf-hld-s3",
            title: "Distributed Object Store (S3-like)",
            href: "/hld/distributed-cloud-storage-s3",
            description: "Erasure coding (Reed-Solomon), metadata clusters, and multi-petabyte volume servers.",
            estimatedHours: 10,
          },
        ],
      },
      {
        category: "3. Enterprise GenAI Platforms & Org Architecture",
        items: [
          {
            id: "stf-genai-agents",
            title: "Multi-Agent Orchestration & Tool Dispatch",
            href: "/genai",
            description: "Agent state graphs, sandboxed execution boundaries, evaluation loops, and context budgeting.",
            estimatedHours: 9,
          },
          {
            id: "stf-arch-tradeoffs",
            title: "Engineering Trade-offs & Architecture Decision Records (ADRs)",
            href: "/theory",
            description: "Formalizing technical trade-offs, driving cross-team consensus, and managing tech debt.",
            estimatedHours: 6,
          },
        ],
      },
    ],
  },
];
