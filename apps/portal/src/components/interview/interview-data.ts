/** Interview step definitions per problem type */

export type InterviewType =
  | "lld"
  | "hld"
  | "genai-hld"
  | "behavioral"
  | "coding"
  | "salary-negotiation";

export interface InterviewStep {
  title: string;
  durationMin: number;
  prompt: string;
  tips: string[];
}

export interface InterviewTemplate {
  type: InterviewType;
  label: string;
  totalMin: number;
  steps: InterviewStep[];
}

export const LLD_TEMPLATE: InterviewTemplate = {
  type: "lld",
  label: "Low-Level Design",
  totalMin: 45,
  steps: [
    {
      title: "Requirements Clarification",
      durationMin: 5,
      prompt:
        "Ask clarifying questions. Identify functional requirements, non-functional requirements, and scope.",
      tips: [
        "List at least 4-5 functional requirements",
        "Ask about concurrency and scale",
        "Define what is out of scope",
      ],
    },
    {
      title: "Core Entities & Relationships",
      durationMin: 5,
      prompt:
        "Identify the key entities (nouns) and map their relationships (has-a, is-a, uses).",
      tips: [
        "Extract nouns from requirements",
        "Distinguish composition from aggregation",
        "Note cardinality (1:1, 1:N, M:N)",
      ],
    },
    {
      title: "Design Patterns Selection",
      durationMin: 5,
      prompt:
        "Choose 2-3 design patterns and justify why each one fits the problem.",
      tips: [
        "Strategy for interchangeable behaviors",
        "Observer for event-driven updates",
        "Factory for object creation without exposing logic",
        "Singleton for shared resources (with reset for tests)",
      ],
    },
    {
      title: "Class Design",
      durationMin: 15,
      prompt:
        "Design classes with attributes, methods, interfaces, and enums. Write code.",
      tips: [
        "Start with interfaces and enums",
        "Apply Single Responsibility Principle",
        "Use meaningful names for methods",
        "Keep classes focused — avoid God classes",
      ],
    },
    {
      title: "Edge Cases & Optimizations",
      durationMin: 10,
      prompt:
        "Handle edge cases, discuss thread safety, and analyze time/space complexity.",
      tips: [
        "Null/empty inputs",
        "Concurrent access scenarios",
        "Invalid state transitions",
        "Complexity of key operations",
      ],
    },
    {
      title: "Wrap-Up & Follow-Ups",
      durationMin: 5,
      prompt:
        "Summarize your design, draw a class diagram, and discuss extensibility.",
      tips: [
        "Walk through a key use case end-to-end",
        "Discuss 2-3 follow-up extensions",
        "Mention what you would do differently with more time",
      ],
    },
  ],
};

export const HLD_TEMPLATE: InterviewTemplate = {
  type: "hld",
  label: "High-Level Design",
  totalMin: 45,
  steps: [
    {
      title: "Requirements Clarification",
      durationMin: 5,
      prompt:
        "Clarify functional and non-functional requirements. Define scale targets.",
      tips: [
        "Availability, latency, consistency targets",
        "Read:write ratio",
        "Approximate user count and traffic",
        "What is out of scope",
      ],
    },
    {
      title: "Capacity Estimation",
      durationMin: 5,
      prompt:
        "Estimate QPS, storage, and bandwidth with back-of-envelope math.",
      tips: [
        "Daily active users → QPS (divide by 86,400)",
        "Storage = record size × count × retention",
        "Bandwidth = QPS × average response size",
        "Peak = 2-3× average",
      ],
    },
    {
      title: "API Design",
      durationMin: 5,
      prompt:
        "Define core API endpoints — method, path, request/response bodies.",
      tips: [
        "Cover all functional requirements",
        "RESTful conventions",
        "Pagination for list endpoints",
        "Authentication/rate limiting mentions",
      ],
    },
    {
      title: "Data Model",
      durationMin: 5,
      prompt:
        "Design the schema, choose database type, and define indexes.",
      tips: [
        "SQL vs NoSQL — justify the choice",
        "Primary keys and indexes for query patterns",
        "Denormalize for read-heavy workloads",
        "Consider partition keys for distributed DBs",
      ],
    },
    {
      title: "High-Level Architecture",
      durationMin: 10,
      prompt:
        "Draw the component diagram. Explain read and write data flows.",
      tips: [
        "Load balancer → app servers → cache → database",
        "Include message queues for async work",
        "Show CDN for static/media content",
        "Explain both read path and write path",
      ],
    },
    {
      title: "Deep Dives",
      durationMin: 10,
      prompt:
        "Go deep on 2-3 topics: scaling, caching, key algorithms, failure handling.",
      tips: [
        "Horizontal scaling + sharding strategy",
        "Caching layer: what to cache, TTL, invalidation",
        "Handle failure scenarios gracefully",
        "Discuss consistency guarantees",
      ],
    },
    {
      title: "Trade-Offs & Wrap-Up",
      durationMin: 5,
      prompt:
        "Discuss key trade-offs and summarize your design. Answer follow-ups.",
      tips: [
        "Consistency vs availability",
        "Cost vs performance",
        "Simplicity vs extensibility",
        "What would change at 10× scale",
      ],
    },
  ],
};

