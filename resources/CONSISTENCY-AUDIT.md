# 📋 Consistency Audit Checklist

Use this checklist for manual review to ensure consistency across the repository.

---

## 🔍 How to Use This Checklist

1. **Periodic Review**: Run through this checklist monthly or after major additions
2. **Before Release**: Complete all checks before tagging a new version
3. **Contributor Check**: Use relevant sections when reviewing PRs

---

## 💻 Code Consistency

### Java Code Standards

- [ ] All Java class files use `PascalCase` naming (e.g., `ParkingLot.java`)
- [ ] All Java methods use `camelCase` naming
- [ ] All constants use `UPPER_SNAKE_CASE`
- [ ] All classes have appropriate Javadoc comments
- [ ] Private fields are used with getters/setters where needed
- [ ] `final` keyword used for immutable fields
- [ ] Constructor injection used for dependencies
- [ ] Time/space complexity documented for main methods
- [ ] Consistent indentation (4 spaces)
- [ ] Consistent brace style (same line)

### Python Code Standards

- [ ] All Python files use `snake_case` naming (e.g., `parking_lot.py`)
- [ ] All classes use `PascalCase` naming
- [ ] All functions/methods use `snake_case`
- [ ] All constants use `UPPER_SNAKE_CASE`
- [ ] Type hints used throughout
- [ ] Docstrings for all public classes and methods
- [ ] Private members prefixed with `_`
- [ ] Consistent indentation (4 spaces)
- [ ] Imports organized (standard lib, third-party, local)

### General Code Quality

- [ ] Comments explain "why", not "what"
- [ ] No commented-out code left in files
- [ ] Consistent error handling approach
- [ ] Edge cases explicitly handled
- [ ] No magic numbers (use named constants)

---

## 📖 Documentation Consistency

### README Files

- [ ] Every folder has a README.md
- [ ] All READMEs follow the same structure within their category
- [ ] Emoji usage is consistent (📚 Theory, 🏗️ Implementation, etc.)
- [ ] All READMEs have a Table of Contents for long files
- [ ] Cross-references use relative paths
- [ ] No broken internal links

### Design Pattern READMEs

All pattern files should have:
- [ ] Theory section (Problem & Motivation)
- [ ] Structure/UML diagram
- [ ] Java implementation
- [ ] Python implementation
- [ ] "When to Use" section
- [ ] "Trade-offs" section (Pros/Cons)
- [ ] Related patterns section
- [ ] Interview Q&A section

### LLD Project READMEs

All LLD projects should have:
- [ ] Problem Statement section
- [ ] Requirements (Functional + Non-functional)
- [ ] Approach section
- [ ] Solution (v1, v2, v3 versions)
- [ ] Java code
- [ ] Python code
- [ ] Edge Cases section
- [ ] Follow-up Questions section

### HLD Concept READMEs

All HLD concepts should have:
- [ ] What is it? section
- [ ] Why do we need it? section
- [ ] How does it work? section
- [ ] When to use section
- [ ] Trade-offs section
- [ ] Technologies section
- [ ] Interview Q&A section

### HLD Project READMEs

All HLD projects should have:
- [ ] Problem Statement section
- [ ] Requirements (Functional + Non-functional)
- [ ] Capacity Estimation section
- [ ] API Design section
- [ ] Data Model section
- [ ] High-Level Architecture (with diagram)
- [ ] Deep Dives section
- [ ] Trade-offs section
- [ ] Follow-up Questions section

---

## 📊 Content Completeness

### Design Patterns (23 total)

#### Creational (5)
- [ ] Singleton - has all 3 versions
- [ ] Factory Method - has all 3 versions
- [ ] Abstract Factory - has all 3 versions
- [ ] Builder - has all 3 versions
- [ ] Prototype - has all 3 versions

#### Structural (7)
- [ ] Adapter - has all 3 versions
- [ ] Bridge - has all 3 versions
- [ ] Composite - has all 3 versions
- [ ] Decorator - has all 3 versions
- [ ] Facade - has all 3 versions
- [ ] Flyweight - has all 3 versions
- [ ] Proxy - has all 3 versions

#### Behavioral (11)
- [ ] Chain of Responsibility - has all 3 versions
- [ ] Command - has all 3 versions
- [ ] Interpreter - has all 3 versions
- [ ] Iterator - has all 3 versions
- [ ] Mediator - has all 3 versions
- [ ] Memento - has all 3 versions
- [ ] Observer - has all 3 versions
- [ ] State - has all 3 versions
- [ ] Strategy - has all 3 versions
- [ ] Template Method - has all 3 versions
- [ ] Visitor - has all 3 versions

### LLD Projects (20 total)

