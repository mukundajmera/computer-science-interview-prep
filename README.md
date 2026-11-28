# 🎯 System Design Interview Prep Guide

> **One repository for mastering LLD, HLD, Design Patterns in Java & Python**

[![GitHub stars](https://img.shields.io/github/stars/mukundajmera/computer-science-interview-prep?style=social)](https://github.com/mukundajmera/computer-science-interview-prep)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Java](https://img.shields.io/badge/Java-11%2B-orange)](https://openjdk.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)

A comprehensive, structured approach to mastering system design interviews. From foundational concepts to complex distributed systems - everything you need in one place.

---

## 📑 Table of Contents

- [🚀 Quick Start](#-quick-start)
- [📦 What's Inside](#-whats-inside)
- [📂 Repository Structure](#-repository-structure)
- [📅 Study Plans](#-study-plans)
- [✅ Progress Tracker](#-progress-tracker)
- [📖 How to Use](#-how-to-use-this-repository)
- [💻 Languages](#-languages)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## 🚀 Quick Start

**New to the repo?** Start here:

1. 📖 Read [QUICK-START.md](./QUICK-START.md) for learning paths
2. 📅 Choose a [study plan](./resources/study-plans/) based on your timeline
3. 📚 Begin with [00-theory](./00-theory/) for fundamentals
4. ⚡ Review [Concurrency in LLD](./00-theory/system-design-fundamentals/concurrency-in-lld.md) before advanced LLD rounds
5. 🔧 Practice with [LLD projects](./02-lld-projects/)
6. 🌐 Master [HLD concepts](./03-hld-concepts/) and [projects](./04-hld-projects/)

**Interview in 1 week?** Follow the [1-week crash course](./resources/study-plans/1-week-plan.md)

**Need a quick reference?** Check [CONCEPTS.md](./CONCEPTS.md)

---

## 📦 What's Inside

| Section | Content | Coverage | Status |
|---------|---------|----------|--------|
| [00-theory](./00-theory/) | Core CS concepts (OOP, DB, Networks) | Fundamentals library | Active |
| [01-design-patterns](./01-design-patterns/) | GoF patterns with Java & Python | Full pattern catalog | 🚧 v2/v3 refresh active |
| [02-lld-projects](./02-lld-projects/) | Low-level designs | Project catalog | 🚧 coaching/test-quality refresh active |
| [03-hld-concepts](./03-hld-concepts/) | System components | Concept library | 🚧 database concept gaps active |
| [04-hld-projects](./04-hld-projects/) | HLD system designs | Doc-pack catalog | 🚧 diagram/depth refresh active |
| [05-coding-problems](./05-coding-problems/) | Algorithm patterns | Active pattern packs | 🚧 In Progress |
| [06-genai-systems](./06-genai-systems/) | GenAI/LLM system design | Concepts plus LLD/HLD tracks | 🚧 active |
| [case-studies](./case-studies/) | Real company architectures | Architecture deep dives | 🚧 GenAI-era research active |
| [resources](./resources/) | Study aids, cheatsheets, tips | Supporting materials | 🚧 assessment mapping active |

---

## 📂 Repository Structure

```
system-design-interview-prep/
├── 📚 00-theory/              # Fundamentals (OOP, DB, Networks, Complexity)
│   ├── oop-principles/        # SOLID, DRY, KISS, Composition
│   ├── database-concepts/     # SQL, NoSQL, Indexing, Transactions
│   ├── networking-basics/     # HTTP, TCP/IP, REST, gRPC
│   ├── complexity-analysis/   # Big-O notation, Space/Time
│   └── system-design-fundamentals/
│
├── 🎨 01-design-patterns/     # 23 GoF Patterns (Java + Python)
│   ├── creational/            # Singleton, Factory, Builder, Prototype, Abstract Factory
│   ├── structural/            # Adapter, Bridge, Composite, Decorator, Facade, Flyweight, Proxy
│   └── behavioral/            # Strategy, Observer, Command, State, Template, Chain, Iterator, Mediator, Memento, Visitor, Interpreter
│
├── 🏗️ 02-lld-projects/        # Real-world LLD Projects
│   ├── parking-lot/
│   ├── elevator-system/
│   ├── library-management/
│   ├── chess-game/
│   ├── hotel-reservation/
│   └── ... additional projects
│
├── ⚙️ 03-hld-concepts/         # System Design Building Blocks
│   └── (Load Balancing, Caching, Sharding, Queues, etc.)
│
├── 🌐 04-hld-projects/         # HLD System Designs
│   └── (URL Shortener, Twitter, WhatsApp, YouTube, Uber, etc.)
│
├── 🧩 05-coding-problems/      # Algorithm Patterns (Two Pointers, Sliding Window, Binary Search, BFS/DFS, DP, Greedy, Backtracking, Heap, Trie, Union-Find)
│
├── 🤖 06-genai-systems/        # Generative AI / LLM System Design
│   ├── 00-concepts/            # RAG, vector DBs, safety, evaluation
│   ├── 01-llm-lld-projects/    # GenAI component LLD exercises
│   └── 02-llm-hld-projects/    # Full GenAI system designs
│
├── 📊 case-studies/            # 12 Real Company Case Studies
│   ├── twitter-timeline/       # Twitter feed architecture
│   ├── netflix-streaming/      # Netflix CDN and streaming
│   ├── uber-realtime/          # Uber real-time matching
│   ├── whatsapp-messaging/     # WhatsApp messaging at scale
│   ├── instagram-feed/         # Instagram photo feed
│   ├── airbnb-search/          # Airbnb search & booking
│   ├── spotify-streaming/      # Spotify music streaming
│   ├── amazon-orders/          # Amazon order processing
│   ├── youtube-video/          # YouTube video platform
│   ├── linkedin-feed/          # LinkedIn professional feed
│   ├── chatgpt-inference/      # ChatGPT enterprise assistant and agents
│   └── github-copilot/         # Copilot code assist and coding agents
│
└── 📖 resources/               # Study Materials
    ├── study-plans/           # 1-week, 1-month, topic-based plans
    ├── cheatsheets/           # Quick reference guides
    ├── interview-tips/        # LLD/HLD/behavioral/salary-negotiation checklists and playbooks
    └── templates/             # Practice templates (LLD/HLD/behavioral/salary-negotiation)
```


---

## 📅 Study Plans

Choose a plan based on your timeline:

| Plan | Duration | Best For | Link |
|------|----------|----------|------|
| 🚨 **1-Week Crash Course** | 7 days | Interview coming up soon | [1-week-plan.md](./resources/study-plans/1-week-plan.md) |
| 📚 **1-Month Deep Dive** | 4 weeks | Comprehensive preparation | [1-month-plan.md](./resources/study-plans/1-month-plan.md) |
| 🎯 **Topic-Based** | Flexible | Filling specific gaps | [topic-based-plan.md](./resources/study-plans/topic-based-plan.md) |

---

## ✅ Progress Tracker

Track your preparation by checking off completed items:

### Design Patterns (23)
**Creational (5)**
- [ ] Singleton
- [ ] Factory Method
- [ ] Abstract Factory
- [ ] Builder
- [ ] Prototype

**Structural (7)**
- [ ] Adapter
- [ ] Bridge
- [ ] Composite
- [ ] Decorator
- [ ] Facade
- [ ] Flyweight
- [ ] Proxy

**Behavioral (11)**
- [ ] Chain of Responsibility
- [ ] Command
- [ ] Interpreter
- [ ] Iterator
- [ ] Mediator
- [ ] Memento
- [ ] Observer
- [ ] State
- [ ] Strategy
- [ ] Template Method
- [ ] Visitor

### LLD Projects (61)
**Beginner**
- [ ] Parking Lot
- [ ] Tic-Tac-Toe
- [ ] Connect Four
- [ ] Vending Machine
- [ ] Snake & Ladder
- [ ] LRU Cache

**Intermediate**
- [ ] Library Management
- [ ] Amazon Locker
- [ ] Elevator System
- [ ] ATM System
- [ ] Hotel Reservation
- [ ] Movie Ticket Booking
- [ ] Inventory Management
- [ ] Online Shopping Cart
- [ ] Restaurant Management

**Advanced**
- [ ] Chess Game
- [ ] Splitwise
- [ ] Rate Limiter
- [ ] Ride Sharing
- [ ] File System
- [ ] LinkedIn Connection
- [ ] Stack Overflow
- [ ] Car Rental

**Additional**
- [ ] Instagram Core
- [ ] Live Comments
- [ ] Online Auction
- [ ] Price Tracking Service
- [ ] Social Post Search
- [ ] YouTube Top-K
- [ ] Job Scheduler
- [ ] Web Crawler
- [ ] Ad Click Aggregator
- [ ] Payment System

### HLD Concepts
**Infrastructure**
- [ ] Load Balancing
- [ ] Caching
- [ ] CDN
- [ ] Large Blob Handling
- [ ] DNS
- [ ] API Gateway
- [ ] Rate Limiting

**Data**
- [ ] Database Sharding
- [ ] Database Replication
- [ ] Read Scaling
- [ ] Write Scaling
- [ ] Large Blob Handling
- [ ] Consistent Hashing
- [ ] Relational Databases (PostgreSQL)
- [ ] NoSQL Databases (Cassandra, DynamoDB)
- [ ] Redis
- [ ] Time-Series Databases

**Communication**
- [ ] Message Queues
- [ ] API Design
- [ ] Microservices Communication
- [ ] Stream Processing
- [ ] Search Systems

**Coordination & Observability**
- [ ] Distributed Coordination (ZooKeeper)
- [ ] Service Discovery
- [ ] Monitoring & Observability
- [ ] Long-Running Tasks

### HLD Systems
- [ ] URL Shortener (TinyURL)
- [ ] News Feed (Twitter/Facebook)
- [ ] File Storage (Dropbox)
- [ ] Chat Service (WhatsApp)
- [ ] Video Streaming (YouTube/Netflix)
- [ ] Ride Sharing (Uber)
- [ ] Notification Service
- [ ] E-commerce (Amazon)
- [ ] Ticketing Platform
- [ ] Quick Commerce Delivery
- [ ] Realtime Metrics Platform
- [ ] Brokerage Platform
- [ ] Collaborative Doc Editor
- [ ] Distributed Cache
- [ ] Online Auction
- [ ] Live Comments
- [ ] Social Post Search
- [ ] Price Tracking Service
- [ ] Job Scheduler
- [ ] Web Crawler
- [ ] Ad Click Aggregator
- [ ] Payment System
- [ ] Metrics Monitoring (Baseline)
- [ ] Content Moderation Platform
- [ ] Bot Detection Platform

### GenAI Systems
**Concepts** (14)
- [x] RAG Architecture
- [x] LLM-Oriented System Design
- [x] Prompting, Tools & Agents
- [x] Safety & Governance
- [x] LLM Evaluation
- [x] Model Generalization
- [x] Safety, Evaluation & Governance (consolidated reference)
- [x] Vector Databases
- [x] Model Routing & Orchestration
- [x] Streaming & KV-Cache
- [x] Token / Cost / Latency Planning
- [x] GenAI Design Patterns

**LLD Components** (17)
- [x] Document Chunker & Metadata Indexer
- [x] Embedding Service
- [x] Retriever & Ranker
- [x] Prompt Builder
- [x] Conversation Memory Store
- [x] Tool Router
- [x] Safety Filter & Policy Engine
- [x] LLM Request Orchestrator
- [x] Evaluation Harness

**HLD Systems** (10)
- [x] [Document Q&A (RAG)](06-genai-systems/02-llm-hld-projects/document-qa-rag/)
- [x] [Multi-Tenant Chat Assistant](06-genai-systems/02-llm-hld-projects/multi-tenant-chat-assistant/)
- [x] [AI Coding Copilot](06-genai-systems/02-llm-hld-projects/ai-coding-copilot/)
- [x] [Agentic Workflow Orchestrator](06-genai-systems/02-llm-hld-projects/agentic-workflow-orchestrator/)
- [x] [LLM Evaluation & Safety Platform](06-genai-systems/02-llm-hld-projects/llm-evaluation-safety-platform/)
- [x] [LLM Safety & Eval Platform (Governance-Focused)](06-genai-systems/02-llm-hld-projects/llm-safety-eval-platform/)
- [x] [Semantic Retrieval Platform](06-genai-systems/02-llm-hld-projects/semantic-retrieval-platform/)

---

## 📖 How to Use This Repository

### 1. Learning Mode (Building Foundation)
Perfect for building a strong base from scratch:
```
00-theory/          → Understand fundamentals
      ↓
01-design-patterns/ → Learn reusable solutions
      ↓
02-lld-projects/    → Practice hands-on design
      ↓
03-hld-concepts/    → Learn distributed systems
      ↓
04-hld-projects/    → Master HLD architectures
      ↓
06-genai-systems/   → Design LLM-powered systems (GenAI track)
```

### 2. Interview Prep Mode (Time-Constrained)
Perfect for focused preparation with limited time:
- Follow [study plans](./resources/study-plans/) based on timeline
- Use [cheatsheets](./resources/cheatsheets/) for quick review
- Practice with [templates](./resources/templates/)
- Review [interview tips](./resources/interview-tips/)
- Run the [Behavioral Interviews Quiz](./quizzes/behavioral-interviews-quiz.md) after story prep
- Run the [Salary Negotiation Quiz](./quizzes/salary-negotiation-quiz.md) before offer-stage calls
- Explore [LLD Interview Q&A](./02-lld-projects/INTERVIEW-QA.md) for common follow-ups and scoring cues
- Self-test delivery with the [LLD Interview Framework Quiz](./quizzes/lld-interview-framework-quiz.md) (answers at [./quizzes/answers/lld-interview-framework-answers.md](./quizzes/answers/lld-interview-framework-answers.md))

### 3. Topic-Based Mode (Filling Gaps)
Perfect for targeting specific weak areas:
- Identify weak areas from mock interviews
- Navigate to specific topic folders
- Follow cross-references from theory to practice
- Use [CONCEPTS.md](./CONCEPTS.md) for quick lookups

---

## 💻 Languages

All implementations are provided in both **Java** and **Python**:

### Java Requirements
- Java 11+ recommended
- JUnit 5 for tests
- No external dependencies (pure Java)

```bash
# Compile and run
javac Solution.java && java Solution

# Run tests
java -jar junit-platform-console-standalone.jar --scan-classpath
```

### Python Requirements
- Python 3.8+ recommended
- Type hints throughout
- unittest/pytest for tests
- No external dependencies (standard library only)

```bash
# Run solution
python solution.py

# Run tests
pytest tests/ -v
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](.github/CONTRIBUTING.md) for:

- 📝 Adding new patterns or projects
- 📈 Improving existing content
- 🐛 Fixing errors or typos
- 🌍 Adding implementations in other languages

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⭐ Show Your Support

If this repository helps you prepare for interviews, please consider:
- ⭐ **Starring** this repository
- 📢 **Sharing** with others preparing for interviews
- 🐛 **Reporting** issues or suggesting improvements

---

## 🔗 Quick Links

| Resource | Description |
|----------|-------------|
| [📖 QUICK-START.md](./QUICK-START.md) | Getting started guide |
| [📋 CONCEPTS.md](./CONCEPTS.md) | Quick reference cheatsheet |
| [🧠 CAP Theorem](./00-theory/system-design-fundamentals/cap-theorem.md) | Distributed consistency trade-offs |
| [🧮 Back-of-Envelope](./00-theory/system-design-fundamentals/back-of-envelope.md) | Capacity estimation for interviews |
| [⚡ Concurrency in LLD](./00-theory/system-design-fundamentals/concurrency-in-lld.md) | Correctness, coordination, and scarcity in class-level design |
| [📅 Study Plans](./resources/study-plans/) | Structured learning paths |
| [💡 Interview Tips](./resources/interview-tips/) | Checklists, communication guides, and behavioral playbooks |
| [🎤 LLD Interview Q&A](./02-lld-projects/INTERVIEW-QA.md) | Reference follow-up bank for common LLD callbacks |
| [🧭 LLD Interview Framework Quiz](./quizzes/lld-interview-framework-quiz.md) | 25-question delivery checkpoint |
| [🧠 Behavioral Interviews Quiz](./quizzes/behavioral-interviews-quiz.md) | 36-question behavioral execution checkpoint |
| [💬 Salary Negotiation Quiz](./quizzes/salary-negotiation-quiz.md) | 36-question offer-stage negotiation execution checkpoint |
| [✅ LLD Interview Framework Answers](./quizzes/answers/lld-interview-framework-answers.md) | Answer key + rationale |
| [🗂️ LLD Flashcards (100 cards)](./flashcards/lld-concepts.md) | Question-only deck covering LLD fundamentals plus project drills |
| [🧠 Behavioral Flashcards (60 cards)](./flashcards/behavioral-interviews.md) | Question-only deck for behavioral loops and follow-up handling |
| [💬 Salary Negotiation Flashcards (60 cards)](./flashcards/salary-negotiation.md) | Question-only deck for offer-stage negotiation drills and adaptations |
| [🧾 Salary Negotiation Playbook](./resources/interview-tips/salary-negotiation-playbook.md) | Stakeholder map, component strategy, and Global/India negotiation flow |
| [📝 Templates](./resources/templates/) | Practice frameworks |
| [📊 Cheatsheets](./resources/cheatsheets/) | Quick reference guides |
| [🏢 Case Studies](./case-studies/) | Real company architectures |

---

<p align="center">
  <b>Happy Learning! 🎉</b><br>
  <i>Remember: Consistency beats intensity. Practice a little every day.</i>
</p>

---

## March 2026 Curriculum Upgrade

- Added source-set-driven interview tracks: Online Auction, Live Comments, Social Post Search, Price Tracking Service.
- Added six new LLD modules and upgraded News Feed + Realtime Metrics with Instagram/YouTube Top-K variants.
- Added full behavioral track: frameworks, pitfalls, special-round guides, quiz, flashcards, and interview-mode coach answers.
- Added full salary negotiation track: playbook, practice template, mock scorecard, quiz + answers, flashcards, and coach answer.
