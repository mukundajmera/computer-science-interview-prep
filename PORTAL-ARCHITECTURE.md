# Portal Architecture & Sitemap — Phase 2

> **Purpose:** Architecture, tech-stack justification, sitemap, data model, and
> UI patterns for the `apps/portal` learning portal. The portal treats the
> repository's markdown content as the **single source of truth** — no content
> duplication.
>
> This document is the output of Prompt 2. Review and approve before proceeding
> to Prompt 3 (Implement Portal MVP).

> **Current status note (2026-06-13):** This is a historical portal design
> document. The live route/source contract is maintained in
> [`resources/CONTENT-UI-MAP.md`](resources/CONTENT-UI-MAP.md),
> [`apps/portal/AGENTS.md`](apps/portal/AGENTS.md), and
> `apps/portal/src/content/route-manifest.ts`. Flashcards remain non-portal
> study-aid files; `/resources` is live for study plans, cheatsheets,
> interview tips, and templates. Hidden `/reveal/*` routes are static-exported
> support routes for reveal panels; they are intentionally absent from nav and
> search.

---

## 1. Tech Stack Selection

### Chosen Stack

| Layer | Technology | Version |
|-------|-----------|---------|
| **Framework** | Next.js (App Router) | 14.x |
| **Language** | TypeScript | 5.x |
| **Styling** | Tailwind CSS | 3.x |
| **Markdown** | `gray-matter` + `unified`/`remark-parse`/`remark-gfm`/`remark-rehype`/`rehype-sanitize`/`rehype-stringify` | — |
| **Diagrams** | Mermaid `.mmd` source linked as learning artifacts; runtime rendering remains future work | — |
| **Code Highlighting** | `rehype-pretty-code` + `shiki` | — (future) |
| **Progress Storage** | `localStorage` (client-only; no backend) | — |
| **Package Manager** | npm | — |
| **Deployment** | Next.js static export (`output: "export"`) for GitHub Pages or any static host | — |

### Justification

