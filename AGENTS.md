# AGENTS Handbook

## Repository Intent
- Provide a single, interview-oriented curriculum spanning theory, design patterns, LLD/HLD projects, quizzes, flashcards, and templates.
- Maintain executable examples and accompanying tests in **Java 11+** and **Python 3.8+**, keeping language parity for every code artifact.
- Preserve progressive solution tracks (`v1-basic`, `v2-extended`, `v3-optimized`) so learners can observe iterative refinement.

## Directory Map & Responsibilities
| Path | Purpose | Notes |
|------|---------|-------|
| `README.md`, `QUICK-START.md`, `CONCEPTS.md` | Global overview, study plans, quick references | Keep cross-links and metrics current when adding content. |
| `00-theory/` | Core CS fundamentals | Markdown only; follow per-topic guidance in `00-theory/AGENTS.md`. |
| `01-design-patterns/` | GoF patterns with code | Maintain Java/Python parity and versioned folders; see local `AGENTS.md`. |
| `02-lld-projects/` | Interview-grade LLD problems | Track exact docs, dual-language code, tests, and version progression in `02-lld-projects/lld-doc-coverage-matrix.md`. |
| `03-hld-concepts/` | Distributed systems building blocks | Sync concept docs with diagrams in `diagrams/`; respect local `AGENTS.md`. |
| `04-hld-projects/` | Full HLD case studies + template | Update `DESIGN-TEMPLATE.md` before altering individual systems. |
| `05-coding-problems/` | Algorithm practice (WIP) | Retain "🔜 Coming Soon" placeholders until topics are complete. |
| `06-genai-systems/` | GenAI concepts, LLD & HLD projects | Python-first; follow `06-genai-systems/AGENTS.md` for GenAI-specific conventions. |
| `apps/portal/` | Next.js learning portal | Reads Markdown at build time; see `apps/portal/AGENTS.md` for routing and registry guidance. |
| `case-studies/` | Real-world architecture deep dives | Keep scale metrics sourced; update cross-references on new studies. |
| `resources/` | Study plans, cheatsheets, interview tips, templates | Update indices and maintenance guides in tandem. See `resources/CONTRIBUTOR-PLAYBOOK.md` for end-to-end recipes. |
| `flashcards/` | Question-only decks + exports | Preserve counts/descriptions; sync with Anki export instructions. |
| `diagrams/` | Mermaid (`.mmd`) sources | Keep source diagrams versioned; render temporary assets only for validation or external export. |
| `quizzes/` | Markdown quizzes + answer keys | Maintain naming, scoring tables, and alignment with repo content. |
| `.github/CONTRIBUTING.md` | Canonical style guide | Overrides any conflicting guidance; review before major changes. |

## Runtimes, Tools, and Dependencies
- **Languages:** Java 11+ (no external libraries), Python 3.8+ (standard library only).
- **Testing:** JUnit 5 console runner (`junit-platform-console-standalone.jar`) for Java; `pytest` or `unittest` for Python.
- **Build tooling:** None required beyond language toolchains; treat each project as self-contained.
- **Diagrams:** Mermaid CLI (`mmdc`) for rendering `.mmd` files to images when needed.
- **Dependency policy:** Do not introduce new build systems, package managers, or third-party libs without maintainer approval.

## Configuration & Schema Conventions
- Numbered top-level directories (`00-`, `01-`, …) define study flow—do not renumber without owner sign-off.
- Every code-based topic keeps Java and Python under `java/` and `python/` with versioned subfolders; tests live in sibling `tests/` directories.
- Documentation templates (e.g., `resources/templates/`, `04-hld-projects/DESIGN-TEMPLATE.md`) are authoritative; update them before altering downstream content.
- Shared diagrams reside in `diagrams/`; project-specific diagrams may live in that project's `diagrams/` subfolder. Link `.mmd` sources via relative paths unless an explicitly exported artifact is requested.

## Coding Standards
- **Dual-language commitment:** Update both Java and Python implementations for any shared logic unless project docs explicitly mark a language gap.
- **Java:**
  - Follow `.github/CONTRIBUTING.md` (PascalCase classes, camelCase methods, `UPPER_SNAKE_CASE` constants, constructor injection, Javadoc + complexity notes).
  - Keep stateful singletons resettable (`resetInstance`) for tests.
- **Python:**
  - Use `snake_case` modules, `PascalCase` classes, `UPPER_SNAKE_CASE` constants, and type hints throughout.
  - Provide docstrings for public APIs; prefer `dataclasses` where fitting.
