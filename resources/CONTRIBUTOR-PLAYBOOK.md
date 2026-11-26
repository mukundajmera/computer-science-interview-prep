# 📘 Contributor Playbook

> Step-by-step workflows for adding new content and keeping the repository coherent.

This playbook supplements [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md) with **end-to-end recipes** for the most common contribution scenarios. Follow the relevant recipe so that content, portal, practice layers, cross-references, and AGENTS guidance stay in sync.

---

## 📑 Table of Contents

- [Recipe 0 — Core Evidence Contract & Templates](#recipe-0--core-evidence-contract--templates)
- [Recipe 1 — Add a New LLD Problem](#recipe-1--add-a-new-lld-problem)
- [Recipe 2 — Add a New Classic HLD Project](#recipe-2--add-a-new-classic-hld-project)
- [Recipe 3 — Add a New GenAI SD Topic](#recipe-3--add-a-new-genai-sd-topic)
- [Recipe 4 — Add a New Design Pattern](#recipe-4--add-a-new-design-pattern)
- [Recipe 5 — Update the Portal When Content Changes](#recipe-5--update-the-portal-when-content-changes)
- [Running Checks](#running-checks)
- [Quick Reference — What to Update Where](#quick-reference--what-to-update-where)

---

## Recipe 0 — Core Evidence Contract & Templates

Before creating any new content, you must read the [Curriculum Evidence Contract](./templates/curriculum-evidence-contract.md). This defines our rules for correctness-first learning, layering, and assumptions.

1.  **Use Canonical Templates:** Base your new content on the authoritative templates in the appropriate directory (e.g., `04-hld-projects/DESIGN-TEMPLATE.md`).
2.  **Adhere to Scope Policies:** 
    *   Maintain the **Python-first / Markdown-only** policies for GenAI/Theory content.
    *   Preserve existing template compatibility and sections (including explicit normal, failure, and evidence fields without arbitrary line counts). Do not reinvent the wheel.
    *   No executable code or scripts should be added to `resources/` – all scripts belong in `scripts/`.
    *   For HLD, designs must remain docs-only unless an explicit policy exception allows for execution simulators.
3.  **Specify the Layering:** Clearly identify if the material targets Beginner, Core, or Staff level. Staff-level deeper-analysis is optional.

---

## Recipe 1 — Add a New LLD Problem

### 1. Scaffold the project folder

```
02-lld-projects/<project-name>/
├── PROBLEM.md
├── APPROACH.md
├── DESIGN.md
├── java/
│   ├── v1-basic/          # Minimal working solution
│   ├── v2-extended/       # Design patterns applied
│   ├── v3-optimized/      # Production-ready
│   └── tests/
├── python/
│   ├── v1-basic/
│   ├── v2-extended/
│   ├── v3-optimized/
│   └── tests/
└── README.md              # Summary with cross-links
```

Use lowercase, hyphen-separated folder names (e.g., `movie-ticket-booking`).

### 2. Write the content

| File | Key sections |
|------|-------------|
| `PROBLEM.md` | Problem Statement, Functional & Non-Functional Requirements, Constraints |
| `APPROACH.md` | Step-by-step design thinking, trade-off analysis |
| `DESIGN.md` | Entities, class diagram, data flow |
| Code (v1/v2/v3) | Progressive implementations in Java **and** Python |
| Tests | At minimum: happy path, edge cases, error handling |

Follow templates and standards in [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md) and [`02-lld-projects/AGENTS.md`](../02-lld-projects/AGENTS.md).

### 3. Add cross-references

- In the project `README.md`, link to patterns used, related theory, similar LLD projects, and related HLD systems (see [`resources/CROSS-REFERENCE-GUIDE.md`](./CROSS-REFERENCE-GUIDE.md)).
- Update the pattern READMEs that are used in this project to back-link here.

### 4. Update indexes

| File to update | What to add |
|----------------|-------------|
| `02-lld-projects/README.md` | Row in the project table with difficulty |
| Root `README.md` | Progress tracker entry (if tracked) |
| `CONCEPTS.md` | Entry if the project introduces a new concept |
| `resources/study-plans/` | Reference in relevant study plans |
| `flashcards/lld-concepts.md` | New flashcard(s) if applicable |
| `quizzes/lld-projects-quiz.md` | New quiz question(s) + answer key |

### 5. Update the portal

The portal auto-discovers new LLD projects by scanning `02-lld-projects/`. Ensure your new folder follows the scaffolded structure above. You only need to touch `apps/portal/src/content/registry.ts` if you want to set a non-default difficulty in the `DIFFICULTY` map. See [Recipe 5](#recipe-5--update-the-portal-when-content-changes).

### 6. Validate

```bash
# Java
javac 02-lld-projects/<project>/java/v1-basic/*.java
java -jar junit-platform-console-standalone.jar \
  --scan-classpath --classpath 02-lld-projects/<project>/java

# Python
python -m pytest 02-lld-projects/<project>/python/tests -v
```

---

## Recipe 2 — Add a New Classic HLD Project

### 1. Scaffold the project folder

```
04-hld-projects/<project-name>/
├── PROBLEM.md
├── DESIGN.md
├── APPROACH.md
├── diagrams/              # Mermaid .mmd sources
└── README.md
```

Follow the authoritative template in [`04-hld-projects/DESIGN-TEMPLATE.md`](../04-hld-projects/DESIGN-TEMPLATE.md).

### 2. Write the content

Include all sections from the template: Problem → Requirements → Capacity Estimation → API Design → Data Model → Architecture → Deep Dives → Trade-offs → Follow-ups.

### 3. Create diagrams

- Store Mermaid `.mmd` files in the project's `diagrams/` subfolder.
- Render locally to `/tmp` for validation: `mmdc -i diagrams/<file>.mmd -o /tmp/<file>.svg`
- Commit the `.mmd` source. Do not commit generated SVG/PNG files unless an explicit export task asks for rendered assets.

### 4. Add cross-references

- Link to HLD concepts used (`03-hld-concepts/`), related LLD projects, similar systems, and relevant design patterns.
- Update concept READMEs to back-link to this project.

### 5. Update indexes

| File to update | What to add |
|----------------|-------------|
| `04-hld-projects/README.md` | Row in the project table |
| Root `README.md` | Progress tracker entry |
| `case-studies/README.md` | Cross-link if a matching case study exists |
| `resources/study-plans/` | Reference in relevant study plans |

### 6. Validate portal integration

The portal auto-discovers HLD projects by scanning `04-hld-projects/`. Ensure your project folder and file layout follow the conventions above. No per-project `registry.ts` edit is needed unless you want to set a non-default difficulty. See [Recipe 5](#recipe-5--update-the-portal-when-content-changes).

### 7. Validate

- No executable code to test; run an editorial QA pass using [`resources/CONSISTENCY-AUDIT.md`](./CONSISTENCY-AUDIT.md).
- Verify all internal links resolve.

---

## Recipe 3 — Add a New GenAI SD Topic

GenAI content may be a **concept**, an **LLD component**, or an **HLD system**. Follow the relevant sub-recipe below.

### 3a. New GenAI Concept

1. Create `06-genai-systems/00-concepts/<concept-name>/README.md` with sections: **📚 Theory**, **🏗️ How It Works**, **⚖️ Trade-offs**, **🎯 When to Use**, **🔗 Cross-links**.
2. Cross-link to classical HLD concepts in `03-hld-concepts/` and to GenAI HLD projects that use this concept.
3. Update `06-genai-systems/00-concepts/README.md` status table.
4. Update `06-genai-systems/README.md` progress tracker.
5. Update root `CONCEPTS.md` if the concept warrants a top-level entry.

### 3b. New GenAI LLD Project

1. Scaffold under `06-genai-systems/01-llm-lld-projects/<project-name>/` with `PROBLEM.md`, `APPROACH.md`, `DESIGN.md`, `python/v1-basic/`, `python/tests/`.
2. Python-first; Java is optional. Follow conventions in [`06-genai-systems/AGENTS.md`](../06-genai-systems/AGENTS.md).
3. Cross-link to GenAI concepts the component implements.
4. Update `06-genai-systems/01-llm-lld-projects/README.md` and `06-genai-systems/README.md`.
5. Run tests: `python -m pytest 06-genai-systems/01-llm-lld-projects/<project>/python/tests -v`.

### 3c. New GenAI HLD Project

1. Scaffold under `06-genai-systems/02-llm-hld-projects/<project-name>/` with `PROBLEM.md`, `DESIGN.md`, `APPROACH.md`, `diagrams/`.
2. Include GenAI-specific sections: Model Selection & Routing, RAG Pipeline, Safety & Guardrails, Evaluation & Observability, Cost & Latency Analysis.
3. Cross-link to GenAI concepts and classical HLD concepts.
4. Update `06-genai-systems/02-llm-hld-projects/README.md`, `06-genai-systems/README.md`, and root `README.md`.

### Portal integration for all GenAI content

The portal auto-discovers GenAI content by scanning the `06-genai-systems/` folders. As long as you follow the folder/file conventions above, new GenAI topics will appear in the portal without any per-topic edits to `apps/portal/src/content/registry.ts`.

You only need to touch `registry.ts` for:
- Adding or renaming **top-level sections/routes** in the portal navigation
- Changing **global ordering/grouping** of sections
- Defining or overriding **difficulty metadata** that cannot be inferred from the content structure

See [Recipe 5](#recipe-5--update-the-portal-when-content-changes) for portal update workflows.

---

## Recipe 4 — Add a New Design Pattern

### 1. Scaffold the pattern folder

```
01-design-patterns/<category>/<pattern-name>/
├── README.md              # Theory, structure, when to use, trade-offs, Q&A
├── THEORY.md              # Deep-dive theory (if needed)
├── java/
│   ├── v1-basic/
│   ├── v2-extended/
│   ├── v3-optimized/
│   └── tests/
├── python/
│   ├── v1-basic/
│   ├── v2-extended/
│   ├── v3-optimized/
│   └── tests/
```

### 2. Write content and code

Follow the pattern template in [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md). Include `📚 Theory`, `🏗️ Implementation`, `🎯 When to Use`, `⚠️ Trade-offs`, `🔗 Related Patterns`, `❓ Interview Q&A`.

### 3. Add cross-references

- Link to LLD projects using this pattern, related theory, and similar/related patterns.
- Update LLD project READMEs to back-link to this pattern.

### 4. Update indexes

| File to update | What to add |
|----------------|-------------|
| Category `README.md` (e.g., `behavioral/README.md`) | Row in the pattern table |
| `01-design-patterns/README.md` | Update pattern count |
| `flashcards/design-patterns.md` | New flashcard(s) |
| `quizzes/design-patterns-quiz.md` | New quiz question(s) + answer key |

### 5. Create a diagram

Add a Mermaid class diagram in `diagrams/patterns/<category>/<pattern>.mmd`.

### 6. Validate portal integration

The portal auto-discovers patterns by scanning `01-design-patterns/`. No manual `registry.ts` edit is needed. See [Recipe 5](#recipe-5--update-the-portal-when-content-changes).

### 7. Validate

```bash
# Java
javac 01-design-patterns/<category>/<pattern>/java/v1-basic/*.java
java -jar junit-platform-console-standalone.jar \
  --scan-classpath --classpath 01-design-patterns/<category>/<pattern>/java

# Python
python -m pytest 01-design-patterns/<category>/<pattern>/python/tests -v
```

---

## Recipe 5 — Update the Portal When Content Changes

The portal app (`apps/portal/`) reads Markdown from the repo and renders it. The portal **auto-discovers** topics by scanning content directories at build time via `apps/portal/src/content/registry.ts`. Most content additions require no portal changes.

| Content change | Portal action |
|----------------|---------------|
| **New topic/project added under an existing section** | **No action needed** — auto-discovered from the content folder. Optionally add a `DIFFICULTY` entry in `registry.ts` if the default difficulty needs adjustment. |
| **Topic renamed/moved within the same section** | **No action needed** — auto-discovery picks up the change. Verify the route in `apps/portal/src/app/` and update any internal links that referenced the old path. |
| **New top-level section** | Add route folder under `apps/portal/src/app/`, register in navigation (`components/layout/`), and add auto-discovery logic in `registry.ts`. |
| **Difficulty metadata changed** | Update the `DIFFICULTY` map in `registry.ts` if the portal needs a different difficulty than the default. |
| **No structural change** (content edit only) | No portal change needed—Markdown is read at build time |

### Portal development commands

```bash
cd apps/portal
npm ci               # Reproducible install from package-lock.json
npm run dev          # Start dev server (http://localhost:3000)
npm run build        # Production build
npm run lint         # Lint check
```

Use Node.js 18.17+ with the committed portal lockfile. The latest local validation used Node v26.0.0 and npm 11.12.1.

### Key portal files

| File | Purpose |
|------|---------|
| `src/content/registry.ts` | Auto-discovery registry — scans content directories at build time; includes `DIFFICULTY` override map |
| `src/content/loader.ts` | Markdown file loader (reads from repo at build time) |
| `src/content/types.ts` | TypeScript type definitions for content objects |
| `src/app/` | Next.js route handlers (one folder per section) |
| `src/components/layout/` | Global navigation, sidebar, footer |
| `src/components/content/` | Reusable content rendering components |
| `src/components/progress/` | Local-storage progress tracker |

---

## Running Checks

### Repository smoke checks

Run the standard non-destructive smoke surface from the repo root:

```bash
PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_repo_smoke.py

# Discover stable check names
python3 scripts/check_repo_smoke.py --list

# Print commands without executing them
python3 scripts/check_repo_smoke.py --dry-run

# Run a narrower slice
python3 scripts/check_repo_smoke.py --only check_secret_artifacts check_markdown_links
```

The default smoke intentionally uses known-healthy link and inventory subsets. Java and Mermaid are opt-in toolchain probes because local installations vary; run them with `--only check_java_smoke check_mermaid` when the change touches Java examples or diagrams. Full link and inventory health gates are listed below and should pass before handoff for broad content, catalog, or portal changes unless an owner-approved allowlist records the exception.

The required GitHub Actions workflow in [`.github/workflows/repo-smoke.yml`](../.github/workflows/repo-smoke.yml) mirrors this stable surface: it installs portal dependencies with `npm ci`, runs the default smoke command, runs the full Markdown link and content inventory checks, runs portal tests, builds the portal, and compiles one Java smoke target into `/tmp`. Java/JUnit and Mermaid availability probes stay non-blocking until those external toolchains are pinned for the repository.

### Code tests

| Language | Command |
|----------|---------|
| **Java preflight + compile smoke** | `python3 scripts/check_java_smoke.py` |
| **Java compile** | `javac -d /tmp/sdip-java-smoke <path>/java/v1-basic/*.java` |
| **Java tests** | `java -jar junit-platform-console-standalone.jar --scan-classpath --classpath <path>/java` |
| **Python tests** | `python -m pytest <path>/python/tests -v` |
| **Python fallback** | `python -m unittest discover <path>/python/tests` |

`scripts/check_java_smoke.py` requires Java 11+, usable `javac`, and a JUnit 5 console standalone jar at `junit-platform-console-standalone.jar` or `JUNIT_PLATFORM_CONSOLE_STANDALONE_JAR`. It compiles the Parking Lot v1 smoke target to `/tmp/sdip-java-smoke` and refuses output directories inside the repository.

### Portal checks

```bash
cd apps/portal && npm run lint && npm run build
```

### Link checks

Validate local Markdown links and heading anchors with the repo-native checker:

```bash
python3 scripts/check_markdown_links.py

# Targeted checks for a smaller change surface
python3 scripts/check_markdown_links.py README.md resources/README.md

# Suppress intentional placeholders with exact source/target entries
python3 scripts/check_markdown_links.py --allowlist resources/link-allowlist.txt
```

Allowlist entries use `source.md|target` format. External URLs are skipped by default; this check is for local repo paths and Markdown anchors.

### Inventory checks

Validate portal-discovered content counts against `resources/CONTENT-UI-MAP.md`:

```bash
python3 scripts/check_content_inventory.py

# Targeted checks for one or more sections
python3 scripts/check_content_inventory.py --sections hld-concepts quizzes

# Machine-readable output for CI or scripted review
python3 scripts/check_content_inventory.py --format json
```

Validate that complete HLD concept folders are discoverable from the canonical learner catalog:

```bash
python3 scripts/check_hld_concept_catalog.py
```

This check compares `03-hld-concepts/<concept>/` folders that contain both `THEORY.md` and `INTERVIEW-QA.md` against `03-hld-concepts/README.md`. It requires catalog, concept-to-project mapping, and completion-checklist coverage while allowing external prerequisite links such as theory articles.

### Pattern completion checks

Validate that the design-pattern completion matrix matches the shipped pattern folders:

```bash
python3 scripts/check_pattern_completion.py
```

This check distinguishes theory, dual-language `v1-basic` examples, tests, and full v2/v3 progression. Do not mark a pattern as fully progressed unless the matching source folders exist.

### LLD project coverage checks

Validate that the LLD project coverage matrix matches shipped project docs, versioned code, and tests:

```bash
python3 scripts/check_lld_project_coverage.py
```

This check distinguishes core project docs, rubric/pitfalls/follow-up docs, Java/Python v1-v3 source, and Java/Python tests. Do not claim every LLD project has the full rubric pack unless this matrix proves it.

### Executable sample inventory checks

Validate that concept-level executable samples outside LLD project contracts are explicitly classified:

```bash
python3 scripts/check_executable_sample_inventory.py
python3 scripts/check_content_inventory.py --sections executable-samples
```

This check covers Java and Python source under `00-theory/`, `03-hld-concepts/`, `04-hld-projects/`, and `06-genai-systems/00-concepts/`, excluding tests and `__init__.py`. Use `tested` only when a same-language test suite exists in that concept folder; otherwise use `illustrative-only` or `move-to-lld`.

**Policy Decision Note:** A narrowly approved educational simulator exception allows executable code in classical concept/HLD directories.
- Approved source paths: `03-hld-concepts/<concept>/java/`, `03-hld-concepts/<concept>/python/`, `04-hld-projects/<project>/java/`, and `04-hld-projects/<project>/python/`.
- Language/test rules: Java 11+ SE and Python 3.8+ standard libraries only. No external dependencies, package managers, or frameworks. Full behavior parity across Java and Python. Clean local verification required.

### Secret artifact checks

Validate that tracked files do not include credential-like local artifacts:

```bash
python3 scripts/check_tracked_secret_artifacts.py

# Suppress intentional fixtures with exact or glob path entries
python3 scripts/check_tracked_secret_artifacts.py --allowlist resources/secret-artifact-allowlist.txt
```

This scanner is path-only: it uses `git ls-files` and never prints file contents or secret values. Allowlist globs are path-segment aware: `*` matches one path segment and `**` is required for recursive matches.

### Diagram generation

```bash
mmdc -i diagrams/<file>.mmd -o /tmp/<file>.svg
```

### Consistency audit

Run through the checklist in [`resources/CONSISTENCY-AUDIT.md`](./CONSISTENCY-AUDIT.md) for documentation-heavy changes.

### Clean up

Inventory first, then delete only a reviewed generated-output set:

```bash
git status --short
find . -name '*.class' -print

# After confirming the listed files are disposable build outputs:
find . -name '*.class' -delete
git status --short
```

Prefer compiling into `/tmp` or another disposable output directory so source-tree cleanup is rarely needed. Do not remove tracked files, lockfiles, legal/provenance manifests, or uncommitted user work as part of broad cleanup.

---

## Quick Reference — What to Update Where

Use this table as a final checklist before opening a PR.

| Action | Files to update |
|--------|----------------|
| **Any new content** | Section `README.md`, root `README.md` progress tracker |
| **New LLD project** | `02-lld-projects/README.md`, flashcards, quizzes, study plans (portal auto-discovers; optionally update `DIFFICULTY` map) |
| **New HLD project** | `04-hld-projects/README.md`, case-studies cross-links, study plans (portal auto-discovers) |
| **New GenAI topic** | `06-genai-systems/README.md`, subsection `README.md`, root `CONCEPTS.md` (if applicable) (portal auto-discovers) |
| **New design pattern** | Category `README.md`, `01-design-patterns/README.md`, flashcards, quizzes, diagrams (portal auto-discovers) |
| **New theory topic** | `00-theory/README.md`, root `CONCEPTS.md`, study plans |
| **Diagram added/changed** | `diagrams/` folder, regenerate SVG, mention command in PR |
| **Cross-references changed** | Follow [`resources/CROSS-REFERENCE-GUIDE.md`](./CROSS-REFERENCE-GUIDE.md) |

---

<p align="center">
  <b>Follow the recipes, keep indexes in sync, and the repo stays coherent! 📘</b>
</p>
