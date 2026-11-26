# 🔗 Cross-Reference Guide

This guide provides instructions for maintaining cross-references throughout the repository to help learners connect related concepts.

---

## 📋 Cross-Reference Philosophy

Cross-references help learners:
- **Connect theory to practice** - See how concepts apply in real projects
- **Navigate efficiently** - Find related content without searching
- **Build mental models** - Understand relationships between topics
- **Reinforce learning** - Review related concepts together

---

## 🎨 Design Patterns Cross-References

### Adding References to Pattern Files

Each pattern README should include a "Related Content" section:

```markdown
## 🔗 Related Content

### Theory Foundation
- [SOLID Principles](../../00-theory/oop-principles/solid-principles.md) - Open/Closed Principle
- [Composition vs Inheritance](../../00-theory/oop-principles/composition-inheritance.md)

### Used In LLD Projects
- [Parking Lot](../../02-lld-projects/parking-lot/) - Vehicle type selection
- [Chess Game](../../02-lld-projects/chess-game/) - Piece movement strategies

### Related Patterns
- [State Pattern](../behavioral/state/) - Often confused with Strategy
- [Factory Pattern](../creational/factory/) - Often used together

### Used In HLD Concepts
- [Caching Strategies](../../03-hld-concepts/) - Cache eviction algorithms
```

### Pattern-to-Project Mapping

| Pattern | Update With These LLD Projects | Update With These HLD Concepts |
|---------|-------------------------------|-------------------------------|
| Singleton | Database connections, Logger | Connection pooling |
| Factory | Parking Lot (vehicles), Library (books) | Service instantiation |
| Strategy | Parking Lot (pricing), Chess (moves) | Load balancing algorithms |
| Observer | Elevator (buttons), Library (notifications) | Event-driven systems, Pub/Sub |
| State | Elevator, Vending Machine | Connection states |
| Command | Chess (undo), Text Editor | Command queues, Task scheduling |
| Decorator | Coffee Shop, Pizza ordering | Middleware, Filters |
| Adapter | Payment integrations | API adapters, Protocol conversion |
| Proxy | Cache implementation | Caching proxy, Load balancer |

---

## 🏗️ LLD Projects Cross-References

### Adding References to Project Files

Each LLD project README should include cross-references:

```markdown
## 🔗 Related Content

### Patterns Used
| Pattern | How It's Used | Link |
|---------|---------------|------|
| Factory | Creating vehicle objects | [→](../../01-design-patterns/creational/factory/) |
| Strategy | Pricing strategies | [→](../../01-design-patterns/behavioral/strategy/) |
| Singleton | ParkingLot instance | [→](../../01-design-patterns/creational/singleton/) |

### Concepts Covered
- [OOP Principles](../../00-theory/oop-principles/) - SOLID, inheritance
- [Complexity Analysis](../../00-theory/complexity-analysis/) - Time/space analysis

### Similar Projects
| Project | Similarity | Link |
|---------|------------|------|
| Library Management | Resource management | [→](../library-management/) |
| Hotel Reservation | Booking system | [→](../hotel-reservation/) |

### Related HLD Systems
- [Ride Sharing](../../04-hld-projects/) - Similar vehicle/spot matching
```

### Project-to-Pattern Mapping

| LLD Project | Primary Patterns | Add Cross-Reference To |
|-------------|-----------------|----------------------|
| Parking Lot | Factory, Strategy, Singleton | These pattern files |
| Elevator System | State, Observer, Strategy | These pattern files |
| Library Management | Factory, Observer | These pattern files |
| Chess Game | Strategy, Command | These pattern files |
| Vending Machine | State, Strategy | These pattern files |
| LRU Cache | - | Proxy pattern, Caching concept |
| Rate Limiter | Strategy | Rate Limiting HLD concept |
| Splitwise | Strategy, Observer | Graph algorithms |

---

## ⚙️ HLD Concepts Cross-References

### Adding References to Concept Files

Each HLD concept README should include:

```markdown
## 🔗 Related Content

### Theory Foundation
- [Database Concepts](../../00-theory/database-concepts/) - Query optimization
- [Networking Basics](../../00-theory/networking-basics/) - HTTP, TCP

### Related Patterns
- [Proxy Pattern](../../01-design-patterns/structural/proxy/) - Caching proxy
- [Flyweight Pattern](../../01-design-patterns/structural/flyweight/) - Object caching

### Used In These Systems
| System | How Caching Is Used | Link |
|--------|---------------------|------|
| Twitter Feed | Timeline caching | [→](../../04-hld-projects/) |
| URL Shortener | URL lookup caching | [→](../../04-hld-projects/) |

### Related Concepts
- [Load Balancing](../load-balancing/) - Often used together
- [CDN](../cdn/) - Edge caching
- [Database Replication](../replication/) - Read replicas + cache
```

### Concept-to-System Mapping