- [ ] Parking Lot - complete with tests
- [ ] LRU Cache - complete with tests
- [ ] Elevator System - complete with tests
- [ ] Library Management - complete with tests
- [ ] Vending Machine - complete with tests
- [ ] ATM System - complete with tests
- [ ] Chess Game - complete with tests
- [ ] Hotel Reservation - complete with tests
- [ ] Movie Ticket Booking - complete with tests
- [ ] Snake & Ladder - complete with tests
- [ ] Tic-Tac-Toe - complete with tests
- [ ] Rate Limiter - complete with tests
- [ ] Splitwise - complete with tests
- [ ] Ride Sharing - complete with tests
- [ ] Car Rental - complete with tests
- [ ] Online Shopping Cart - complete with tests
- [ ] Restaurant Management - complete with tests
- [ ] File System - complete with tests
- [ ] LinkedIn Connection - complete with tests
- [ ] Stack Overflow - complete with tests

### HLD Concepts

- [ ] Load Balancing - complete
- [ ] Caching - complete
- [ ] CDN - complete
- [ ] API Gateway - complete
- [ ] Rate Limiting - complete
- [ ] Database Sharding - complete
- [ ] Database Replication - complete
- [ ] Consistent Hashing - complete
- [ ] CAP Theorem - complete
- [ ] Message Queues - complete
- [ ] Microservices Communication - complete
- [ ] Service Discovery - complete

### HLD Projects (8 total)

- [ ] URL Shortener - complete with diagrams
- [ ] Twitter/News Feed - complete with diagrams
- [ ] Chat Service (WhatsApp) - complete with diagrams
- [ ] Video Streaming (YouTube) - complete with diagrams
- [ ] Ride Sharing (Uber) - complete with diagrams
- [ ] File Storage (Dropbox) - complete with diagrams
- [ ] Notification Service - complete with diagrams
- [ ] E-commerce (Amazon) - complete with diagrams

### GenAI Concepts (12 planned)

- [ ] RAG Architecture - complete
- [ ] LLM-Oriented System Design - complete
- [ ] Prompting, Tools & Agents - complete
- [ ] Safety & Governance - complete
- [ ] LLM Evaluation - complete
- [ ] Safety, Evaluation & Governance (consolidated) - complete
- [ ] Vector Databases - complete; currentness review tracked separately
- [ ] Model Routing & Orchestration - complete; currentness review tracked separately
- [ ] Streaming & KV-Cache - complete; currentness review tracked separately
- [ ] Token / Cost / Latency Planning - complete; currentness review tracked separately
- [ ] GenAI Design Patterns - complete; currentness review tracked separately
- [ ] Model Generalization - complete; currentness review tracked separately

### GenAI LLD Projects (9 planned)

- [ ] Document Chunker & Metadata Indexer - complete with tests
- [ ] Retriever & Ranker - complete with tests
- [ ] Prompt Builder - complete with tests
- [ ] Conversation Memory Store - complete with tests
- [ ] Safety Filter & Policy Engine - complete with tests
- [ ] LLM Request Orchestrator - complete with tests
- [ ] Embedding Service - complete with tests
- [ ] Tool Router - complete with tests
- [ ] Evaluation Harness - complete with tests

### GenAI HLD Projects (7 total)

- [ ] Document Q&A (RAG) - complete with diagrams
- [ ] Multi-Tenant Chat Assistant - complete with diagrams
- [ ] AI Coding Copilot - complete with diagrams
- [ ] Agentic Workflow Orchestrator - complete with diagrams
- [ ] LLM Evaluation & Safety Platform - complete with diagrams
- [ ] LLM Safety & Eval Platform (Governance-Focused) - complete with diagrams
- [ ] Semantic Retrieval Platform - complete with diagrams

---

## 🤖 GenAI Content Consistency (`06-genai-systems/`)

### GenAI Concepts (`00-concepts/`)

- [ ] Each concept folder contains a `README.md` with required sections: 📚 Theory, 🏗️ How It Works, ⚖️ Trade-offs, 🎯 When to Use, 🔗 Cross-links
- [ ] Concepts cross-link to relevant classical HLD concepts in `03-hld-concepts/` (e.g., caching → semantic caching)
- [ ] Concepts cross-link to GenAI HLD projects in `02-llm-hld-projects/` that use them
- [ ] Status indicators (`✅`/`🔜`) in `00-concepts/README.md` match actual content

### GenAI LLD Projects (`01-llm-lld-projects/`)

- [ ] Each project has `PROBLEM.md`, code under `python/v*-*/`, and tests under `python/tests/`
- [ ] Python code follows `snake_case` modules, `PascalCase` classes, type hints, and docstrings
- [ ] No external Python dependencies introduced without maintainer approval (standard library only)
- [ ] Tests pass: `python -m pytest <project>/python/tests -v`
- [ ] Projects cross-link to the GenAI concepts they implement
- [ ] Version tracks (`v1-basic`, `v2-extended`, `v3-optimized`) are used where appropriate

