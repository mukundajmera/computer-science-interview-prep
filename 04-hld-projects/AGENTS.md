# AGENTS Guidance — 04-hld-projects

## Scope
Supports all system design case studies and templates in `04-hld-projects/`.

## Template & Structure
- Every project must follow the standard outline (Problem → Requirements → Capacity → APIs → Data Model → Architecture → Deep Dives → Trade-offs → Q&A).
- Update `DESIGN-TEMPLATE.md` before diverging in individual projects; the template is authoritative for new content.
- Maintain status/difficulty tables in `README.md` when adding or completing projects.

## Content Expectations
- Provide concrete scale metrics (DAU, QPS, storage) and justify technology choices with trade-offs.
- Cross-link to relevant concept guides (`../03-hld-concepts/`) and case studies when referencing shared components.
- Store diagrams as Mermaid `.mmd` files under `diagrams/`; regenerate rendered assets when diagrams change.

## Validation
- A narrowly approved educational simulator exception allows executable code.
  - Approved source paths: `04-hld-projects/<project>/java/` and `04-hld-projects/<project>/python/`.
  - Language/test rules: Java 11+ SE and Python 3.8+ standard libraries only. No external dependencies, package managers, or frameworks. Full behavior parity across Java and Python. Clean local verification required.
- Perform editorial QA:
  - Review with `resources/CONSISTENCY-AUDIT.md` checklists.
  - Verify all internal and external links.
  - Ensure consistency with other sections (e.g., study plans, concept indices).

## Portal & GenAI Integration
- New HLD projects under `04-hld-projects/` are auto-discovered by the portal; no per-project edits to `apps/portal/src/content/registry.ts` are needed. Update the portal code only if you change the folder layout or need new metadata fields surfaced.
- GenAI HLD projects (`06-genai-systems/02-llm-hld-projects/`) follow the same design template; if a new classical HLD project shares patterns with a GenAI project, add cross-links in both directions.
- For full end-to-end instructions, see [`resources/CONTRIBUTOR-PLAYBOOK.md`](../resources/CONTRIBUTOR-PLAYBOOK.md).

## Stability Guarantees
- Retain "🔜 Coming Soon" placeholders until the full project is ready.
- Keep folder names stable (e.g., `url-shortener`, `chat-service`) to avoid breaking cross-references throughout the repo, the portal, and study plans.
- Highlight template changes and diagram regenerations in PR descriptions so downstream contributors are aware.