export const GENAI_HLD_TEMPLATE: InterviewTemplate = {
  type: "genai-hld",
  label: "GenAI System Design",
  totalMin: 45,
  steps: [
    {
      title: "Clarify Use Case & LLM Role",
      durationMin: 5,
      prompt:
        "What does the LLM do? What are the input/output modalities? Is RAG needed?",
      tips: [
        "Distinguish LLM tasks from classic backend tasks",
        "Identify if retrieval augmentation is needed",
        "Define user expectations for quality and latency",
        "Scope V1 vs future extensions",
      ],
    },
    {
      title: "Token Budget & Cost Estimation",
      durationMin: 5,
      prompt:
        "Estimate tokens per request, cost per query, and latency waterfall.",
      tips: [
        "Input tokens = system prompt + context + query",
        "Output tokens = expected response length",
        "Cost = (input × input price) + (output × output price)",
        "Latency = embedding + retrieval + LLM generation",
      ],
    },
    {
      title: "Architecture Sketch",
      durationMin: 10,
      prompt:
        "Draw the end-to-end architecture. Show ingestion pipeline and query pipeline.",
      tips: [
        "Ingestion: document → chunk → embed → store",
        "Query: question → embed → retrieve → rerank → generate",
        "Show vector store, embedding service, LLM gateway",
        "Include async/batch vs real-time paths",
      ],
    },
    {
      title: "LLM Pipeline Deep Dive",
      durationMin: 10,
      prompt:
        "Deep dive into chunking, embedding, retrieval, ranking, and prompt construction.",
      tips: [
        "Chunking strategy and size trade-offs",
        "Embedding model selection and dimensions",
        "Vector search vs hybrid (vector + BM25)",
        "Prompt template with system instructions + context + query",
      ],
    },
    {
      title: "Safety & Guardrails",
      durationMin: 5,
      prompt:
        "Discuss input filtering, output validation, PII handling, and hallucination mitigation.",
      tips: [
        "Prompt injection detection",
        "Groundedness check for answers",
        "PII redaction in inputs and outputs",
        "Content policy enforcement",
      ],
    },
    {
      title: "Evaluation & Observability",
      durationMin: 5,
      prompt:
        "Define offline metrics, online monitoring, and feedback loops.",
      tips: [
        "Offline: faithfulness, relevance, correctness",
        "Online: latency, error rate, token usage, user satisfaction",
        "A/B testing for model/prompt changes",
        "Human feedback → golden evaluation set",
      ],
    },
    {
      title: "Wrap-Up",
      durationMin: 5,
      prompt:
        "Summarize trade-offs and discuss follow-up extensions.",
      tips: [
        "Cost vs quality trade-offs",
        "Chunk size vs retrieval accuracy",
        "Managed vs self-hosted vector DB",
        "Multi-turn chat, streaming, fine-tuning",
      ],
    },
  ],
};