### GenAI HLD Projects (`02-llm-hld-projects/`)

- [ ] Each project has `PROBLEM.md`, `DESIGN.md`, `APPROACH.md`, and a `diagrams/` subfolder
- [ ] Designs follow the GenAI design template (`GENAI-DESIGN-TEMPLATE.md`)
- [ ] GenAI-specific sections present: Model Selection & Routing, RAG Pipeline, Safety & Guardrails, Evaluation & Observability, Cost & Latency Analysis
- [ ] Cross-links to GenAI concepts (`00-concepts/`) use correct relative paths
- [ ] Cross-links to classical concepts (`03-hld-concepts/`) use correct relative paths
- [ ] Diagrams are `.mmd` only; no committed `.svg` or `.png` binary files
- [ ] If diagram syntax was changed, `mmdc` render smoke was run to `/tmp` or missing `mmdc` was recorded as a local tooling blocker

### GenAI Cross-Links & Alignment

- [ ] `06-genai-systems/README.md` progress tracker matches actual shipped content
- [ ] Root `README.md` progress tracker reflects GenAI section status
- [ ] `CONCEPTS.md` (root) includes entries for GenAI concepts where applicable
- [ ] GenAI HLD projects link back to classical sections (`03-hld-concepts/`, `04-hld-projects/`, `01-design-patterns/`)
- [ ] No broken internal links within `06-genai-systems/`

### GenAI Pattern Currency

- [ ] Volatile GenAI provider/model/pricing/safety claims are covered by `resources/GENAI-CURRENTNESS-LEDGER.md` and pass `python3 -B scripts/check_genai_currentness.py`
- [ ] RAG architecture patterns reflect current best practices (chunking strategies, reranking, hybrid search)
- [ ] Safety and governance content aligns with latest frameworks and industry guidelines
- [ ] Evaluation approaches include up-to-date metrics and red-teaming methodologies
- [ ] Agent/tool-use patterns reflect current orchestration best practices
- [ ] LLD component designs are consistent with the HLD projects that reference them

---

## 🔗 Cross-Reference Audit

### Pattern Cross-References
- [ ] Each pattern links to LLD projects using it
- [ ] Each pattern links to related patterns
- [ ] Each pattern links to relevant theory

### Project Cross-References
- [ ] Each LLD project links to patterns used
- [ ] Each LLD project links to similar projects
- [ ] Each HLD project links to concepts used
- [ ] Each HLD project links to similar systems

### Concept Cross-References
- [ ] Each concept links to HLD systems using it
- [ ] Each concept links to related concepts
- [ ] Each concept links to foundational theory

---

## 🔧 Technical Checks

### Links
- [ ] All internal links work (no 404s)
- [ ] External links are valid
- [ ] Images load correctly
- [ ] Diagrams are visible

### File Structure
- [ ] No empty folders
- [ ] No orphan files
- [ ] Consistent folder naming
- [ ] Proper `.gitignore` coverage

### Build/Test
- [ ] All Java code compiles
- [ ] All Python code runs without syntax errors
- [ ] All tests pass
- [ ] No deprecated dependencies

---

## 📝 Quality Checks

### Writing Quality
- [ ] No spelling errors
- [ ] No grammar issues
- [ ] Consistent terminology
- [ ] Clear and concise explanations

### Formatting
- [ ] Consistent header levels
- [ ] Consistent list formatting
- [ ] Consistent table formatting
- [ ] Consistent code block formatting

### Accessibility
- [ ] Images have alt text
- [ ] Tables have headers
- [ ] Links have descriptive text

---

## 📅 Audit Schedule

| Check Type | Frequency | Last Completed |
|------------|-----------|----------------|
| Code Standards | Monthly | YYYY-MM-DD |
| Documentation | Monthly | YYYY-MM-DD |
| Content Completeness | Quarterly | YYYY-MM-DD |
| Cross-References | Quarterly | YYYY-MM-DD |
| GenAI Content & Alignment | Quarterly | YYYY-MM-DD |
| GenAI Pattern Currency | Semi-annually | 2026-06-14 |
| Technical Checks | Before release | YYYY-MM-DD |
| Quality Checks | Before release | YYYY-MM-DD |

> **Note**: Track audit completion in GitHub Issues with label `audit` for better visibility.

---

## 🐛 Issues Found

Track issues found during audit:

| Date | Category | Issue | Status |
|------|----------|-------|--------|
| | | | |
| | | | |
| | | | |

---

<p align="center">
  <b>Consistency builds quality! 📋</b>
</p>