| HLD Concept | Add References to These Systems |
|-------------|--------------------------------|
| Caching | All systems (esp. Twitter, URL Shortener) |
| Load Balancing | All systems |
| Sharding | Twitter, Chat, Video Streaming |
| Message Queues | Twitter (fan-out), Notification, Video |
| CDN | YouTube, Instagram, Netflix |
| Rate Limiting | API Gateway, URL Shortener |
| WebSockets | Chat, Real-time notifications |
| Consistent Hashing | Distributed cache, Sharding |

---

## 🌐 HLD Projects Cross-References

### Adding References to Project Files

Each HLD project should reference:

```markdown
## 🔗 Related Content

### Concepts Used
| Concept | Application in This System | Link |
|---------|---------------------------|------|
| Caching | User timeline caching | [→](../../03-hld-concepts/) |
| Message Queues | Fan-out to followers | [→](../../03-hld-concepts/) |
| Sharding | User data partitioning | [→](../../03-hld-concepts/) |

### Related LLD Projects
- [Rate Limiter](../../02-lld-projects/rate-limiter/) - API protection implementation

### Similar Systems
| System | Key Similarity | Link |
|--------|---------------|------|
| Instagram | Feed generation | [→](../instagram/) |
| Facebook | News feed | [→](../facebook/) |

### Related Patterns
- [Observer Pattern](../../01-design-patterns/behavioral/observer/) - Notification system
- [Strategy Pattern](../../01-design-patterns/behavioral/strategy/) - Feed ranking
```

---

## 📚 Theory Files Cross-References

### Adding References to Theory Files

Each theory file should link to practical applications:

```markdown
## 🔗 Related Content

### Applied in Patterns
- [Strategy Pattern](../../01-design-patterns/behavioral/strategy/) - Open/Closed Principle
- [Factory Pattern](../../01-design-patterns/creational/factory/) - Dependency Inversion

### Demonstrated in Projects
| Project | Principle Applied | Link |
|---------|------------------|------|
| Parking Lot | Single Responsibility | [→](../../02-lld-projects/parking-lot/) |
| Chess Game | Open/Closed (new pieces) | [→](../../02-lld-projects/chess-game/) |

### See Also
- [Composition vs Inheritance](./composition-inheritance.md)
- [Design Patterns Overview](../../01-design-patterns/)
```

---

## 🧭 Interview Readiness Cross-References

Leverage the new LLD delivery artifacts to close the loop between theory, project walk-throughs, and assessment prep. Add these links whenever updating README tables, study plans, or interview tips.

### Assets to Reference
- `[LLD Interview Q&A](../02-lld-projects/INTERVIEW-QA.md)` — include in any README or theory file that sums up LLD troubleshooting, follow-up responses, or interview habits. This document doubles as a micro-case FAQ.
- `[LLD Interview Framework Quiz](../quizzes/lld-interview-framework-quiz.md)` — link from `quizzes/README.md`, `02-lld-projects/README.md`, and any study plan that enumerates assessment tools so the framework quiz is easy to discover.
- `[LLD Interview Framework Answers](../quizzes/answers/lld-interview-framework-answers.md)` — reference wherever the quiz appears, especially in Quick Links, so learners can check explanations immediately.
- `[LLD Concepts Flashcards (100)](../flashcards/lld-concepts.md)` — mention in OOP resources, flashcard overviews, and README quick-links to keep the card count accurate while spotlighting the new delivery cards.

### Cross-Link Tips
- When you update `READMEs` or `study plans` for LLD projects, add a “Resources” subsection that points at the QA, quiz, answers, and flashcards to reinforce the interview delivery path.
- Use the phrase “LLD Interview framework” consistently across link labels so learners can easily search for and recognize the new assets.
- Keep relative links short (see `## 🔧 Link Format Standards` for reference). Example from `02-lld-projects/README.md`:

```markdown
[LLD Interview Q&A](./INTERVIEW-QA.md)
[LLD Interview Framework Quiz](../quizzes/lld-interview-framework-quiz.md)
[LLD Interview Framework Answers](../quizzes/answers/lld-interview-framework-answers.md)
```

---

## 🤖 GenAI Systems Cross-References

> **Note:** The path examples below are templates. Use them when creating or editing files **within** the specified GenAI directories — the relative paths are written from the target file's perspective, not from this guide's location.

### Adding References to GenAI Concept Files

Each GenAI concept should link to both classical and GenAI-specific content:

```markdown
## 🔗 Related Content

### Classical Foundations
| Concept | Relationship | Link |
|---------|-------------|------|
| Caching | Semantic caching for LLM responses | [→](../../../03-hld-concepts/caching/) |
| Rate Limiting | Token-based rate limiting | [→](../../../03-hld-concepts/rate-limiting/) |

### Applied in GenAI Systems
| System | How It's Used | Link |
|--------|---------------|------|
| Document Q&A (RAG) | Core retrieval pipeline | [→](../../02-llm-hld-projects/document-qa-rag/) |
| AI Coding Copilot | Context retrieval | [→](../../02-llm-hld-projects/ai-coding-copilot/) |

### Related GenAI Concepts
- [Safety & Governance](../safety-governance/) - Guardrails for retrieved content
- [LLM Evaluation](../llm-evaluation/) - Measuring retrieval quality
```

### Adding References to GenAI LLD Projects