| Requirement | How the stack meets it |
|-------------|----------------------|
| **Markdown-first** ([NORTH-STAR.md §C.1](NORTH-STAR.md#content-principles)) | `unified` + `remark`/`rehype` pipeline renders `.md` files at build time directly from the repo tree. HTML output is sanitized via `rehype-sanitize` to prevent XSS. No content is copied or duplicated — the portal reads files via `fs.readFileSync` relative to the repo root. |
| **Simple setup for learners** | `npm install && npm run dev` — single command. No database, no Docker, no separate API server. |
| **Standard library only** ([NORTH-STAR.md §C.4](NORTH-STAR.md#content-principles)) | The portal's own dependencies are limited to the JS/TS ecosystem. They do not affect the Java/Python code examples in the repo. |
| **Portal under `apps/portal/`** ([NORTH-STAR.md §C.9](NORTH-STAR.md#structural-principles)) | The app lives in `apps/portal/`, fully decoupled. A root `package.json` workspaces entry is optional but not required — `cd apps/portal && npm run dev` works standalone. |
| **Diagrams** | Mermaid `.mmd` files are source artifacts linked from content. Runtime diagram rendering is a future enhancement. |
| **No backend** | Progress tracking uses `localStorage`. No auth, no database. If a backend is needed later, Next.js API routes can be added incrementally. |
| **Static deployable** | `next export` produces a static site hostable on GitHub Pages, Vercel, or any CDN. |

### Alternatives Considered

| Alternative | Why not chosen |
|------------|---------------|
| **Docusaurus** | Opinionated sidebar structure doesn't map well to nested project dirs with Java/Python/version subfolders. Harder to add custom pages (interview mode, progress tracker). |
| **Astro** | Good fit for content sites, but smaller community for complex interactive features (quizzes, interview timers). Next.js has broader ecosystem. |
| **VitePress** | Vue-based; the React/Next.js ecosystem is more widely known among the target audience (engineers prepping for interviews). |
| **Plain HTML + JS** | No SSR, no routing, no component model. Would require reinventing too much. |

---

## 2. Sitemap & Routing

### Top-Level Routes

```
/                                           → Landing / Dashboard
├── /theory/                                → 00-theory section index
│   ├── /theory/[topic-area]/               → Topic area (e.g., oop-principles)
│   └── /theory/[topic-area]/[article]      → Individual article
│
├── /patterns/                              → 01-design-patterns section index
│   ├── /patterns/[category]/               → Category (creational, structural, behavioral)
│   └── /patterns/[category]/[pattern]      → Individual pattern page
│
├── /lld/                                   → 02-lld-projects section index
│   └── /lld/[project]                      → Individual LLD project page
│
├── /hld-concepts/                          → 03-hld-concepts section index
│   └── /hld-concepts/[concept]             → Individual HLD concept page
│
├── /hld/                                   → 04-hld-projects section index
│   └── /hld/[project]                      → Individual HLD project page
│
├── /coding/                                → 05-coding-problems section index
│   └── /coding/[pattern]                   → Algorithm pattern page
│
├── /genai/                                 → 06-genai-systems section index
│   ├── /genai/concepts/                    → Concepts sub-section
│   │   └── /genai/concepts/[concept]       → Individual GenAI concept
│   ├── /genai/lld/                         → GenAI LLD sub-section
│   │   └── /genai/lld/[project]            → Individual GenAI LLD project
│   └── /genai/hld/                         → GenAI HLD sub-section
│       └── /genai/hld/[project]            → Individual GenAI HLD project
│
├── /case-studies/                          → Case studies index
│   └── /case-studies/[study]               → Individual case study
│
├── /resources/                             → Resources hub
│   ├── /resources/study-plans/             → Study plan browser
│   ├── /resources/cheatsheets/             → Cheatsheet browser
│   ├── /resources/interview-tips/          → Interview tips browser
│   └── /resources/templates/               → Template browser
│
├── /quizzes/                               → Quiz index
│   └── /quizzes/[quiz]                     → Interactive quiz view
│
├── /progress/                              → Personal progress dashboard
│
└── /reveal/                                → Hidden static reveal endpoints
    ├── /reveal/solution/[type]/[slug]      → Interview coach answer
    └── /reveal/quiz-answer/[quiz]          → Quiz answer key
```

### Route-to-Filesystem Mapping

| Route Pattern | Filesystem Source | Page Type |
|--------------|------------------|-----------|
| `/theory/oop-principles/solid-principles` | `00-theory/oop-principles/solid-principles.md` | `article` |
| `/patterns/creational/singleton` | `01-design-patterns/creational/singleton/` | `pattern` |
| `/lld/parking-lot` | `02-lld-projects/parking-lot/` | `lld-project` |
| `/hld-concepts/caching` | `03-hld-concepts/caching/` | `hld-concept` |
| `/hld/url-shortener` | `04-hld-projects/url-shortener/` | `hld-project` |
| `/coding/two-pointers` | `05-coding-problems/two-pointers/` | `coding-pattern` |
| `/genai/concepts/rag-architecture` | `06-genai-systems/00-concepts/rag-architecture/` | `genai-concept` |
| `/genai/lld/chunker-metadata-indexer` | `06-genai-systems/01-llm-lld-projects/chunker-metadata-indexer/` | `genai-lld` |
| `/genai/hld/document-qa-rag` | `06-genai-systems/02-llm-hld-projects/document-qa-rag/` | `genai-hld` |
| `/case-studies/twitter-timeline` | `case-studies/twitter-timeline/` | `case-study` |
| `/quizzes/design-patterns-quiz` | `quizzes/design-patterns-quiz.md` | `quiz` |
| `/reveal/solution/lld/parking-lot` | `solutions/lld-parking-lot.md` through the curated `INTERVIEW_PROBLEMS` list | `hidden reveal` |
| `/reveal/quiz-answer/design-patterns` | `quizzes/answers/design-patterns-answers.md` when present | `hidden reveal` |

---

## 3. Data Model

### 3a. Content Metadata Schema

Every content item is represented as a **strongly-typed TypeScript object** derived
from the filesystem — no duplication. Metadata is extracted by convention (directory
name, presence of specific files, position in tree) plus optional YAML front matter
if present.

```typescript
// ---- Base types ----

type ContentCategory =
  | "theory"
  | "pattern"
  | "lld-project"
  | "hld-concept"
  | "hld-project"
  | "coding-pattern"
  | "genai-concept"
  | "genai-lld"
  | "genai-hld"
  | "case-study"
  | "quiz";

// Future extension: "flashcard-deck" if flashcards become portal-routed.

type Difficulty = "beginner" | "intermediate" | "advanced";

type ContentStatus = "complete" | "in-progress" | "coming-soon";

interface ContentItem {
  /** URL-safe identifier derived from directory name */
  id: string;

  /** Human-readable title derived from directory name or front matter */
  title: string;

  /** Content category determines page layout */
  category: ContentCategory;

  /** Difficulty level (derived from section README or front matter) */
  difficulty: Difficulty;

  /** Absolute filesystem path to content root */
  fsPath: string;

  /** URL path for the portal */
  href: string;

  /** Tags for search and filtering */
  tags: string[];

  /** Prerequisite content IDs */
  prereqs: string[];

  /** Suggested next content IDs */
  nextSteps: string[];

  /** Completion status */
  status: ContentStatus;
}
```

### 3b. Specialized Content Types

```typescript
// ---- Theory Article ----
interface TheoryArticle extends ContentItem {
  category: "theory";
  /** Topic area: oop-principles, database-concepts, etc. */
  topicArea: string;
  /** Markdown file path */
  markdownFile: string;
}

// ---- Design Pattern ----
interface DesignPattern extends ContentItem {
  category: "pattern";
  /** creational | structural | behavioral */
  patternCategory: "creational" | "structural" | "behavioral";
  /** Available doc files */
  docs: {
    readme: string | null;
    theory: string | null;
  };
  /** Code versions available */
  versions: VersionedCode[];
}

// ---- LLD Project ----
interface LLDProject extends ContentItem {
  category: "lld-project";
  docs: {
    problem: string | null;   // PROBLEM.md
    design: string | null;    // DESIGN.md
    approach: string | null;  // APPROACH.md
    walkthrough: string | null; // CODE-WALKTHROUGH.md
    rubric: string | null;    // RUBRIC.md (future)
    pitfalls: string | null;  // PITFALLS.md (future)
    followUps: string | null; // FOLLOW-UPS.md (future)
  };
  versions: VersionedCode[];
  /** Design patterns used in this project */
  patternsUsed: string[];
}

// ---- HLD Concept ----
interface HLDConcept extends ContentItem {
  category: "hld-concept";
  docs: {
    theory: string | null;      // THEORY.md
    interviewQA: string | null; // INTERVIEW-QA.md
  };
  versions: VersionedCode[];
  /** Which HLD projects use this concept */
  usedInProjects: string[];
}

// ---- HLD Project ----
interface HLDProject extends ContentItem {
  category: "hld-project";
  docs: {
    problem: string | null;
    design: string | null;
    approach: string | null;
    rubric: string | null;      // future
    pitfalls: string | null;    // future
    comparison: string | null;  // future
    followUps: string | null;   // future
    strongAnswer: string | null; // future
  };
  versions: VersionedCode[];
  /** Mermaid diagram files */
  diagrams: string[];
  /** HLD concepts applied in this project */
  conceptsUsed: string[];
}

// ---- GenAI Content Types ----
interface GenAIConcept extends ContentItem {
  category: "genai-concept";
  markdownFile: string;
}

interface GenAILLDProject extends ContentItem {
  category: "genai-lld";
  docs: {
    problem: string | null;
    design: string | null;
    approach: string | null;
  };
  /** Implementations — Python-only per AGENTS guidance; Java is a stretch goal */
  versions: VersionedCode[];
}

interface GenAIHLDProject extends ContentItem {
  category: "genai-hld";
  docs: {
    problem: string | null;
    design: string | null;
    approach: string | null;
  };
  /** Documentation + diagrams only (no implementation code per AGENTS) */
  diagrams: string[];
}

// ---- Case Study ----
interface CaseStudy extends ContentItem {
  category: "case-study";
  markdownFile: string;
  /** Company / system name */
  company: string;
  /** Related HLD projects */
  relatedProjects: string[];
}

// ---- Shared Types ----
/**
 * Version naming follows repo conventions:
 *   v1-basic     — Core solution, minimal features
 *   v2-extended  — Additional features (LLD) | v2-scaled (HLD) |
 *                  v2-realistic (concepts) | v2-variant (patterns)
 *   v3-optimized — Performance-tuned (LLD) | v3-distributed (HLD) |
 *                  v3-production (concepts) | v3-advanced (patterns)
 * The exact v2/v3 suffix varies by section; the scanner discovers them
 * dynamically rather than hard-coding the full union.
 */
interface VersionedCode {
  version: string;              // e.g. "v1-basic", "v2-extended", "v3-distributed"
  language: "java" | "python";
  path: string;
  files: string[];
  hasTests: boolean;
}
```

### 3c. Content Registry (Build-Time Generation)

At build time, a **content loader** scans the repo filesystem and produces a typed
registry. This is the only place filesystem scanning happens.

```typescript
// Generated at build time by scanning the repo tree
interface ContentRegistry {
  theory: TheoryArticle[];
  patterns: DesignPattern[];
  lldProjects: LLDProject[];
  hldConcepts: HLDConcept[];
  hldProjects: HLDProject[];
  codingPatterns: ContentItem[];
  genaiConcepts: GenAIConcept[];
  genaiLLD: GenAILLDProject[];
  genaiHLD: GenAIHLDProject[];
  caseStudies: CaseStudy[];
  flashcardDecks: ContentItem[];
  quizzes: ContentItem[];

  /** Flat lookup by ID */
  byId: Map<string, ContentItem>;

  /** Total counts per category */
  counts: Record<ContentCategory, number>;
}
```

### 3d. How Metadata Is Extracted (No Duplication)

| Metadata Field | Source | Example |
|---------------|--------|---------|
| `id` | Directory name | `parking-lot` |
| `title` | Directory name → title case, or `# heading` from README/THEORY.md | "Parking Lot" |
| `category` | Parent directory position in tree | `02-lld-projects/` → `lld-project` |
| `difficulty` | Lookup table in `apps/portal/content/difficulty-map.ts` | `parking-lot` → `beginner` |
| `tags` | Convention + optional YAML front matter in markdown | `["singleton", "thread-safety"]` |
| `prereqs` / `nextSteps` | Lookup table in `apps/portal/content/learning-paths.ts` | `prereqs: ["oop-principles"]` |
| `docs.*` | `fs.existsSync()` check for known filenames | `PROBLEM.md` exists → `docs.problem = path` |
| `versions` | Scan `java/` and `python/` subdirectories | `[{version: "v1-basic", language: "java", ...}]` |
| `diagrams` | Glob `diagrams/*.mmd` in project directory | `["architecture.mmd"]` |
| `status` | File presence heuristic: has README/THEORY → complete, only stub → coming-soon | `"complete"` |

**Key principle:** Metadata that would be duplicated across markdown and the
portal is either derived automatically from filesystem conventions or stored in
small lookup files inside `apps/portal/content/`. The markdown files themselves
are never modified for portal purposes.

---

## 4. Core UI Patterns

### 4a. Global Layout

```
┌─────────────────────────────────────────────────────┐
│  🎯 System Design Prep          [Progress: 42%] 🔍  │  ← Top nav
├──────────┬──────────────────────────────────────────┤
│          │                                          │
│  📚 Theory│  [Breadcrumb: Theory > OOP > SOLID]     │
│  🎨 Patt. │                                          │
│  🏗️ LLD   │  ┌─ Page Content ──────────────────┐    │
│  ⚙️ HLD-C │  │                                  │    │
│  🌐 HLD-P │  │  Rendered Markdown + Diagrams    │    │
│  🤖 GenAI │  │  + Code Tabs + Cross-Links       │    │
│  📊 Cases │  │                                  │    │
│  📅 Plans │  └──────────────────────────────────┘    │
│  📝 Quiz  │                                          │
│  🃏 Flash │  ┌─ Sidebar ──────────────────────┐     │
│           │  │ In-page TOC / Related Items     │     │
│           │  └────────────────────────────────┘      │
├──────────┴──────────────────────────────────────────┤
│  [Mark as Complete ✓]  |  [← Prev]  [Next →]        │  ← Bottom bar
└─────────────────────────────────────────────────────┘
```

**Components:**

| Component | Responsibility |
|-----------|---------------|
| `<AppShell>` | Top nav + left sidebar + main content area + bottom bar |
| `<SectionNav>` | Left sidebar: collapsible section navigation from `ContentRegistry` |
| `<Breadcrumb>` | Contextual breadcrumb trail |
| `<ProgressBadge>` | Top-right: global completion percentage |
| `<BottomNav>` | "Mark as Complete" toggle + prev/next navigation |
| `<SearchDialog>` | Cmd+K search across all content items |

### 4b. Topic Page Layout (Per Content Type)

#### Pattern: Project Page (LLD / HLD / GenAI)

```
┌─ Title ─────────────────────────────────────────────┐
│  🏗️ Parking Lot System           ⭐ Beginner          │
│  Tags: [OOP] [Strategy] [Factory]   [Mark Complete ✓]│
├─────────────────────────────────────────────────────┤
│  Tabs: [Overview] [Design] [Approach] [Code] [More] │
├─────────────────────────────────────────────────────┤
│                                                      │
│  [Overview Tab - PROBLEM.md rendered]                │
│                                                      │
│  📋 Requirements                                     │
│  🎯 Key Design Decisions                             │
│  ⚠️ Constraints                                      │
│                                                      │
├─────────────────────────────────────────────────────┤
│  [Design Tab - DESIGN.md rendered]                   │
│                                                      │
│  Class Diagram (Mermaid rendered)                    │
│  Entity Relationships                                │
│  API Contracts                                       │
│                                                      │
├─────────────────────────────────────────────────────┤
│  [Code Tab]                                          │
│                                                      │
│  Version: [v1-basic ▾]  Language: [Java ▾] [Python ▾]│
│  ┌─ Code viewer with syntax highlighting ──────────┐ │
│  │  // ParkingLot.java                              │ │
│  │  public class ParkingLot { ... }                 │ │
│  └──────────────────────────────────────────────────┘│
│                                                      │
├─────────────────────────────────────────────────────┤
│  [More Tab - when RUBRIC / PITFALLS / FOLLOW-UPS]   │
│                                                      │
│  📊 Scoring Rubric                                   │
│  ⚠️ Common Pitfalls                                  │
│  🔄 Follow-Up Variants                               │
│  🆚 Comparison with Similar Systems                  │
│                                                      │
├─────────────────────────────────────────────────────┤
│  📌 Cross-References                                 │
│  • Patterns used: Strategy, Factory Method           │
│  • Related HLD: Ride Sharing System                  │
│  • Next: Elevator System →                           │
└─────────────────────────────────────────────────────┘
```

#### Pattern: Concept Page (Theory / HLD Concept / GenAI Concept)

```
┌─ Title ─────────────────────────────────────────────┐
│  ⚙️ Caching                      ⭐⭐ Intermediate    │
├─────────────────────────────────────────────────────┤
│  Tabs: [Theory] [Interview Q&A] [Code] [Cross-Refs] │
├─────────────────────────────────────────────────────┤
│  [Theory Tab - THEORY.md rendered]                   │
│                                                      │
│  📖 What, Why, When                                  │
│  🔧 Types & Strategies                               │
│  📊 Comparison Tables                                │
│  🎯 Key Takeaways                                    │
│                                                      │
├─────────────────────────────────────────────────────┤
│  [Interview Q&A Tab - INTERVIEW-QA.md rendered]      │
│                                                      │
│  Expandable question/answer pairs                    │
│                                                      │
├─────────────────────────────────────────────────────┤
│  [Code Tab - same version/language selector]         │
├─────────────────────────────────────────────────────┤
│  📌 Used In: URL Shortener, News Feed, Video Stream  │
└─────────────────────────────────────────────────────┘
```

#### Pattern: Case Study Page

```
┌─ Title ─────────────────────────────────────────────┐
│  📊 Twitter Timeline Architecture                    │
├─────────────────────────────────────────────────────┤
│  [README.md rendered as single long-form article]    │
│                                                      │
│  Scale Metrics                                       │
│  Architecture Evolution                              │
│  Key Design Decisions                                │
│  Trade-offs                                          │
│  Lessons Learned                                     │
│                                                      │
├─────────────────────────────────────────────────────┤
│  📌 Related: News Feed System, Notification Service  │
└─────────────────────────────────────────────────────┘
```

#### Pattern: Flashcard Deck / Quiz

```
┌─ Flashcards: Design Patterns ───────────────────────┐
│                                                      │
│  Card 12 of 100              [Flip]                  │
│  ┌──────────────────────────────────────────┐        │
│  │  Q: What is the key difference between   │        │
│  │     Strategy and State patterns?          │        │
│  └──────────────────────────────────────────┘        │
│                                                      │
│  [← Prev]  [Shuffle 🔀]  [Next →]                   │
│                                                      │
│  Progress: ████████░░░░ 12/100                       │
└─────────────────────────────────────────────────────┘

┌─ Quiz: LLD Projects ───────────────────────────────┐
│                                                      │
│  Question 5 of 40            Timer: 0:45             │
│                                                      │
│  Which pattern best handles dynamic pricing          │
│  in a ride-sharing LLD?                              │
│                                                      │
│  ○ Observer     ○ Strategy                           │
│  ○ Singleton    ○ Factory                            │
│                                                      │
│  [Submit Answer]                                     │
│                                                      │
│  Score: 3/4 correct so far                           │
└─────────────────────────────────────────────────────┘
```

### 4c. Global Progress Indicator

**Storage:** `localStorage` key: `sdp-progress`. The key is stable; migrations
must normalize the value in place instead of switching keys and losing learner
progress.

```typescript
interface ProgressState {
  /** Schema version for idempotent localStorage migrations */
  version: 1;

  /** Map of content ID → completion timestamp */
  completed: Record<string, string>;     // e.g. { "lld-parking-lot": "2026-02-28T..." }

  /** Retired or unmapped IDs preserved for manual cleanup/recovery */
  legacyCompleted: Record<string, string>;
}
```

Future quiz scores, flashcard progress, or last-visited state should extend this
schema with an explicit version bump and migration test.

**Computation:**

```
Global % = (completed items in main track) / (total items in main track) × 100

Main track = theory articles + patterns + LLD projects + HLD concepts
           + HLD projects + GenAI concepts + GenAI LLD + GenAI HLD

Excludes: case studies, flashcards, quizzes, coding problems (optional)
```

**Stable ID policy:** content IDs are public persistence keys. Do not rename a
folder, route slug, or registry ID without adding an alias, running an
idempotent migration twice in tests, and preserving unknown IDs in
`legacyCompleted` rather than deleting them.

**Display:** Top-right badge in `<AppShell>` showing `42% complete`. Clicking
navigates to `/progress` which shows per-section breakdown.

---

## 5. Content Loading Architecture

### Build-Time Content Pipeline

```
                  ┌─────────────────────┐
                  │   Repository Root    │
                  │  (markdown + code)   │
                  └──────────┬──────────┘
                             │
                   ┌─────────▼──────────┐
                   │  Content Scanner    │
                   │  (build-time Node)  │
                   │                     │
                   │  • Walk dir tree    │
                   │  • Check file       │
                   │    existence        │
                   │  • Parse front      │
                   │    matter (if any)  │
                   │  • Apply lookup     │
                   │    tables           │
                   └─────────┬──────────┘
                             │
              ┌──────────────▼──────────────┐
              │    ContentRegistry JSON      │
              │  (generated at build time)   │
              │  • Typed metadata objects    │
              │  • No markdown content yet   │
              └──────────────┬──────────────┘
                             │
            ┌────────────────▼───────────────┐
            │  Next.js Static Generation     │
            │  (getStaticProps / generateSP) │
            │                                │
            │  • Read markdown on demand     │
            │  • Render via MDX pipeline     │
            │  • Inject metadata from        │
            │    registry                    │
            └────────────────────────────────┘
```

### Markdown Rendering Pipeline

```
.md file → gray-matter (extract front matter)
         → remark-gfm (GitHub Flavored Markdown)
         → remark-math (optional, for formulas)
         → rehype-pretty-code + shiki (syntax highlighting)
         → custom rehype plugin: mermaid code blocks → <MermaidDiagram>
         → custom rehype plugin: relative links → portal route links
         → React component tree
```

### Code File Loading

Source code files (`.java`, `.py`) are loaded at build time and embedded as
syntax-highlighted blocks. The code tab component receives:

```typescript
interface CodeTab {
  versions: {
    label: string;        // "v1-basic"
    languages: {
      label: string;      // "Java" | "Python"
      files: {
        name: string;     // "ParkingLot.java"
        content: string;  // Raw source code
        path: string;     // Relative path for display
      }[];
    }[];
  }[];
}
```

---

## 6. Portal Directory Structure

### Minimal File Plan

```
apps/portal/
├── package.json                    # Dependencies + scripts
├── tsconfig.json                   # TypeScript config
├── next.config.mjs                 # Next.js config (static export, MDX)
├── tailwind.config.ts              # Tailwind config
├── postcss.config.mjs              # PostCSS for Tailwind
├── .gitignore                      # node_modules, .next, out/
│
├── content/                        # Content configuration (NOT content itself)
│   ├── registry.ts                 # ContentRegistry builder (build-time scanner)
│   ├── loader.ts                   # Markdown + code file loaders
│   ├── difficulty-map.ts           # id → difficulty lookup
│   ├── learning-paths.ts           # Prereqs, next-steps, recommended order
│   ├── tags-map.ts                 # id → tags lookup
│   └── types.ts                    # TypeScript type definitions
│
├── components/                     # Reusable UI components
│   ├── layout/
│   │   ├── AppShell.tsx            # Global layout wrapper
│   │   ├── SectionNav.tsx          # Left sidebar navigation
│   │   ├── Breadcrumb.tsx          # Breadcrumb trail
│   │   ├── BottomNav.tsx           # Prev/Next + Mark Complete
│   │   └── ProgressBadge.tsx       # Top-right progress indicator
│   │
│   ├── content/
│   │   ├── MarkdownRenderer.tsx    # MDX rendering with custom components
│   │   ├── CodeViewer.tsx          # Tabbed code viewer (version × language)
│   │   ├── MermaidDiagram.tsx      # Client-side Mermaid renderer
│   │   ├── TabPanel.tsx            # Generic tabbed content panel
│   │   ├── CrossReferences.tsx     # Related items section
│   │   └── DifficultyBadge.tsx     # Difficulty level indicator
│   │
│   ├── interactive/
│   │   ├── FlashcardViewer.tsx     # Flashcard flip + navigation
│   │   ├── QuizRunner.tsx          # Quiz question display + scoring
│   │   └── SearchDialog.tsx        # Cmd+K global search
│   │
│   └── progress/
│       ├── ProgressTracker.tsx     # localStorage-backed progress state
│       ├── MarkCompleteButton.tsx  # Toggle completion for current item
│       └── ProgressDashboard.tsx   # Full progress view (/progress page)
│
├── app/                            # Next.js App Router pages
│   ├── layout.tsx                  # Root layout with AppShell
│   ├── page.tsx                    # Landing / dashboard
│   │
│   ├── theory/
│   │   ├── page.tsx                # Theory section index
│   │   └── [topicArea]/
│   │       ├── page.tsx            # Topic area index
│   │       └── [article]/
│   │           └── page.tsx        # Individual article
│   │
│   ├── patterns/
│   │   ├── page.tsx                # Patterns section index
│   │   └── [category]/
│   │       ├── page.tsx            # Category index
│   │       └── [pattern]/
│   │           └── page.tsx        # Individual pattern page
│   │
│   ├── lld/
│   │   ├── page.tsx                # LLD section index
│   │   └── [project]/
│   │       └── page.tsx            # Individual LLD project
│   │
│   ├── hld-concepts/
│   │   ├── page.tsx                # HLD Concepts section index
│   │   └── [concept]/
│   │       └── page.tsx            # Individual concept page
│   │
│   ├── hld/
│   │   ├── page.tsx                # HLD Projects section index
│   │   └── [project]/
│   │       └── page.tsx            # Individual HLD project
│   │
│   ├── coding/
│   │   ├── page.tsx                # Coding Problems section index
│   │   └── [pattern]/
│   │       └── page.tsx            # Individual coding pattern
│   │
│   ├── genai/
│   │   ├── page.tsx                # GenAI section index
│   │   ├── concepts/
│   │   │   ├── page.tsx            # Concepts sub-index
│   │   │   └── [concept]/
│   │   │       └── page.tsx        # Individual GenAI concept
│   │   ├── lld/
│   │   │   ├── page.tsx            # GenAI LLD sub-index
│   │   │   └── [project]/
│   │   │       └── page.tsx        # Individual GenAI LLD project
│   │   └── hld/
│   │       ├── page.tsx            # GenAI HLD sub-index
│   │       └── [project]/
│   │           └── page.tsx        # Individual GenAI HLD project
│   │
│   ├── case-studies/
│   │   ├── page.tsx                # Case Studies index
│   │   └── [study]/
│   │       └── page.tsx            # Individual case study
│   │
│   ├── resources/
│   │   ├── page.tsx                # Resources hub
│   │   ├── study-plans/
│   │   │   └── page.tsx            # Study plan browser
│   │   ├── cheatsheets/
│   │   │   └── page.tsx            # Cheatsheets browser
│   │   └── interview-tips/
│   │       └── page.tsx            # Interview tips browser
│   │
│   ├── flashcards/
│   ├── quizzes/
│   │   ├── page.tsx                # Quiz index
│   │   └── [quiz]/
│   │       └── page.tsx            # Interactive quiz runner
│   │
│   └── progress/
│       └── page.tsx                # Progress dashboard
│
├── lib/                            # Shared utilities
│   ├── markdown.ts                 # Markdown processing helpers
│   ├── mermaid.ts                  # Mermaid integration helpers
│   ├── sections.ts                 # Portal navigation contract
│   └── utils.ts                    # Slug generation, title formatting, compatibility exports
│
└── public/                         # Static assets
    └── favicon.ico
```

### File Count Summary

| Directory | Files | Purpose |
|-----------|-------|---------|
| `content/` | 6 | Content config & type defs |
| `components/` | 14 | Reusable React components |
| `app/` | ~35 | Next.js route pages |
| `lib/` | 3 | Shared utilities |
| Root config | 6 | package.json, tsconfig, etc. |
| **Total** | **~64** | — |

### How the Portal Imports Markdown

The portal reads markdown from the **repository root** using relative paths
resolved at build time:

```typescript
// apps/portal/content/loader.ts
import path from "path";
import fs from "fs";

/**
 * Repo root is two levels above apps/portal/.
 * In Next.js, process.cwd() points to the project root (apps/portal/)
 * during both dev and build. We resolve upward from there.
 */
const REPO_ROOT = path.resolve(process.cwd(), "../..");

export function loadMarkdown(relativePath: string): string {
  const fullPath = path.join(REPO_ROOT, relativePath);
  return fs.readFileSync(fullPath, "utf-8");
}

export function loadCodeFile(relativePath: string): string {
  return loadMarkdown(relativePath); // Same mechanism
}

export function fileExists(relativePath: string): boolean {
  return fs.existsSync(path.join(REPO_ROOT, relativePath));
}
```

---

## 7. Dependency Budget

| Package | Purpose | Size Impact |
|---------|---------|-------------|
| `next` | Framework | Core |
| `react`, `react-dom` | UI library | Core |
| `typescript` | Type safety | Dev only |
| `tailwindcss`, `postcss`, `autoprefixer` | Styling | Dev + runtime CSS |
| `next-mdx-remote` | MDX rendering | ~15 KB |
| `gray-matter` | YAML front matter parsing | ~5 KB |
| `remark-gfm` | GitHub Flavored Markdown | ~10 KB |
| `rehype-pretty-code` | Code syntax highlighting | ~20 KB |
| `shiki` | Syntax highlighting engine | ~2 MB (build; tree-shaken at runtime) |
| `mermaid` | Diagram rendering (client-side) | ~1.5 MB (lazy-loaded) |

**Total runtime JS budget:** < 200 KB (gzipped, excluding lazy-loaded Mermaid).
Mermaid is loaded only on pages with diagrams.

---

## 8. Future Extensions (Out of Scope for MVP)

| Extension | When | Notes |
|-----------|------|-------|
| **Interview Mode** | Prompt 5 | Timed walkthrough UI with rubric steps |
| **Backend + Auth** | Post-MVP | Sync progress across devices; optional |
| **Full-text search** | Post-MVP | Flexsearch or Algolia; Cmd+K initially searches the content registry only |
| **Dark mode** | Post-MVP | Tailwind `dark:` variants; add toggle in top nav |
| **CI for portal** | Post-MVP | `npm run build` in GitHub Actions to catch broken builds |
| **Rendered diagram cache** | Post-MVP | Pre-render `.mmd` → `.svg` at build time for faster page loads |

---

*This document is the output of Prompt 2 (Portal Architecture & Sitemap).
Review and approve before proceeding to Prompt 3 (Implement Portal MVP).*