export const BEHAVIORAL_TEMPLATE: InterviewTemplate = {
  type: "behavioral",
  label: "Behavioral Interview",
  totalMin: 45,
  steps: [
    {
      title: "Clarify Round Context",
      durationMin: 5,
      prompt:
        "Confirm role level, interviewer context, and what they are most likely evaluating.",
      tips: [
        "Identify if this is recruiter, manager, leadership, or cross-functional round",
        "Check which signal areas matter most for this round",
        "Set a concise response approach before starting",
      ],
    },
    {
      title: "Select Story by Signal Fit",
      durationMin: 6,
      prompt:
        "Choose the strongest story for this question based on signal fit and level scope.",
      tips: [
        "Prioritize ownership, ambiguity, conflict, and communication coverage",
        "Pick one story with explicit decisions and measurable outcomes",
        "Avoid reusing a weak or overused story",
      ],
    },
    {
      title: "Deliver Core Narrative",
      durationMin: 8,
      prompt:
        "Deliver a concise CARL response: context, actions, results, learnings.",
      tips: [
        "Keep context brief and action-heavy",
        "Use clear ownership language",
        "Include metric or operational evidence in results",
      ],
    },
    {
      title: "Deep Dive Decisions and Trade-offs",
      durationMin: 8,
      prompt:
        "Defend your choices under probing questions and compare alternatives.",
      tips: [
        "Explain what you rejected and why",
        "Link decisions to risk, speed, quality, and stakeholder impact",
        "Stay consistent under interruption",
      ],
    },
    {
      title: "Communication and Stakeholder Handling",
      durationMin: 6,
      prompt:
        "Show how you aligned stakeholders and handled disagreement professionally.",
      tips: [
        "Describe alignment sequence, not just final agreement",
        "Show relationship outcomes after conflict",
        "Demonstrate influence without authority",
      ],
    },
    {
      title: "Reflection and Growth",
      durationMin: 6,
      prompt:
        "Explain what you changed in your operating style after this experience.",
      tips: [
        "Avoid generic lessons",
        "Give one concrete behavior/process change",
        "Connect learning to future execution quality",
      ],
    },
    {
      title: "Wrap-Up",
      durationMin: 6,
      prompt:
        "Summarize impact and close with one strong follow-up invitation.",
      tips: [
        "State business/team impact in one line",
        "Reinforce role-level signal",
        "Offer deeper dive on trade-offs or stakeholder decisions",
      ],
    },
  ],
};

export const CODING_TEMPLATE: InterviewTemplate = {
  type: "coding",
  label: "Coding Interview (Pattern-Oriented)",
  totalMin: 45,
  steps: [
    {
      title: "Clarify Inputs and Constraints",
      durationMin: 5,
      prompt:
        "Confirm data constraints, ordering/contiguity/monotonicity assumptions, output format, and mutability requirements.",
      tips: [
        "Ask whether order, contiguity, or predicate monotonicity must be preserved",
        "Confirm index/value return contract",
        "Check in-place mutation expectations",
      ],
    },
    {
      title: "Select Pattern and Invariant",
      durationMin: 7,
      prompt:
        "Choose the template (pointer elimination, sliding window, binary search, partition, anchor+sweep, or deque) and state the core invariant.",
      tips: [
        "Define each pointer, window boundary, or search boundary role before coding",
        "State elimination, validity, monotonicity, or maintained-state logic explicitly",
        "Mention termination argument",
      ],
    },
    {
      title: "Implement Core Loop",
      durationMin: 15,
      prompt:
        "Write the core loop with clear movement rules, state updates, and boundary handling.",
      tips: [
        "Move only the justified pointer, window boundary, or search boundary",
        "Update counts, sums, deques, or duplicate handling consistently",
        "Keep loop guard simple and verifiable",
      ],
    },
    {
      title: "Validate with Edge Cases",
      durationMin: 8,
      prompt:
        "Walk through edge inputs and prove invariant holds after each iteration.",
      tips: [
        "Empty/small input cases",
        "All-equal, strictly monotonic, and invalid-window cases",
        "No-solution and all-solution boundaries",
      ],
    },
    {
      title: "Complexity and Trade-offs",
      durationMin: 5,
      prompt:
        "Defend time/space complexity and compare with alternative approaches.",
      tips: [
        "State exact Big-O",
        "Discuss sort-first, hash-map, deque, or predicate-cost trade-offs",
        "Mention memory vs simplicity trade-off",
      ],
    },
    {
      title: "Follow-Ups and Extension",
      durationMin: 5,
      prompt:
        "Handle one variant (counting, dedupe, index return, rolling window, answer-space search, or SD-adjacent adaptation).",
      tips: [
        "Do not rewrite from scratch",
        "Reuse same invariant where possible",
        "Narrate changes before coding",
      ],
    },
  ],
};

