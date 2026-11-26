# AGENTS Guidance — resources

## Scope
Applies to study plans, cheatsheets, interview tips, templates, and maintenance guides under `resources/`.

## Structure & Synchronization
- Update `resources/README.md` tables when adding or revising materials.
- Keep study plans aligned with repository content; adjust timelines and references if upstream folders change.
- Templates in `resources/templates/` are canonical—update them before modifying dependent documents.
- Maintenance guides (`CROSS-REFERENCE-GUIDE.md`, `CONSISTENCY-AUDIT.md`) must be kept in sync with actual processes.

## Documentation Standards
- Markdown only; maintain interview-focused tone consistent with `.github/CONTRIBUTING.md`.
- Preserve emoji/status indicators across study plans, checklists, and templates.
- Cross-link to relevant directories (theory, LLD, HLD) to reinforce learning paths.

## QA Workflow
- Run through `CONSISTENCY-AUDIT.md` before submitting broad documentation changes.
- Ensure new resources appear in `CONCEPTS.md` or other indices if applicable.
- Validate links and ensure instructions are actionable (commands, prerequisites, expected outcomes).

## Contributor Playbook
- See [`CONTRIBUTOR-PLAYBOOK.md`](./CONTRIBUTOR-PLAYBOOK.md) for step-by-step recipes on adding content end-to-end (LLD, HLD, GenAI, design patterns) including which index files to touch and the portal workflow / when portal code needs updates.

## Restrictions
- Do not add runtime scripts or binaries.