- **Both:**
  - Avoid inline comments for obvious logic; document design choices, trade-offs, and complexity.
  - Keep demo entry points (`*Demo.*`) compiling and runnable.
  - Do not add formatters or linters; follow established manual style.

## Documentation Standards
- Use the structure and iconography defined in `.github/CONTRIBUTING.md` (`📚 Theory`, `🏗️ Implementation`, `🎯 When to Use`, etc.).
- Update tables of contents, status columns, and progress trackers whenever content changes.
- Maintain emoji markers (✅ complete, 🔜 coming soon) consistently across dashboards and summaries.
- Cross-link related material with relative paths; update `CONCEPTS.md`, study plans, and maintenance guides when learning order or coverage shifts.
- Respect and consult localized `AGENTS.md` files for subdirectory-specific instructions; the deepest applicable scope wins.

## Testing Strategy
- **Java:**
  1. Compile: `javac path/to/classes/*.java` (include relevant `v#` folder).
  2. Test: `java -jar junit-platform-console-standalone.jar --scan-classpath --classpath path/to/classes:path/to/tests`.
  3. Clean: inventory generated `.class` files before deletion (`find . -name '*.class' -print`) or compile into `/tmp`.
- **Python:**
  - Preferred: `python -m pytest <project>/python/tests -v`.
  - Fallback: `python -m unittest discover <project>/python/tests`.
- **Manual reviews:** For diagram-heavy or documentation-only updates, run through `resources/CONSISTENCY-AUDIT.md`.
- **Quality gate:** Passing local tests (or documented reasoning for omissions) plus updated docs are mandatory before raising a PR. GitHub Actions smoke workflows exist for the stable repository/portal gates, including readability and link checks. Local evidence remains required because optional Java/Mermaid probes and any owner-approved source metadata refresh can depend on workstation tooling, explicit approval, or private ignored artifacts.

## Build, Packaging, and Assets
- No repo-wide build or packaging workflow. Treat each folder as its own learning module.
- Keep compiled artifacts, archives, and personal notes out of version control; `.gitignore` already excludes common outputs.
- Mermaid source files are the canonical committed assets. Do not commit generated SVG/PNG files unless a task explicitly requests rendered exports; when rendering for validation, write outputs under `/tmp`.
- Flashcards, quizzes, and study guides remain Markdown; do not introduce proprietary formats or binaries.

## Portal Sync
The learning portal (`apps/portal/`) is a read-only Next.js view over the Markdown content. The portal **auto-discovers** topics by scanning content directories at build time (see `apps/portal/src/content/registry.ts`).

- **Adding content to an existing section:** No portal changes needed — place files in the correct folder and they will be discovered automatically.
- **Adjusting difficulty:** Optionally update the `DIFFICULTY` map in `registry.ts` if the default difficulty classification needs adjustment.
- **Adding a new top-level section:** Create a route folder under `apps/portal/src/app/`, add a nav entry in `apps/portal/src/lib/sections.ts` `PORTAL_SECTIONS`, add route-manifest coverage in `apps/portal/src/content/route-manifest.ts`, and add auto-discovery logic in `registry.ts`.
- **Adding a quiz:** Place `<topic>-quiz.md` in `quizzes/` — auto-discovered.
- **Adding an interview problem:** Add to `INTERVIEW_PROBLEMS` in `apps/portal/src/components/interview/interview-data.ts`.
- **Content-only edits:** No portal changes needed — Markdown is read at build time.
- **Root-level files in content dirs** (e.g., `HOW-TO-APPROACH.md`, `DESIGN-TEMPLATE.md`) are **not** auto-discovered — only subdirectory contents are scanned.

See `apps/portal/AGENTS.md` for detailed portal conventions and [`resources/CONTENT-UI-MAP.md`](resources/CONTENT-UI-MAP.md) for the full content-to-UI mapping, mismatch log, and extension guidelines.

## Contribution Workflow
> **Tip:** For step-by-step recipes (add an LLD problem, HLD project, GenAI topic, or design pattern end-to-end), see [`resources/CONTRIBUTOR-PLAYBOOK.md`](resources/CONTRIBUTOR-PLAYBOOK.md).

