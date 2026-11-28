# 📋 Content ↔ Portal UI Map

> **Purpose:** Single source of truth for how the repository's Markdown content
> maps to routes and categories in the learning portal (`apps/portal/`).
> Consult this document whenever adding, renaming, or removing content to keep
> the filesystem and the UI aligned.

---

## Table of Contents

- [Content Inventory](#content-inventory)
- [Portal-Covered Categories](#portal-covered-categories)
- [Non-Portal Content](#non-portal-content)
- [Learning-Path Coverage](#learning-path-coverage)
- [Utility Routes](#utility-routes)
- [Mismatch Log](#mismatch-log)
- [Extension Guidelines](#extension-guidelines)
- [Cross-References](#cross-references)

---

## Content Inventory

Quick-reference counts (auto-discovery means these grow without portal changes):

| Section | Items | Source |
|---------|-------|--------|
| Theory articles | 74 | `00-theory/` (9 topic areas) |
| Design Patterns | 23 | `01-design-patterns/` (5 creational + 7 structural + 11 behavioral) |
| LLD Projects | 61 | `02-lld-projects/` |
| HLD Concepts | 64 | `03-hld-concepts/` |
| HLD Projects | 54 | `04-hld-projects/` |
| GenAI Concepts | 18 | `06-genai-systems/00-concepts/` |
| GenAI LLD Projects | 17 | `06-genai-systems/01-llm-lld-projects/` |
| GenAI HLD Projects | 16 | `06-genai-systems/02-llm-hld-projects/` |
| Coding Pattern Packs | 27 | `05-coding-problems/` (10 unnumbered doc packs with Interview Mode coach answers plus 17 numbered executable practice packs `01-two-pointers` to `17-union-find`: `two-pointers`, `sliding-window`, `binary-search`, `bfs-dfs`, `dynamic-programming`, `greedy`, `backtracking`, `heap-priority-queue`, `trie`, `union-find`) |
| Case Studies | 16 | `case-studies/` |
| Quizzes | 41 | `quizzes/` (networking-fundamentals, database-internals, os-concurrency, security-auth, design-patterns, lld-projects, lld-interview-framework, hld-concepts, hld-projects, infra-technologies, two-pointers, sliding-window, binary-search, bfs-dfs, dynamic-programming, greedy, backtracking, heap-priority-queue, trie, union-find, ai-coding-interview, ai-coding-interviews, applied-ml-system-design, genai-system-design, behavioral-interviews, salary-negotiation, distributed-systems-core, graph-algorithms, monotonic-stack, intervals-sweepline, bit-manipulation) |
| Interview Problems | 104 | `solutions/` (curated non-coding list plus auto-discovered coding pattern packs from `solutions/coding-*.md`) |
| Resources | 48 | `resources/{study-plans,cheatsheets,interview-tips,templates}/` public learner resource files (excludes category README files) |
| Flashcard Decks | 28 | `flashcards/` (design-patterns, lld-concepts, hld-concepts, infra-technologies, ai-coding-interview, ai-coding-interviews, applied-ml-system-design, genai-system-design, two-pointers, sliding-window, binary-search, bfs-dfs, dynamic-programming, greedy, backtracking, heap-priority-queue, trie, union-find, behavioral-interviews, salary-negotiation, distributed-systems-core) |
| Prompt Workflow Files | 0 | `prompts/` (not published in this public repository) |
| Executable Sample Files | 287 | `00-theory/`, `03-hld-concepts/`, and `06-genai-systems/00-concepts/` source samples; excludes tests and `__init__.py` |
| Mermaid Diagrams | 29 | `diagrams/` (23 patterns + 6 components) |

---

## Portal-Covered Categories

Each row describes one content category that is both **present in the
filesystem** and **reachable through the portal UI**.

| # | Category | Source Directory | File / Dir Pattern | Registry Key (`types.ts`) | Portal Route | Nav Link | Discovery Method | Items |
|---|----------|------------------|--------------------|--------------------------|--------------|----------|------------------|-------|
| 1 | Theory | `00-theory/` | `<topicArea>/*.md` | `theory` · `TheoryArticle[]` | `/theory` → `/theory/[topicArea]` → `/theory/[topicArea]/[article]` | Theory | Scans subdirs → markdown files | 74 |
| 2 | Design Patterns | `01-design-patterns/` | `<creational\|structural\|behavioral>/<pattern>/` | `patterns` · `DesignPattern[]` | `/patterns` → `/patterns/[category]` → `/patterns/[category]/[pattern]` | Design Patterns | Scans category dirs → pattern dirs | 23 |
| 3 | LLD Projects | `02-lld-projects/` | `<project>/` (PROBLEM.md, DESIGN.md, …) | `lldProjects` · `LLDProject[]` | `/lld` → `/lld/[project]` | LLD Projects | Scans subdirs | 61 |
| 4 | HLD Concepts | `03-hld-concepts/` | `<concept>/` (THEORY.md, INTERVIEW-QA.md) | `hldConcepts` · `HLDConcept[]` | `/hld-concepts` → `/hld-concepts/[concept]` | HLD Concepts | Scans subdirs | 64 |
| 5 | HLD Projects | `04-hld-projects/` | `<project>/` (PROBLEM.md, DESIGN.md, …) | `hldProjects` · `HLDProject[]` | `/hld` → `/hld/[project]` | HLD Projects | Scans subdirs | 54 |
| 6 | GenAI Concepts | `06-genai-systems/00-concepts/` | `<concept>/README.md` | `genaiConcepts` · `GenAIConcept[]` | `/genai` → `/genai/concepts/[concept]` | GenAI Systems | Scans subdirs | 18 |
| 7 | GenAI LLD | `06-genai-systems/01-llm-lld-projects/` | `<project>/` (PROBLEM.md, …) | `genaiLLD` · `GenAILLDProject[]` | `/genai` → `/genai/lld/[project]` | (same nav) | Scans subdirs | 17 |
| 8 | GenAI HLD | `06-genai-systems/02-llm-hld-projects/` | `<project>/` (PROBLEM.md, …) | `genaiHLD` · `GenAIHLDProject[]` | `/genai` → `/genai/hld/[project]` | (same nav) | Scans subdirs | 16 |
| 9 | Coding Patterns | `05-coding-problems/` | `<topic>/README.md` | `codingTopics` · `CodingTopic[]` | `/coding` → `/coding/[topic]` | Coding Patterns | Scans subdirs | 27 |
| 10 | Case Studies | `case-studies/` | `<study>/README.md` | `caseStudies` · `CaseStudy[]` | `/case-studies` → `/case-studies/[study]` | Case Studies | Scans subdirs |16 |
| 11 | Quizzes | `quizzes/` | `*-quiz.md` (answers in `answers/`) | *(not in registry — uses `listMarkdownFiles` directly)* | `/quizzes` → `/quizzes/[quiz]` | Quizzes | Scans `*-quiz.md` files | 41 |
| 12 | Interview Mode | `solutions/` + project dirs | Curated non-coding list plus `solutions/coding-*.md` | *(not in registry — uses `interviews.ts`)* | `/interview` → `/interview/[type]/[project]` | Interview Mode | Curated non-coding entries plus coding solution scan | 104 |
| 13 | Resources | `resources/{study-plans,cheatsheets,interview-tips,templates}/` | `<resource>.md` excluding category `README.md` files | *(not in registry — uses `resources.ts`)* | `/resources` → `/resources/[category]` → `/resources/[category]/[resource]` | Resources | Scans approved resource categories | 48 |

### Coverage Notes

- **All items discoverable:** Every subdirectory or markdown file matching
  the patterns above is automatically picked up by the portal's registry
  or loader. Adding a new project/concept/article under an existing section
  requires **zero portal changes**.
- **Quizzes** use a separate discovery path (`listMarkdownFiles("quizzes")`)
  rather than the central `ContentRegistry`. This works correctly; quiz
  files matching `*-quiz.md` are auto-discovered.
- **Interview Mode** uses curated non-coding entries plus auto-discovered
  coding packs from `solutions/coding-*.md`. New LLD, HLD, GenAI, or
  behavioral interview problems still need a curated entry; new coding packs
  are picked up automatically when the solution markdown is approved.
- **Resources** expose public study plans, cheatsheets, interview tips, and templates through a dedicated resource loader. Maintainer-only resource files remain excluded.
- **Root-level files in content dirs** (e.g., `README.md`, `AGENTS.md`,
  `HOW-TO-APPROACH.md`, `DESIGN-TEMPLATE.md`) are **not** scanned by the
  registry — only subdirectories and their contents are discovered. See the
  [Mismatch Log](#mismatch-log) for specific files affected.

---

## Non-Portal Content

The following directories and files contain valuable content that is **not
surfaced through the portal UI**. Each entry includes the rationale for
exclusion.

### Directories

| Directory | Content | Rationale for Exclusion |
|-----------|---------|------------------------|
| `flashcards/` | Markdown Q&A decks (`design-patterns.md`, `lld-concepts.md`, `hld-concepts.md`, `infra-technologies.md`, `ai-coding-interview.md`, `ai-coding-interviews.md`, `applied-ml-system-design.md`, `genai-system-design.md`, `two-pointers.md`, `sliding-window.md`, `binary-search.md`, `bfs-dfs.md`, `dynamic-programming.md`, `greedy.md`, `backtracking.md`, `heap-priority-queue.md`, `trie.md`, `union-find.md`, `behavioral-interviews.md`, `salary-negotiation.md`) + Anki export instructions | Designed for standalone study tools (Anki, printed cards). Their Q&A format does not fit the portal's topic-page layout. |
| `diagrams/` | Mermaid `.mmd` source files (29 files: 23 pattern + 6 component diagrams) | Source-only diagram artifacts. The portal does not render Mermaid at runtime; content links to `.mmd` sources for GitHub/preview-tool use. |
| `solutions/` | Coach-answer markdown files for Interview Mode (curated subset of many solutions) | Exposed only through hidden static reveal routes under `/reveal/solution/[type]/[slug]`, which are fetched by Interview Mode. No standalone browse, nav, or search route is needed. |

### Portal-Covered Resource Files

The portal exposes these learner-facing resource subdirectories at `/resources`.
Category pages render the configured category label, description, and resource
list. Category `README.md` files are intentionally excluded from individual
resource pages and are not rendered as category-page bodies.

| Subdirectory | Files | Portal Behavior |
|--------------|-------|------------------------|
| `resources/study-plans/` | `1-week-plan.md`, `1-month-plan.md`, `topic-based-plan.md`, `genai-crash-track.md`, `genai-deep-dive.md` | Listed under `/resources/study-plans`; category README is excluded from the item list. |
| `resources/cheatsheets/` | `complexity-reference.md`, `pattern-decision-tree.md`, `hld-components-map.md`, `trade-offs-matrix.md`, `genai-system-design-one-pager.md`, `rag-architecture-cheatsheet.md` | Listed under `/resources/cheatsheets`; category README is excluded from the item list. |
| `resources/interview-tips/` | LLD/HLD checklists, behavioral/AI playbooks, salary negotiation, communication, and pitfalls guides | Listed under `/resources/interview-tips`; category README is excluded from the item list. |
| `resources/templates/` | LLD/HLD templates, practice worksheets, behavioral story template, salary negotiation worksheets | Listed under `/resources/templates`; category README is excluded from the item list. |

### Resource Files Not Surfaced Through the Portal

| Subdirectory | Files | Rationale for Exclusion |
|--------------|-------|------------------------|

### Root-Level Files Not Scanned by the Portal

| File | Content | Rationale |
|------|---------|-----------|
| `05-coding-problems/PATTERN-SD-MAP.md` | Maps coding patterns to system-design uses, related repo examples, and interview signals | Root-level coding guide; registry scans only pattern-pack subdirectories. Accessible on GitHub and linked from the coding README. |
| `05-coding-problems/TOP-20.md` | Curated internal coding-practice ladder with difficulty, core insight, related repo content, time targets, and Wave 3 extension rows | Root-level coding guide; registry scans only pattern-pack subdirectories. Accessible on GitHub and linked from the coding README. |
| `02-lld-projects/HOW-TO-APPROACH.md` | 7-step framework for tackling LLD problems | Root-level guide file; registry scans only project subdirectories. Accessible on GitHub. |
| `02-lld-projects/lld-doc-coverage-matrix.md` | Matrix of per-project docs, versioned code, and test coverage | Root-level maintenance/learner transparency file; registry scans only project subdirectories. Accessible on GitHub. |
| `resources/executable-sample-inventory.md` | Matrix of concept source samples and whether same-language tests exist | Maintainer/learner transparency file; not a portal content source. |
| `04-hld-projects/DESIGN-TEMPLATE.md` | HLD design document template | Authoritative template; registry scans only project subdirectories. Accessible on GitHub. |
| `06-genai-systems/CLASSIC-VS-GENAI.md` | Side-by-side comparison of classical vs GenAI system design | Cross-cutting guide; registry scans `00-concepts/`, `01-llm-lld-projects/`, `02-llm-hld-projects/` only. |
| `06-genai-systems/GENAI-SD-FRAMEWORK.md` | 6-step framework for GenAI system design interviews | Framework guide; not inside a scanned subdirectory. Referenced by GenAI study plans. |
| `06-genai-systems/PITFALLS.md` | Top 10 GenAI system design interview pitfalls | Pitfall-avoidance guide; not inside a scanned subdirectory. |
| Root: `CONCEPTS.md` | Quick-reference cheatsheet for all topics | Repository-level documentation for GitHub visitors. |
| Root: `QUICK-START.md` | Navigation and study-mode guide | Entry point for GitHub visitors. |
| Root: `NORTH-STAR.md` | Repository vision, audit, and strategic direction | Maintainer/contributor documentation. |
| Root: `CONTENT-MAP.md` | Future content architecture and phase plan | Maintainer/contributor documentation. |
| Root: `PORTAL-ARCHITECTURE.md` | Portal tech stack and sitemap | Maintainer/contributor documentation. |
| Root: `instruction.md` | LLM agent prompt-sequencing strategy | Internal development tooling. |

---

## Learning-Path Coverage

The main learning paths described in `README.md` and `QUICK-START.md` reference
topics across the repo. The table below confirms whether each referenced area
is reachable through the portal.

| Learning Path | Source File | Referenced Topics | Portal Reachable? | Non-Portal Companions |
|---------------|------------|-------------------|-------------------|-----------------------|
| **1-Week Crash Course** | `resources/study-plans/1-week-plan.md` | Design Patterns (Singleton, Factory, Strategy, Observer, Builder, Decorator), LLD (Parking Lot, LRU Cache, Elevator), HLD Concepts (Caching, Load Balancing, Sharding, Message Queues, CAP), HLD Projects (URL Shortener, Twitter Feed, Chat App, Video Streaming) | All topics reachable | `CONCEPTS.md`, cheatsheets, interview tips |
| **1-Month Deep Dive** | `resources/study-plans/1-month-plan.md` | All of the above + OOP/SOLID theory, all 23 design patterns, 10+ LLD projects, Case Studies, advanced HLD (Uber, E-commerce, Notifications) | All topics reachable | Templates, `HOW-TO-APPROACH.md` |
| **GenAI Crash Track** | `resources/study-plans/genai-crash-track.md` | GenAI Concepts (LLM System Design, RAG, Vector DBs, Prompting, Safety, Evaluation), GenAI LLD (Retriever-Ranker, Chunker, Prompt Builder, Memory Store, Orchestrator, Safety Filter), GenAI HLD (Document Q&A RAG, Chat Assistant) | All topics reachable | `GENAI-SD-FRAMEWORK.md`, GenAI cheatsheets |
| **GenAI Deep Dive** | `resources/study-plans/genai-deep-dive.md` | GenAI concepts + GenAI LLD/HLD project tracks + classical integration | All topics reachable | `CLASSIC-VS-GENAI.md`, `PITFALLS.md` |
| **Topic-Based Prep** | `resources/study-plans/topic-based-plan.md` | Individual topics across all sections — Design Patterns deep dive, LLD mastery, HLD fundamentals, Database/Storage, Caching, Concurrency | All topics reachable | `HOW-TO-APPROACH.md`, templates |

> **Summary:** Every curriculum topic described in the learning paths is
> reachable via the portal. Public study plans, cheatsheets, interview tips,
> and templates are also reachable through `/resources`; maintainer-only
> guides remain documented in the [Non-Portal Content](#non-portal-content)
> section above.

---

## Utility Routes

These portal routes do not map to filesystem content but provide UI features.

| Route | Purpose | Nav Link? | Notes |
|-------|---------|-----------|-------|
| `/` | Home page — grid of all portal sections | N/A (always visible) | Uses `PORTAL_SECTIONS` from `sections.ts` |
| `/progress` | User progress dashboard (`localStorage`-backed) | Not in `PORTAL_SECTIONS`; reachable via URL | Utility page, not a content section |
| `/reveal/solution/[type]/[slug]` | Static coach-answer endpoint used by Interview Mode reveal panels | No | Included in `route-manifest.ts` for static export coverage; excluded from search and section counts |
| `/reveal/quiz-answer/[quiz]` | Static quiz-answer endpoint for quizzes that have answer files | No | Generated only when a matching `quizzes/answers/*-answers.md` file exists; excluded from search and section counts |

---

## Mismatch Log

Mismatches detected during the coherence audit and their resolutions.

| # | Mismatch | Severity | Resolution |
|---|----------|----------|------------|
| 1 | `flashcards/` has 20 Q&A decks but no portal route | Low | Documented as non-portal content — study-aid format incompatible with topic-page layout. |
| 3 | `05-coding-problems/` was previously placeholder-only and non-portal | Resolved | Added `codingTopics` registry entry + `/coding` and `/coding/[topic]` routes; live packs now include `two-pointers`, `sliding-window`, `binary-search`, `bfs-dfs`, `dynamic-programming`, `greedy`, `backtracking`, `heap-priority-queue`, `trie`, and `union-find`. |
| 4 | `diagrams/` has 29 `.mmd` sources (23 pattern + 6 component) but no portal route | Low | Documented as non-portal source artifacts; rendered SVG/PNG files are not committed by default. |
| 5 | `solutions/` has many markdown files but no standalone browse route | Low | Documented as hidden reveal content — `/reveal/solution/[type]/[slug]` is exported for curated Interview Mode entries, but solutions stay out of nav and search. |
| 6 | `quizzes/` and Interview Mode use separate discovery paths outside `ContentRegistry` | Info | Acceptable by design — quizzes auto-discover `*-quiz.md` files; Interview Mode combines curated non-coding entries with auto-discovered coding packs. |
| 7 | `/progress` route exists but is not in `PORTAL_SECTIONS` navigation | Info | Acceptable — utility page, not a content section. Reachable via direct URL. |
| 8 | `06-genai-systems/CLASSIC-VS-GENAI.md`, `GENAI-SD-FRAMEWORK.md`, `PITFALLS.md` exist at root of `06-genai-systems/` but are not scanned by registry | Medium | Registry only scans `00-concepts/`, `01-llm-lld-projects/`, `02-llm-hld-projects/` subdirectories. These root-level guides are accessible on GitHub and referenced by study plans. Moving them into `00-concepts/` as dedicated concept directories would make them portal-discoverable without code changes. |
| 9 | `02-lld-projects/HOW-TO-APPROACH.md` and `02-lld-projects/lld-doc-coverage-matrix.md` are root-level files not scanned by registry | Low | Root-level guide and maintenance matrix; registry scans project subdirectories only. Accessible on GitHub. Could be relocated into dedicated subdirectories if portal discoverability is desired. |
| 10 | `04-hld-projects/DESIGN-TEMPLATE.md` is a root-level file not scanned by registry | Low | Authoritative template; registry scans project subdirectories only. Not user-facing curriculum content. |
| 11 | Non-coding inventory and portal counts drifted from repository discovery, and `Prompt Workflow Files` row was missing (2026-11-28) | Resolved | Updated non-coding counts across Content Inventory and Portal-Covered Categories (Theory 67→72, LLD Projects 56→61, HLD Concepts 59→64, HLD Projects 48→54, GenAI Concepts 14→18, GenAI HLD 10→16, Interview Problems/Mode 38→98, Resources portal 47→48, Executable Sample Files 255→287) and added `Prompt Workflow Files` with count `0` (not published in this public repository). Coding pattern counts remain at `10` pending alignment on numbered vs. unnumbered folders under `05-coding-problems/`. |
| 12 | Coding pattern and Theory counts drifted again (2026-11-28) | Resolved | Coding Patterns 10→27 (the portal publishes all 27 folders under `05-coding-problems/`; only the 10 unnumbered packs need an Interview Mode coach answer, `check_content_inventory.py` now encodes that), Interview Problems/Mode 98→104, Theory 72→73. |

---

## Extension Guidelines

### Adding a New Content Category

When introducing a new top-level content section (e.g., `07-new-topic/`):

1. **Create the content directory** at the repo root following the numbered
   prefix convention (`NN-topic-name/`). Add a `README.md` and `AGENTS.md`.

2. **Update the portal registry** — in `apps/portal/src/content/`:
   - `types.ts`: Add a new interface extending `ContentItem` and a new
     `ContentCategory` union member. Add the new array to `ContentRegistry`.
   - `registry.ts`: Add a scanning block that calls `listDirs()` or
     `listMarkdownFiles()` for the new directory and populates the registry
     array. Follow the existing pattern (e.g., the `theory` or `lldProjects`
     blocks).

3. **Add a portal route** — in `apps/portal/src/app/`:
   - Create `<route-name>/page.tsx` (list page) and optionally
     `<route-name>/[slug]/page.tsx` (detail page).
   - Import `buildRegistry()` and render the new content array.

4. **Add a navigation link and route contract**:
   - Append a new entry to `apps/portal/src/lib/sections.ts` `PORTAL_SECTIONS` with `label`, `href`, `emoji`, and `description`.
   - Add the route family to `apps/portal/src/content/route-manifest.ts` so duplicate-route and search contracts cover it.

5. **Update documentation**:
   - Add the new section to the "Directory Map" table in root `AGENTS.md`.
   - Update `README.md` repository structure and table of contents.
   - Add a row to the [Portal-Covered Categories](#portal-covered-categories)
     table and update the [Content Inventory](#content-inventory) in this file.

### Ensuring New Markdown Directories Are Auto-Discovered

The portal's `registry.ts` scans directories using `listDirs()` and
`listMarkdownFiles()` from `loader.ts`. To ensure new subdirectories are
picked up automatically:

- **Within an existing section:** Just create the subdirectory with the
  expected file structure. The existing scanning loop will discover it on
  the next build.
- **New section:** Add a scanning block to `registry.ts` (see step 2 above).
  Use `listDirs("<dir>")` to enumerate subdirectories and iterate over them.
  Avoid hard-coding directory names; the loop-based pattern ensures new
  subdirectories are picked up automatically.
- **Root-level files are not scanned.** Only content inside subdirectories is
  discovered. If you add a standalone `.md` file at the root of a content
  directory (e.g., `02-lld-projects/NEW-GUIDE.md`), it will **not** appear
  in the portal. Either place it inside a subdirectory or note it in
  [Non-Portal Content](#non-portal-content).

### Adding a New Quiz

Place a new `<topic>-quiz.md` file in `quizzes/` and optionally add
`quizzes/answers/<topic>-answers.md`. The portal auto-discovers files
matching the `*-quiz.md` pattern — no code changes needed.

### Adding a New Interview Problem

Add a new entry to the `INTERVIEW_PROBLEMS` array in
`apps/portal/src/components/interview/interview-data.ts`. Provide:
- `slug` — URL-safe identifier.
- `title` — display name.
- `type` — one of `"lld"`, `"hld"`, `"genai-hld"`, `"behavioral"`, or `"coding"` (maps to a template).
- `difficulty` — `"beginner"`, `"intermediate"`, or `"advanced"`.
- `solutionPath` — relative path to a markdown file in `solutions/`.

### Adding a New Case Study

Create a new subdirectory under `case-studies/` with a `README.md`. The
portal auto-discovers it — no code changes needed.

### Marking Content as Non-Portal

If a directory or file intentionally should not appear in the portal, add a
row to the [Non-Portal Content](#non-portal-content) section above with a
brief rationale. This prevents future audits from flagging the same item as
a mismatch.

---

## Cross-References

- **Root handbook:** [`AGENTS.md`](../AGENTS.md) → Portal Sync section
- **Portal guidance:** [`apps/portal/AGENTS.md`](../apps/portal/AGENTS.md)
- **Contributor recipes:** [`resources/CONTRIBUTOR-PLAYBOOK.md`](CONTRIBUTOR-PLAYBOOK.md)
- **Consistency audits:** [`resources/CONSISTENCY-AUDIT.md`](CONSISTENCY-AUDIT.md)
- **Content architecture:** [`CONTENT-MAP.md`](../CONTENT-MAP.md)
- **Repository vision:** [`NORTH-STAR.md`](../NORTH-STAR.md)

---

*Last updated: 2026-11-28 — refreshed non-coding inventory and portal category counts and added the Prompt Workflow Files row.*

---

## March 2026 Mapping Delta

- New HLD folders added under `04-hld-projects/`: `online-auction`, `live-comments`, `social-post-search`, `price-tracking-service`.
- New LLD folders added under `02-lld-projects/`: `online-auction`, `live-comments`, `social-post-search`, `price-tracking-service`, `instagram-core`, `youtube-top-k`.
- Source 24-28 additions:
  - HLD: `job-scheduler`, `web-crawler`, `ad-click-aggregator`, `payment-system`, `metrics-monitoring`
  - LLD: `job-scheduler`, `web-crawler`, `ad-click-aggregator`, `payment-system`
- Source 04-07 additions:
  - HLD: `content-moderation-platform`, `bot-detection-platform`
  - HLD: `video-recommendations` is the standalone recommendation ranking subsystem
- Interview Mode list expanded in portal metadata for new flagship HLD problems.
