# AGENTS Guidance — 01-design-patterns

## Scope
Governs all files within `01-design-patterns/` and its subfolders.

## Structure Expectations
- Every pattern directory must contain:
  - `README.md` following the template in `.github/CONTRIBUTING.md`.
  - `THEORY.md` when present; keep theory and implementation sections synchronized.
  - `java/` and `python/` directories with parity across versions (`v1-basic`, `v2-extended`, `v3-advanced/optimized`).
- Preserve existing numbering and naming for pattern categories (`creational/`, `structural/`, `behavioral/`).

## Coding Standards
- Java: JDK 11+, follow repository-wide guidelines (Javadoc, complexity notes, constructor injection).
- Python: Python 3.8+, enforce type hints, docstrings, and `snake_case` modules.
- Maintain dual-language parity for every change unless a pattern is marked otherwise; note any intentional asymmetry inside the pattern README.
- Tests belong in `java/tests/` or `python/tests/` mirrors; reuse existing structure when expanding coverage.

## Documentation Requirements
- Update category README tables when adding or renaming patterns.
- Keep iconography and section ordering (`📚 Theory`, `🏗️ Implementation`, etc.) consistent.
- Reference relevant LLD projects or case studies when introducing new examples.

## Validation
- Compile Java implementations (`javac`) and run `java -jar junit-platform-console-standalone.jar` for updated tests.
- Execute Python tests via `python -m pytest <pattern>/python/tests` or `python -m unittest` fallback.

## Portal Integration
- The portal auto-discovers patterns by scanning `01-design-patterns/` directories; new or renamed patterns are picked up without manual edits to `apps/portal/src/content/registry.ts`.
- Only update `apps/portal/src/content/registry.ts` when changing discovery logic or adding a new top-level route/section.
- Content-only edits to existing pattern Markdown files require no portal changes.
- For full end-to-end instructions, including portal auto-discovery behavior, see [`resources/CONTRIBUTOR-PLAYBOOK.md`](../resources/CONTRIBUTOR-PLAYBOOK.md).

## Stability Guarantees
- Do not remove `v1/v2/v3` progression—learners rely on incremental difficulty.
- Do not rename pattern folder names (e.g., `singleton/`, `observer/`); the portal, cross-references, and diagrams link to them by path.
- Updating shared utilities (e.g., base classes) requires reviewing all affected patterns for compatibility.
- Keep Mermaid diagrams in sync with textual explanations when applicable.