/** Map problem type to template */
export function getTemplate(type: InterviewType): InterviewTemplate | null {
  switch (type) {
    case "lld":
      return LLD_TEMPLATE;
    case "hld":
      return HLD_TEMPLATE;
    case "genai-hld":
      return GENAI_HLD_TEMPLATE;
    case "behavioral":
      return BEHAVIORAL_TEMPLATE;
    case "coding":
      return CODING_TEMPLATE;
    default:
      return null;
  }
}

/** Curated non-coding problems wired for Interview Mode.
 *  Coding pattern drills are discovered from solutions/coding-*.md. */
export interface InterviewProblem {
  slug: string;
  title: string;
  type: InterviewType;
  difficulty: "beginner" | "intermediate" | "advanced";
  solutionPath: string;
}

export const INTERVIEW_PROBLEMS: InterviewProblem[] = [

{
  slug: "online-auction",
  title: "Online Auction",
  type: "hld",
  difficulty: "advanced",
  solutionPath: "solutions/hld-online-auction.md",
},
{
  slug: "live-comments",
  title: "Live Comments",
  type: "hld",
  difficulty: "advanced",
  solutionPath: "solutions/hld-live-comments.md",
},
{
  slug: "social-post-search",
  title: "Social Post Search",
  type: "hld",
  difficulty: "advanced",
  solutionPath: "solutions/hld-social-post-search.md",
},
{
  slug: "price-tracking-service",
  title: "Price Tracking Service",
  type: "hld",
  difficulty: "advanced",
  solutionPath: "solutions/hld-price-tracking-service.md",
},
{
  slug: "behavioral-big-three",
  title: "Behavioral Big Three",
  type: "behavioral",
  difficulty: "intermediate",
  solutionPath: "solutions/behavioral-big-three.md",
},
{
  slug: "behavioral-leadership-deep-dive",
  title: "Leadership Deep Dive",
  type: "behavioral",
  difficulty: "advanced",
  solutionPath: "solutions/behavioral-leadership-deep-dive.md",
},
{
  slug: "behavioral-special-rounds",
  title: "Special Interview Rounds",
  type: "behavioral",
  difficulty: "advanced",
  solutionPath: "solutions/behavioral-special-rounds.md",
},
  {
    slug: "food-delivery-platform",
    title: "Food Delivery Platform",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-food-delivery-platform.md",
  },
{
    slug: "parking-lot",
    title: "Parking Lot",
    type: "lld",
    difficulty: "beginner",
    solutionPath: "solutions/lld-parking-lot.md",
  },
  {
    slug: "url-shortener",
    title: "URL Shortener",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-url-shortener.md",
  },
  {
    slug: "scaling-patterns",
    title: "Scaling Patterns (Reads/Writes/Blobs/Async)",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-patterns-read-write-blob-async.md",
  },
  {
    slug: "ride-sharing",
    title: "Ride Sharing",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-ride-sharing.md",
  },
  {
    slug: "video-streaming",
    title: "Video Streaming",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-video-streaming.md",
  },
  {
    slug: "brokerage-platform",
    title: "Brokerage Platform",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-brokerage-platform.md",
  },
  {
    slug: "collaborative-doc-editor",
    title: "Collaborative Doc Editor",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-collaborative-doc-editor.md",
  },
  {
    slug: "distributed-cache",
    title: "Distributed Cache",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-distributed-cache.md",
  },
  {
    slug: "payment-system",
    title: "Payment System",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-payment-system.md",
  },
  {
    slug: "web-crawler",
    title: "Web Crawler",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-web-crawler.md",
  },
  {
    slug: "job-scheduler",
    title: "Job Scheduler",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-job-scheduler.md",
  },
  {
    slug: "metrics-monitoring",
    title: "Metrics Monitoring",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-metrics-monitoring.md",
  },
  {
    slug: "document-qa-rag",
    title: "Document Q&A (RAG)",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-document-qa-rag.md",
  },
  {
    slug: "multi-tenant-chat-assistant",
    title: "Multi-Tenant Chat Assistant",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-multi-tenant-chat-assistant.md",
  },
  {
    slug: "ai-coding-copilot",
    title: "AI Coding Copilot",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-ai-coding-copilot.md",
  },
  {
    slug: "agentic-workflow-orchestrator",
    title: "Agentic Workflow Orchestrator",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-agentic-workflow-orchestrator.md",
  },
  {
    slug: "llm-eval-benchmark-platform",
    title: "LLM Evaluation & Benchmark Platform",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-llm-eval-benchmark-platform.md",
  },
  {
    slug: "semantic-retrieval-platform",
    title: "Semantic Retrieval Platform",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-semantic-retrieval-platform.md",
  },
  {
    slug: "llm-inference-serving-engine",
    title: "LLM Inference Serving Engine",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-llm-inference-serving-engine.md",
  },
  {
    slug: "multi-tenant-enterprise-rag",
    title: "Multi-Tenant Enterprise RAG",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-multi-tenant-enterprise-rag.md",
  },
  {
    slug: "ai-search-engine",
    title: "AI Search Engine",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-ai-search-engine.md",
  },
  {
    slug: "fine-tuning-pipeline",
    title: "LoRA Fine-Tuning Pipeline",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-fine-tuning-pipeline.md",
  },
  {
    slug: "inference-serving-platform",
    title: "LLM Inference Serving Platform",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-inference-serving-platform.md",
  },
  {
    slug: "recommendation-feature-store",
    title: "Recommendation Feature Store",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-recommendation-feature-store.md",
  },
  {
    slug: "text-to-sql-assistant",
    title: "Text-to-SQL Analytics Assistant",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-text-to-sql-assistant.md",
  },
  {
    slug: "voice-assistant",
    title: "Real-Time Voice Assistant",
    type: "genai-hld",
    difficulty: "advanced",
    solutionPath: "solutions/genai-hld-voice-assistant.md",
  },
  {
    slug: "ad-click-aggregator",
    title: "Ad Click Aggregator",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-ad-click-aggregator.md",
  },
  {
    slug: "bot-detection-platform",
    title: "Bot Detection Platform",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-bot-detection-platform.md",
  },
  {
    slug: "bot-detection",
    title: "Bot Detection",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-bot-detection.md",
  },
  {
    slug: "content-moderation-platform",
    title: "Content Moderation Platform",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-content-moderation-platform.md",
  },
  {
    slug: "content-moderation",
    title: "Content Moderation",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-content-moderation.md",
  },
  {
    slug: "news-feed",
    title: "News Feed",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-news-feed.md",
  },
  {
    slug: "quick-commerce-delivery",
    title: "Quick Commerce Delivery",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-quick-commerce-delivery.md",
  },
  {
    slug: "realtime-metrics-platform",
    title: "Realtime Metrics Platform",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-realtime-metrics-platform.md",
  },
  {
    slug: "ticketing-platform",
    title: "Ticketing Platform",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-ticketing-platform.md",
  },
  {
    slug: "video-recommendations",
    title: "Video Recommendations",
    type: "hld",
    difficulty: "advanced",
    solutionPath: "solutions/hld-video-recommendations.md",
  },
  {
    slug: "ad-click-aggregator",
    title: "Ad Click Aggregator",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-ad-click-aggregator.md",
  },
  {
    slug: "amazon-locker",
    title: "Amazon Locker",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-amazon-locker.md",
  },
  {
    slug: "atm-system",
    title: "Atm System",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-atm-system.md",
  },
  {
    slug: "car-rental",
    title: "Car Rental",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-car-rental.md",
  },
  {
    slug: "chess-game",
    title: "Chess Game",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-chess-game.md",
  },
  {
    slug: "connect-four",
    title: "Connect Four",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-connect-four.md",
  },
  {
    slug: "deck-of-cards",
    title: "Deck Of Cards",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-deck-of-cards.md",
  },
  {
    slug: "distributed-counter",
    title: "Distributed Counter",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-distributed-counter.md",
  },
  {
    slug: "dynamic-config-service",
    title: "Dynamic Config Service",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-dynamic-config-service.md",
  },
  {
    slug: "elevator-system",
    title: "Elevator System",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-elevator-system.md",
  },
  {
    slug: "file-system",
    title: "File System",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-file-system.md",
  },
  {
    slug: "finite-state-machine",
    title: "Finite State Machine",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-finite-state-machine.md",
  },
  {
    slug: "hotel-management-system",
    title: "Hotel Management System",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-hotel-management-system.md",
  },
  {
    slug: "hotel-reservation",
    title: "Hotel Reservation",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-hotel-reservation.md",
  },
  {
    slug: "instagram-core",
    title: "Instagram Core",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-instagram-core.md",
  },
  {
    slug: "inventory-management",
    title: "Inventory Management",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-inventory-management.md",
  },
  {
    slug: "job-scheduler",
    title: "Job Scheduler",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-job-scheduler.md",
  },
  {
    slug: "key-value-store-lsm",
    title: "Key Value Store Lsm",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-key-value-store-lsm.md",
  },
  {
    slug: "library-management",
    title: "Library Management",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-library-management.md",
  },
  {
    slug: "linkedin-connection",
    title: "Linkedin Connection",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-linkedin-connection.md",
  },
  {
    slug: "live-comments",
    title: "Live Comments",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-live-comments.md",
  },
  {
    slug: "logging-framework",
    title: "Logging Framework",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-logging-framework.md",
  },
  {
    slug: "lru-cache",
    title: "Lru Cache",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-lru-cache.md",
  },
  {
    slug: "meeting-room-scheduler",
    title: "Meeting Room Scheduler",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-meeting-room-scheduler.md",
  },
  {
    slug: "message-queue",
    title: "Message Queue",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-message-queue.md",
  },
  {
    slug: "movie-ticket-booking",
    title: "Movie Ticket Booking",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-movie-ticket-booking.md",
  },
  {
    slug: "multi-policy-cache",
    title: "Multi Policy Cache",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-multi-policy-cache.md",
  },
  {
    slug: "notification-service",
    title: "Notification Service",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-notification-service.md",
  },
  {
    slug: "online-auction",
    title: "Online Auction",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-online-auction.md",
  },
  {
    slug: "online-code-judge",
    title: "Online Code Judge",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-online-code-judge.md",
  },
  {
    slug: "online-shopping-cart",
    title: "Online Shopping Cart",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-online-shopping-cart.md",
  },
  {
    slug: "payment-gateway-router",
    title: "Payment Gateway Router",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-payment-gateway-router.md",
  },
  {
    slug: "payment-system",
    title: "Payment System",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-payment-system.md",
  },
  {
    slug: "price-tracking-service",
    title: "Price Tracking Service",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-price-tracking-service.md",
  },
  {
    slug: "rate-limiter",
    title: "Rate Limiter",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-rate-limiter.md",
  },
  {
    slug: "restaurant-management",
    title: "Restaurant Management",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-restaurant-management.md",
  },
  {
    slug: "ride-sharing-system",
    title: "Ride Sharing System",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-ride-sharing-system.md",
  },
  {
    slug: "rideshare-matching-engine",
    title: "Rideshare Matching Engine",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-rideshare-matching-engine.md",
  },
  {
    slug: "snake-and-ladder",
    title: "Snake And Ladder",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-snake-and-ladder.md",
  },
  {
    slug: "social-post-search",
    title: "Social Post Search",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-social-post-search.md",
  },
  {
    slug: "splitwise",
    title: "Splitwise",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-splitwise.md",
  },
  {
    slug: "stack-overflow",
    title: "Stack Overflow",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-stack-overflow.md",
  },
  {
    slug: "task-planner",
    title: "Task Planner",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-task-planner.md",
  },
  {
    slug: "text-editor",
    title: "Text Editor",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-text-editor.md",
  },
  {
    slug: "tic-tac-toe",
    title: "Tic Tac Toe",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-tic-tac-toe.md",
  },
  {
    slug: "unix-vfs",
    title: "Unix Vfs",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-unix-vfs.md",
  },
  {
    slug: "vending-machine",
    title: "Vending Machine",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-vending-machine.md",
  },
  {
    slug: "web-crawler",
    title: "Web Crawler",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-web-crawler.md",
  },
  {
    slug: "webhook-dispatcher",
    title: "Webhook Dispatcher",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-webhook-dispatcher.md",
  },
  {
    slug: "youtube-top-k",
    title: "Youtube Top K",
    type: "lld",
    difficulty: "advanced",
    solutionPath: "solutions/lld-youtube-top-k.md",
  },
];
