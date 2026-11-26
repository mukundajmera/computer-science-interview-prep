# AGENTS Guidance — 03-hld-concepts

## Scope
Applicable to all concept guides within `03-hld-concepts/`.

## Content Standards
- Retain structured tables (Status column, concept grouping) and emoji indicators when adding or editing topics.
- Expand each concept with practical trade-offs, capacity planning numbers, and technology references aligned with `.github/CONTRIBUTING.md`.
- Keep individual concept folders (`concept-name/README.md`) organized and linked from the directory `README.md` and dependency maps.

## Cross-Linking
- Reference supporting material in `04-hld-projects/` and `case-studies/` to show applications.
- Link diagrams from `diagrams/components/` or `diagrams/patterns/`; update both doc and diagram when changing either.
- Update study plans or quick-reference guides if new concepts alter recommended learning order.

## Documentation Workflow
- Markdown generally, but a narrowly approved educational simulator exception allows executable code.
  - Approved source paths: `03-hld-concepts/<concept>/java/` and `03-hld-concepts/<concept>/python/`.
  - Language/test rules: Java 11+ SE and Python 3.8+ standard libraries only. No external dependencies, package managers, or frameworks. Full behavior parity across Java and Python. Clean local verification required.
- Store diagrams exclusively as `.mmd` in `diagrams/`.
- Review consistency using `resources/CONSISTENCY-AUDIT.md` before submitting major revisions.
- Maintain "🔜" markers for in-progress topics until content is complete.

## Portal & GenAI Integration
- New concepts under `03-hld-concepts/` are auto-discovered by the portal; no manual edits to `apps/portal/src/content/registry.ts` are needed when adding a concept.
- Only update `apps/portal/src/content/registry.ts` when changing discovery logic or adding metadata overrides for specific concepts.
- GenAI systems (`06-genai-systems/`) build on many classical HLD concepts (caching → semantic caching, rate limiting → token budgets, etc.). When adding or updating a concept, check whether `06-genai-systems/00-concepts/` should cross-link to it.
- For full end-to-end instructions, see [`resources/CONTRIBUTOR-PLAYBOOK.md`](../resources/CONTRIBUTOR-PLAYBOOK.md).

## Stability Guarantees
- Do not collapse subdirectories into a single file; learners expect dedicated folders per concept.
- Do not rename concept folder names (e.g., `caching/`, `load-balancing/`); the portal, GenAI section, and HLD projects link to them.
- Keep terminology precise (e.g., CAP theorem, replication, sharding) and validate against authoritative sources.
- Note any shared glossary updates in `CONCEPTS.md` when concepts introduce new definitions.
