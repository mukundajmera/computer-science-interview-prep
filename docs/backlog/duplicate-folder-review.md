# Duplicate Folder and Quiz Review

Report for the owner. Nothing was moved, merged, renamed or deleted. Every number below comes from a command run against the repository at the commit where this file was added.

Method: file lists and per-pair diffs from `find`, Markdown line counts from `wc -l`, and cross-references from `grep -rl` over `*.md`, `*.ts`, `*.mjs` and `*.json`, excluding each folder's own files. Question overlap between the quizzes was measured by comparing the first 45 characters of every question stem.

## Pair 1: `bot-detection` vs `bot-detection-platform`

| Signal | `bot-detection` | `bot-detection-platform` |
|---|---|---|
| Total files | 29 | 29 |
| Markdown lines | 760 | 276 |
| Java / Python / test files | 6 / 12 / 9 | 6 / 12 / 9 |
| Mermaid diagrams | 3 | 3 |
| External files linking in | 2 | 10 |

The file lists are identical in shape; the only differences are class and module names carrying the `Platform` suffix. The docs differ in scope: `bot-detection` frames a social-platform abuse problem, while `bot-detection-platform` frames a confidence-aware remediation platform with investigator escalation. `04-hld-projects/README.md` (lines 52-53 and 75-76) already declares these as a deliberate Baseline and Advanced pair.

**Recommendation: keep both.** This is an intentional baseline/advanced pair, not an accident, and the README documents that relationship. The real gap is that the platform pack's docs are about a third of the baseline's depth (276 vs 760 Markdown lines) while drawing ten inbound links against the baseline's two. The follow-up worth scheduling is deepening the platform docs, not merging.

## Pair 2: `content-moderation` vs `content-moderation-platform`

| Signal | `content-moderation` | `content-moderation-platform` |
|---|---|---|
| Total files | 29 | 29 |
| Markdown lines | 745 | 276 |
| Java / Python / test files | 6 / 12 / 9 | 6 / 12 / 9 |
| Mermaid diagrams | 3 | 3 |
| External files linking in | 2 | 6 |

Same shape as pair 1: identical structure, `Platform`-suffixed code, thinner docs on the platform side. The README (lines 50-51 and 75) declares baseline and advanced explicitly. The baseline is a moderation design; the platform is the trust-and-safety variant.

**Recommendation: keep both**, for the same reasons as pair 1. The two packs share scaffolding but teach different decision units (content item vs account-level enforcement). If any action is taken, it is bringing the platform docs up to the baseline's depth, not consolidation.

## Pair 3: `distributed-tracing` vs `distributed-tracing-system`

| Signal | `distributed-tracing` | `distributed-tracing-system` |
|---|---|---|
| Total files | 31 | 9 |
| Markdown lines | 266 | 729 |
| Java / Python / test files | 9 / 12 / 3 | 0 / 0 / 0 |
| Mermaid diagrams | 1 | 0 |
| External files linking in | 2 | 0 |

This pair is inverted compared to the others. `distributed-tracing` holds all of the code, tests, the walkthrough and the diagram, and it is the one indexed in `04-hld-projects/README.md` (line 37). `distributed-tracing-system` is docs-only, is not listed in the README, `CONTENT-MAP.md` or `resources/CONTENT-UI-MAP.md`, and no file outside it links to it. Its own DESIGN.md and COMPARISON.md link back to `distributed-tracing` as the companion pack, so the authors saw them as related.

**Recommendation: merge into `distributed-tracing`.** The system pack's unique assets are `CAPACITY.md` (5M spans/sec sizing) and the storage-engine comparison tables. Two parallel PROBLEM/DESIGN documents on the same system will drift. Fold the capacity and comparison material into the code-bearing pack, add the merged docs to the README index, and redirect or delete the docs-only folder. This is the only pair where consolidation looks right.

## Pair 4: `ai-coding-interview-quiz.md` vs `ai-coding-interviews-quiz.md`

| Signal | `ai-coding-interview-quiz.md` | `ai-coding-interviews-quiz.md` |
|---|---|---|
| Lines | 271 | 214 |
| Questions | 24 | 24 |
| Overlapping question stems | 0 | 0 |
| Indexed in `quizzes/README.md` | yes (lines 41, 595) | yes (lines 42, 596) |
| Answer key / flashcards | yes / 24 | yes / 36 |

Zero of the 24 question stems overlap. The singular-named quiz covers AI-assisted build ownership (planning, prompting, verification, recovery). The plural-named quiz covers interview-format strategy (evaluation dimensions, format, orientation, communication). They are different assessments with names that differ by one letter.

**Recommendation: keep both files, rename one.** The content is complementary and both are wired into the coverage matrix with separate answer keys and flashcards. The problem is only naming: a one-letter difference guarantees mis-links. Renaming the plural one to something like `ai-coding-interview-format-quiz.md` would end the confusion, at the cost of updating its rows in `quizzes/README.md`, `resources/ASSESSMENT-COVERAGE-MATRIX.md` and `CONTENT-MAP.md`. That rename is the owner's call and is left undone here.

## Summary

| Pair | Verdict |
|---|---|
| bot-detection / bot-detection-platform | Keep both; deepen platform docs |
| content-moderation / content-moderation-platform | Keep both; deepen platform docs |
| distributed-tracing / distributed-tracing-system | Merge into `distributed-tracing` |
| ai-coding-interview-quiz / ai-coding-interviews-quiz | Keep both; rename one for clarity |
