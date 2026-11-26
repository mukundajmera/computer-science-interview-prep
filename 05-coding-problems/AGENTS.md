# AGENTS Guidance — 05-coding-problems

## Scope
Applies to algorithm pattern documentation under `05-coding-problems/`.

## Content Standards
- Maintain the pattern overview tables with status indicators (`🔜 Coming Soon`) until sections are complete.
- When adding patterns, provide problem descriptions, key techniques, and interview relevance aligned with repository tone.
- Cross-link to implementations or related materials (LLD projects, HLD systems) if they showcase the algorithm.
- 100% original prose is required.
- Original problem statements and constraints must be used (do not copy).

## Documentation Workflow
- Markdown-only content; avoid embedding code unless it is illustrative and language-agnostic.
- Update `README.md` pattern listings and progress checklists whenever new material ships.
- Coordinate with study plans if new algorithm paths affect recommended learning sequences.

## Coding Problem Bank Exception
- Executable code for pattern layouts is allowed. 
- Python and Java solution files are allowed under problem directories.
- Executable Java and Python solution code is allowed under `05-coding-problems/problem-bank/` only.
- Each `verified` or `reviewed` problem must keep Java and Python parity, use the same driver signature defined in `problem.json`, cap solution tiers at five, and pass generated driver execution for available local toolchains; when Java is blocked by a missing JDK, generated Java driver source validation plus the blocker must be reported.
- Each completed problem must include clean-room provenance plus a `cleanRoomReview` receipt before it can be treated as reviewed.
- Collection pages must reference canonical problem IDs instead of duplicating problem or solution content.
- Source-derived content is metadata-only: titles, slugs, IDs, difficulty labels, source URLs, collection order, and paid/free flags. Do not copy external problem statements, examples, constraints, editorials, diagrams, screenshots, or paid-only material.

## Restrictions & Gotchas
- Preserve naming conventions (e.g., `two-pointers`, `sliding-window`) and keep sections modular for future expansion.
- Note dependencies on upstream concepts (e.g., complexity analysis) when referencing earlier folders.
