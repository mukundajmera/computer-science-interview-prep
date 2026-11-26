# AGENTS Guidance — case-studies

## Scope
Covers all materials under `case-studies/`.

## Structure Expectations
- Follow the standard sections (Problem Statement, Architecture Evolution, Key Decisions, Technologies, Trade-offs, Lessons, Interview Relevance).
- Maintain accurate scale metrics (users, QPS, storage) and cite technology choices consistent with concept guides.
- Update `case-studies/README.md` tables whenever adding, renaming, or reprioritizing studies.

## Cross-Linking
- Reference relevant concepts in `03-hld-concepts/` and system templates in `04-hld-projects/`.
- Link diagrams stored in `diagrams/` rather than embedding external images.
- Update `CONCEPTS.md` or study plans when new lessons influence broader guidance.

## Quality Checklist
- Validate internal/external links and ensure tone matches `.github/CONTRIBUTING.md` (interview-focused, instructional).
- Highlight unique insights or pitfalls; ensure lessons remain actionable for interview prep.
- Review using `resources/CONSISTENCY-AUDIT.md` before submitting major additions.

## Portal Integration
- New case studies are auto-discovered by the portal from `case-studies/` (see `apps/portal/src/content/registry.ts`); no manual registry entry is required.
- For full end-to-end instructions, see [`resources/CONTRIBUTOR-PLAYBOOK.md`](../resources/CONTRIBUTOR-PLAYBOOK.md).

## Restrictions
- Documentation only; do not include executable code or proprietary data.
- Preserve directory names (e.g., `twitter-timeline/`) to avoid breaking existing references.