1. **Plan Scope:** Align changes with roadmap tables in `README.md` and confirm whether new material warrants a directory or entry.
2. **Implement:** Update code, docs, diagrams, flashcards, quizzes, and templates in sync. Preserve numbering prefixes and directory conventions.
3. **Cross-reference:** Adjust links in `README.md`, `CONCEPTS.md`, `case-studies/README.md`, study plans, and other indices.
4. **Validate:** Run relevant tests, regenerate diagrams if edited, and proofread Markdown using the established templates.
5. **Document:** Refresh status tables, progress trackers, and any metrics/badges impacted by the change.
6. **Portal:** New topics are auto-discovered; only update portal code for new sections/routes or difficulty overrides (see [Portal Sync](#portal-sync)).
7. **Prepare PR:** Use a feature branch; follow commit message format `<type>: <description>` (`feat`, `fix`, `docs`, `refactor`, `test`, `style`). Include testing evidence and list touched directories in the PR description.

## Special Handling & Gotchas
- **Numbered directories:** Never renumber top-level folders without maintainer approval.
- **Localized guidance:** Each major folder has its own `AGENTS.md`; always consult it before editing files in scope.
- **"Coming Soon" markers:** Retain 🔜 placeholders until content is fully delivered.
- **Singleton resets:** Many Java samples rely on singletons—call provided `reset` helpers between tests.
- **Python `sys.path`:** Tests often adjust `sys.path` to target specific versions; keep directory layouts intact.
- **Templates:** Treat `resources/templates/` and `04-hld-projects/DESIGN-TEMPLATE.md` as source of truth. Breaking changes must be coordinated and highlighted.
- **Diagrams:** Update textual explanations whenever altering Mermaid sources. Validate with `mmdc` when available; missing Mermaid CLI is a documented local blocker, not a reason to commit stale rendered assets.
- **Cleanup:** Inventory generated files and check `git status --short` before deletion. Prefer build outputs under `/tmp`; do not delete tracked files, lockfiles, legal/provenance manifests, or uncommitted user work as broad cleanup.
- **Secrets:** The repository must remain free of credentials or proprietary data. Sanitize all examples before committing.
- **GitHub authentication checks:** A failed `gh auth status` in a network-restricted sandbox may be a connectivity false negative, not proof that the token is invalid. Before asking the user to reauthenticate, retry `gh auth status --hostname github.com` with authorized network access and verify with a read-only request such as `gh api user --jq .login`. Never print, log, or expose token values.

## Quick Reference Commands
| Task | Command |
|------|---------|
| List Java test dirs | `find 02-lld-projects -path "*java/tests" -maxdepth 0` |
| Compile Parking Lot v1 | `javac 02-lld-projects/parking-lot/java/v1-basic/*.java` |
| Run Parking Lot demo | `java -cp 02-lld-projects/parking-lot/java/v1-basic ParkingDemo` |
| Run Elevator Java tests | `java -jar junit-platform-console-standalone.jar --classpath 02-lld-projects/elevator-system/java` |
| Run Elevator Python tests | `python -m unittest discover 02-lld-projects/elevator-system/python/tests` |
| Run Tic-Tac-Toe Python tests | `python -m pytest 02-lld-projects/tic-tac-toe/python/tests -v` |
| Run GenAI LLD tests | `python -m pytest 06-genai-systems/01-llm-lld-projects/<project>/python/tests -v` |
| Inventory `.class` files before cleanup | `find . -name '*.class' -print` |
| Render Mermaid diagram smoke | `mmdc -i diagrams/patterns/behavioral/observer.mmd -o /tmp/observer.svg` |
| Portal dev server | `cd apps/portal && npm run dev` |
| Portal lint | `cd apps/portal && npm run lint` |
| Portal build | `cd apps/portal && npm run build` |

## Escalation & Updates
- Update this handbook whenever tooling, workflows, branching policies, or supported languages change.
- Modify localized `AGENTS.md` files in the same PR and highlight their updates in the description.
- Flag breaking template or numbering changes to maintainers via PR summary and/or issue.
- Sync `.github/CONTRIBUTING.md`, top-level READMEs, study plans, and templates whenever repo-wide conventions shift.

## Onboarding Checklist for New Agents
- [ ] Read `.github/CONTRIBUTING.md` for canonical style and process guidance.
- [ ] Review this `AGENTS.md` plus localized `AGENTS.md` files covering your target directories.
- [ ] Understand study flow by skimming `README.md`, `QUICK-START.md`, and `CONCEPTS.md`.
- [ ] Ensure Java 11+ and Python 3.8+ toolchains are available locally.
- [ ] Download `junit-platform-console-standalone.jar` to run Java tests.
- [ ] Execute at least one Java (`02-lld-projects/elevator-system`) and one Python (`02-lld-projects/tic-tac-toe`) test suite end-to-end.
- [ ] Consult `resources/CONSISTENCY-AUDIT.md` before large documentation or structural edits.
- [ ] Confirm generated artifacts are ignored (`.gitignore`) and clean your workspace before committing.
