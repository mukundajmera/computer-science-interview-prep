# AGENTS Guidance — 00-theory

## Scope
Applies to all content under `00-theory/` and its subdirectories.

## Content Standards
- Author purely in Markdown; do not add executable code or binaries.
- Preserve the existing section hierarchy (emoji headings, tables, navigation indexes) when extending files.
- Use descriptive filenames in `kebab-case.md`; keep multi-file topics grouped within their current folders.
- When adding new fundamentals, update `00-theory/README.md` tables and navigation indices.

## Cross-References
- Link to related practice materials in other top-level folders (e.g., design patterns, LLD projects) using relative paths.
- If new theory impacts quick references, reflect it in `CONCEPTS.md` at repo root.
- Example recently added: [`advanced-hash-tables.md`](./data-structures/advanced-hash-tables.md)
- Example recently added: [`swim-gossip-protocol.md`](./distributed-systems/swim-gossip-protocol.md)

## Quality Checklist
- Verify Markdown renders cleanly (no broken tables or lists).
- Ensure terminology aligns with `.github/CONTRIBUTING.md` tone (interview focused, instructional).
- Keep emoji status markers consistent with surrounding docs.

## Portal & GenAI Integration
- The portal auto-discovers theory articles under `00-theory/` via `apps/portal/src/content/registry.ts`; no manual registry edits are needed when adding new theory topics.
- Only update `apps/portal/src/content/registry.ts` when changing discovery logic or adding a new top-level route/section.
- Theory content underpins the GenAI section (`06-genai-systems/`); if new theory is relevant to GenAI (e.g., vector similarity, embedding spaces), cross-link from `06-genai-systems/00-concepts/` as well.
- For full end-to-end instructions, see [`resources/CONTRIBUTOR-PLAYBOOK.md`](../resources/CONTRIBUTOR-PLAYBOOK.md).

## Stability Guarantees
- Do not move or rename numbered folders (`oop-principles/`, etc.) without owner approval.
- Do not rename existing Markdown filenames; other sections, the portal, and study plans link to them by path.
- Avoid introducing external embeds or HTML; stick to Markdown for portability.