Each GenAI LLD project should link to the concepts it implements:

```markdown
## 🔗 Related Content

### Implements Concepts
- [RAG Architecture](../../00-concepts/rag-architecture/) - This component is part of the RAG pipeline

### Used In Systems
| System | Role | Link |
|--------|------|------|
| Document Q&A (RAG) | Document ingestion | [→](../../02-llm-hld-projects/document-qa-rag/) |

### Classical Parallels
- [LRU Cache](../../../02-lld-projects/lru-cache/) - Similar eviction pattern
```

### Adding References to GenAI HLD Projects

Each GenAI HLD project should link to all layers:

```markdown
## 🔗 Related Content

### GenAI Concepts Used
| Concept | Application | Link |
|---------|-------------|------|
| RAG Architecture | Document retrieval pipeline | [→](../../00-concepts/rag-architecture/) |
| Safety & Governance | Input/output filtering | [→](../../00-concepts/safety-governance/) |

### GenAI Components Used
| Component | Role | Link |
|-----------|------|------|
| Chunker & Metadata Indexer | Content ingestion | [→](../../01-llm-lld-projects/chunker-metadata-indexer/) |
| Retriever & Ranker | Search and ranking | [→](../../01-llm-lld-projects/retriever-ranker/) |

### Classical Concepts Used
| Concept | Application | Link |
|---------|-------------|------|
| Caching | Response caching, KV-cache | [→](../../../03-hld-concepts/caching/) |
| Message Queues | Async inference pipeline | [→](../../../03-hld-concepts/message-queues/) |

### Related Classical Systems
- [Chat Service](../../../04-hld-projects/chat-service/) - Similar real-time architecture
```

### GenAI Concept-to-Classical Mapping

| GenAI Concept | Classical Concept(s) | Link Direction |
|---------------|---------------------|----------------|
| RAG Architecture | Caching, CDN, Database Replication | GenAI ↔ Classical |
| LLM Safety | Rate Limiting, API Gateway | GenAI → Classical |
| LLM Evaluation | Monitoring & Observability | GenAI → Classical |
| Model Routing | Load Balancing, Service Discovery | GenAI ↔ Classical |
| Token Budgeting | Rate Limiting | GenAI → Classical |
| Semantic Caching | Caching | GenAI ↔ Classical |

---

## Cross-Reference Checklist

Use this checklist when adding new content:

### When Adding a New Pattern
- [ ] Link to related theory (SOLID, OOP concepts)
- [ ] Link to LLD projects using this pattern
- [ ] Link to similar/related patterns
- [ ] Link to HLD concepts where applicable
- [ ] Update LLD projects to reference this pattern

### When Adding a New LLD Project
- [ ] Link to all patterns used
- [ ] Link to relevant theory concepts
- [ ] Link to similar difficulty projects
- [ ] Link to related HLD systems
- [ ] Update pattern files to reference this project

### When Adding a New HLD Concept
- [ ] Link to foundational theory
- [ ] Link to related patterns (if any)
- [ ] Link to HLD systems using this concept
- [ ] Link to related concepts
- [ ] Update HLD projects to reference this concept

### When Adding a New HLD Project
- [ ] Link to all concepts used
- [ ] Link to related LLD projects
- [ ] Link to similar systems
- [ ] Link to relevant patterns
- [ ] Update concept files to reference this system

### When Adding a New GenAI Concept
- [ ] Link to classical HLD concepts that it extends or parallels
- [ ] Link to GenAI HLD projects that use this concept
- [ ] Link to related GenAI concepts
- [ ] Update `06-genai-systems/README.md` progress tracker
- [ ] Update root `CONCEPTS.md` if applicable

### When Adding a New GenAI LLD Project
- [ ] Link to GenAI concepts the component implements
- [ ] Link to GenAI HLD systems that use this component
- [ ] Link to classical LLD parallels (if any)
- [ ] Update `06-genai-systems/README.md` progress tracker

### When Adding a New GenAI HLD Project
- [ ] Link to all GenAI concepts used
- [ ] Link to GenAI LLD components used
- [ ] Link to classical HLD concepts used
- [ ] Link to similar classical or GenAI systems
- [ ] Update `06-genai-systems/README.md` progress tracker
- [ ] Update root `README.md` progress tracker

---

## 🔧 Link Format Standards

### Relative Links
Always use relative links from the current file location:

```markdown
<!-- From 01-design-patterns/behavioral/strategy/README.md -->
[Parking Lot](../../../02-lld-projects/parking-lot/)
[SOLID Principles](../../../00-theory/oop-principles/solid-principles.md)
```

### Link Tables
Use tables for multiple related items:

```markdown
| Resource | Relationship | Link |
|----------|--------------|------|
| Factory Pattern | Often used together | [→](../creational/factory/) |
| State Pattern | Often confused with | [→](../behavioral/state/) |
```

### Inline Links
For single references within text:

```markdown
This pattern is commonly used in [Parking Lot](../../02-lld-projects/parking-lot/)
for implementing different pricing strategies.
```

---

<p align="center">
  <b>Keep cross-references updated as content grows! 🔗</b>
</p>
