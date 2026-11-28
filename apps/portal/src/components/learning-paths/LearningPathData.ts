export interface PathItem {
  id: string;
  title: string;
  href: string;
  description: string;
  estimatedHours: number;
}

export interface PathCategory {
  category: string;
  items: PathItem[];
}

export interface LearningPath {
  id: string;
  title: string;
  subtitle: string;
  targetRole: string;
  description: string;
  durationWeeks: number;
  milestones: PathCategory[];
}

export const LEARNING_PATHS_DATA: LearningPath[] = [
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
            href: "/hld/payment-system",
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
    ],
  },
  {
    id: "staff",
    title: "Staff+ Engineer",
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
        category: "3. Enterprise Platforms & Org Architecture",
        items: [
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
  {
    id: "genai",
    title: "GenAI Specialist",
    subtitle: "RAG, Semantic Caching, Multi-Agent & Foundational AI Ops",
    targetRole: "ML/AI Engineers, GenAI Architects",
    durationWeeks: 8,
    description: "Deep dive into state-of-the-art architectures for generative AI applications, reasoning agents, and semantic infrastructure.",
    milestones: [
      {
        category: "1. RAG & Core GenAI Architecture",
        items: [
          {
            id: "genai-rag",
            title: "Production RAG Architecture",
            href: "/genai",
            description: "Vector chunking strategies, dense retrieval, re-ranking pipelines, and evaluation metrics.",
            estimatedHours: 7,
          },
          {
            id: "genai-cache",
            title: "Semantic Caching & LLM Gateway",
            href: "/genai",
            description: "Cosine similarity thresholds, prompt caching, token budgets, and fallback routing.",
            estimatedHours: 6,
          },
        ],
      },
      {
        category: "2. Autonomous Agents",
        items: [
          {
            id: "genai-agents",
            title: "Multi-Agent Orchestration & Tool Dispatch",
            href: "/genai",
            description: "Agent state graphs, sandboxed execution boundaries, evaluation loops, and context budgeting.",
            estimatedHours: 9,
          },
        ],
      }
    ],
  }
];
