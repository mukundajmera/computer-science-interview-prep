# Agent task backlog: AT-001 to AT-030 (public repo `mukundajmera/computer-science-interview-prep`)

You are working on the PUBLIC GitHub repo `mukundajmera/computer-science-interview-prep` using your GitHub token. This file is a backlog of 30 small tasks. Each task is one branch and one pull request. Work on **one task per run**.

## How to pick the next task
1. Fetch the latest `main`.
2. Read every task block below. Pick the FIRST task whose `status` is `TODO` and whose `depends_on` tasks (if any) all have a merged PR on `main`. A task whose dependency PR is still open or unmerged is skipped for now; do not stack branches.
3. A task is TAKEN (skip it) if any PR in any state has a head branch starting `agent-task/at-NNN-` (lowercase id) or a body whose first line is `Agent backlog: AT-NNN`. A dependency counts as satisfied only when such a PR is MERGED. A closed-but-unmerged PR counts as taken; mention it in your reply so the human can decide. Status fields in this file are never updated, so always use the PR list, not the `status` line.
4. Other prompts may run in parallel. If your branch has a merge conflict in `resources/CONTENT-UI-MAP.md` or `scripts/`, stop and report instead of resolving it by guessing. Do that one task, open its PR, then stop. Do not edit this backlog file or any status field (the human tracks status). If no task qualifies, reply `NO ELIGIBLE TASK` and the reason.

## Global rules (apply to every task)
- Base branch `main` (fetch it fresh). One branch and one PR per task. Never push to `main`. Never merge, auto-merge, close or approve any PR. Never force-push.
- Touch ONLY the files in the task's "Allowed files". If another file seems to need a change, do not edit it; put it under "Not done / follow-ups" in the PR body. If a required check fails and the failure names a file outside Allowed files, stop the task, open no PR, and report it.
- Python 3.8-safe, standard library only (no `match`, no `X | Y` types at runtime, no `list[str]` at runtime, no `str.removeprefix`). Java 11+, no external libraries. No new dependencies, formatters, linters or build tools.
- Original prose only. Do not copy or closely paraphrase books, courses, paid sites, or other repos. No secrets, tokens, personal data or emails anywhere (files, commits, PR text). Technical facts must be accurate and well known; if you are not sure of a number, leave it out or label it an illustrative estimate with the arithmetic shown.
- Read root `AGENTS.md` and the `AGENTS.md` of every folder you edit before changing files.
- One commit per branch with the exact commit message in the task. No other commits.
- Run the task's checks before opening the PR. Paste real results (pass/fail lines, not invented text) into the PR body. A check you cannot run gets `BLOCKED: <reason>`; never claim a pass you did not see. If a check fails because of your change, fix it (inside Allowed files) and re-run.
- Review rounds: after the work is done, do at least 5 review passes over your own diff (accuracy, scope, links, 3.8-safety, tone, leftover files) and fix what you find. Say in the PR body how many rounds you did and what the last one still changed.
- Never leave generated files behind (`*.class`, `__pycache__`, rendered SVG/PNG, temp output). Build into `/tmp`. Run `git status --short` before committing and confirm only Allowed files are listed.
- PR base `main`, normal (non-draft) PR, no labels. PR body must start with the line `Agent backlog: <ID>` and follow this template exactly:

```
Agent backlog: <ID>

## Summary
<2-3 sentences: what was missing or wrong, what you changed>

## Files changed
<bulleted list, one line per file, why>

## Checks run
<command> -> <PASS/FAIL/BLOCKED + one-line result>
(one line per command)

## Review rounds
<number of rounds, one line on what the last round changed>

## Not done / follow-ups
<anything out of scope you noticed, or "None">
```

- Final reply after the PR is open: one line `<ID> | <branch> | <PR URL> | <PASS/FAIL/BLOCKED summary>`. For a task you stopped, `<ID> | NO PR | <reason>`.

## Shared helper: MMD-CHECK (for tasks that add or edit `.mmd` files)
Save this as `/tmp/mmdcheck.py` (outside the repo, never commit it). It checks each changed `.mmd` starts with a Mermaid diagram keyword and has no Markdown fence lines.

```python
import subprocess
KW = ('graph', 'flowchart', 'sequenceDiagram', 'classDiagram', 'stateDiagram', 'erDiagram', 'gantt', 'pie', 'journey', 'quadrantChart', 'block-beta', 'mindmap', 'timeline', 'gitGraph')
names = subprocess.check_output(['git', 'diff', '--name-only', 'main...HEAD']).decode().split()
bad = 0
for f in [n for n in names if n.endswith('.mmd')]:
    lines = open(f, encoding='utf-8').read().splitlines()
    if lines and lines[0].strip() == '---':
        end = lines[1:].index('---') + 2 if '---' in lines[1:] else 0
        lines = lines[end:]
    body = [l for l in lines if l.strip() and not l.strip().startswith('%%')]
    fenced = any(l.strip().startswith('```') for l in lines)
    ok = bool(body) and body[0].strip().startswith(KW) and not fenced
    print(('ok   ' if ok else 'FAIL ') + f)
    bad += 0 if ok else 1
raise SystemExit(1 if bad else 0)
```

If the Mermaid CLI (`mmdc`) is installed, also render each changed `.mmd` to `/tmp` (`mmdc -i <file> -o /tmp/<name>.svg`) and report the result; if it is not installed write `BLOCKED: mmdc not installed`. Never commit rendered output.

## Task index
| ID | Type | Title |
|---|---|---|
| AT-001 | diagrams | Add Mermaid diagrams to caching, load-balancing, cdn |
| AT-002 | diagrams | Add Mermaid diagrams to dns, rate-limiting, service-discovery |
| AT-003 | diagrams | Add Mermaid diagrams to database-replication, read-scaling, write-scaling |
| AT-004 | diagrams | Add Mermaid diagrams to message-queues, workflow-orchestration, long-running-tasks |
| AT-005 | diagrams | Remove Markdown fences from 9 HLD diagram sources (set A) |
| AT-006 | diagrams | Remove Markdown fences from 9 HLD diagram sources (set B) |
| AT-007 | diagrams | Remove Markdown fences from 6 diagram sources (set C) |
| AT-008 | docs | Add the 5 missing projects to the HLD diagram source matrix |
| AT-009 | checker | Add a checker that validates Mermaid source files |
| AT-010 | checker | Add a per-folder Python test runner |
| AT-011 | portal | Add a custom 404 page to the portal |
| AT-012 | docs | Add INTERVIEW-QA pages to three single-page concept folders |
| AT-013 | diagrams | Add Mermaid diagrams to elasticsearch, time-series-databases, mongodb |
| AT-014 | diagrams | Add Mermaid diagrams to api-design, microservices-communication, real-time-updates |
| AT-015 | docs | Deepen the database indexing theory page |
| AT-016 | docs | Deepen the database data modeling theory page |
| AT-017 | docs | Add Discord message storage case study |
| AT-018 | docs | Add Meta Memcache and TAO case study |
| AT-019 | docs | Add Shopify flash sale case study |
| AT-020 | docs | Add attention variants (MHA, MQA, GQA) concept |
| AT-021 | docs | Add preference alignment (RLHF, PPO, DPO) concept |
| AT-022 | docs | Deepen the chatgpt-inference case study |
| AT-023 | docs | Deepen the github-copilot case study |
| AT-024 | code | Implement v2-extended for the semantic-embedding-cache GenAI LLD project |
| AT-025 | code | Implement v2-extended for the context-window-manager GenAI LLD project |
| AT-026 | code | Implement v2-extended for the token-streaming-server GenAI LLD project |
| AT-027 | code | Implement v2-extended for the ai-safety-guardrails GenAI LLD project |
| AT-028 | code | Implement v2-extended for the vector-store-inverted-index GenAI LLD project |
| AT-029 | code | Implement v2-extended for the streaming-token-aggregator GenAI LLD project |
| AT-030 | code | Implement v2-extended for the speculative-decoding-cache GenAI LLD project |

## Tasks

---

### AT-001: Add Mermaid diagrams to caching, load-balancing, cdn

- id: AT-001
- status: TODO
- type: diagrams
- branch: `agent-task/at-001-concept-diagrams-caching`
- commit message: `docs: add Mermaid diagrams for caching, load-balancing, cdn concepts`
- PR title: `docs: add Mermaid diagrams for caching, load-balancing, cdn`
- depends_on: none
- allowed files:
  - `03-hld-concepts/caching/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/caching/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/load-balancing/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/load-balancing/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/cdn/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/cdn/THEORY.md` (add one diagram section only)

**Goal.** These concept folders have no external `.mmd` diagram source: caching, load-balancing, cdn (some pages already hold inline Mermaid blocks in `THEORY.md`; leave those untouched and choose subjects different from what they already show). Add one accurate Mermaid diagram per concept (two if the concept clearly has two distinct flows) under that folder's new `diagrams/` subfolder, with names like `<mechanism>.mmd`. Suggested subjects: caching: cache-aside read path and write-through/write-back comparison; load-balancing: L4 vs L7 routing decision flow; cdn: cache purge and invalidation propagation sequence (cdn already has inline request-flow diagrams). Read the concept's `THEORY.md` first and draw only what the page already teaches; diagrams must be technically correct and use plain labels. In each `THEORY.md` add one short section titled `## 📊 Diagrams` near the end (before Related/References if those exist) that explains in 1-2 sentences what each diagram shows and links to it with a relative path such as `./diagrams/<name>.mmd`. Do not paste Mermaid into the Markdown and do not change any other text. Follow `03-hld-concepts/AGENTS.md` (diagrams only as `.mmd`); where it mentions `diagrams/components` or `diagrams/patterns`, the per-concept `diagrams/` folder used by `03-hld-concepts/redis/` is the rule for this task.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. python3 /tmp/mmdcheck.py   (MMD-CHECK from the header, run after the commit)
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
3. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-002: Add Mermaid diagrams to dns, rate-limiting, service-discovery

- id: AT-002
- status: TODO
- type: diagrams
- branch: `agent-task/at-002-concept-diagrams-dns`
- commit message: `docs: add Mermaid diagrams for dns, rate-limiting, service-discovery concepts`
- PR title: `docs: add Mermaid diagrams for dns, rate-limiting, service-discovery`
- depends_on: none
- allowed files:
  - `03-hld-concepts/dns/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/dns/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/rate-limiting/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/rate-limiting/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/service-discovery/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/service-discovery/THEORY.md` (add one diagram section only)

**Goal.** These concept folders have no external `.mmd` diagram source: dns, rate-limiting, service-discovery (some pages already hold inline Mermaid blocks in `THEORY.md`; leave those untouched and choose subjects different from what they already show). Add one accurate Mermaid diagram per concept (two if the concept clearly has two distinct flows) under that folder's new `diagrams/` subfolder, with names like `<mechanism>.mmd`. Suggested subjects: dns: recursive resolution sequence with caching layers; rate-limiting: token bucket vs sliding window decision flow; service-discovery: client-side vs server-side discovery with a registry and health checks. Read the concept's `THEORY.md` first and draw only what the page already teaches; diagrams must be technically correct and use plain labels. In each `THEORY.md` add one short section titled `## 📊 Diagrams` near the end (before Related/References if those exist) that explains in 1-2 sentences what each diagram shows and links to it with a relative path such as `./diagrams/<name>.mmd`. Do not paste Mermaid into the Markdown and do not change any other text. Follow `03-hld-concepts/AGENTS.md` (diagrams only as `.mmd`); where it mentions `diagrams/components` or `diagrams/patterns`, the per-concept `diagrams/` folder used by `03-hld-concepts/redis/` is the rule for this task.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. python3 /tmp/mmdcheck.py   (MMD-CHECK from the header, run after the commit)
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
3. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-003: Add Mermaid diagrams to database-replication, read-scaling, write-scaling

- id: AT-003
- status: TODO
- type: diagrams
- branch: `agent-task/at-003-concept-diagrams-database-replication`
- commit message: `docs: add Mermaid diagrams for database-replication, read-scaling, write-scaling concepts`
- PR title: `docs: add Mermaid diagrams for database-replication, read-scaling, write-scaling`
- depends_on: none
- allowed files:
  - `03-hld-concepts/database-replication/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/database-replication/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/read-scaling/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/read-scaling/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/write-scaling/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/write-scaling/THEORY.md` (add one diagram section only)

**Goal.** These concept folders have no external `.mmd` diagram source: database-replication, read-scaling, write-scaling (some pages already hold inline Mermaid blocks in `THEORY.md`; leave those untouched and choose subjects different from what they already show). Add one accurate Mermaid diagram per concept (two if the concept clearly has two distinct flows) under that folder's new `diagrams/` subfolder, with names like `<mechanism>.mmd`. Suggested subjects: database-replication: leader-follower write and replication-lag read path; read-scaling: read-after-write consistency routing decision flow; write-scaling: hot-key detection and shard-split decision flow (these pages already hold inline diagrams of the basic paths). Read the concept's `THEORY.md` first and draw only what the page already teaches; diagrams must be technically correct and use plain labels. In each `THEORY.md` add one short section titled `## 📊 Diagrams` near the end (before Related/References if those exist) that explains in 1-2 sentences what each diagram shows and links to it with a relative path such as `./diagrams/<name>.mmd`. Do not paste Mermaid into the Markdown and do not change any other text. Follow `03-hld-concepts/AGENTS.md` (diagrams only as `.mmd`); where it mentions `diagrams/components` or `diagrams/patterns`, the per-concept `diagrams/` folder used by `03-hld-concepts/redis/` is the rule for this task.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. python3 /tmp/mmdcheck.py   (MMD-CHECK from the header, run after the commit)
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
3. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-004: Add Mermaid diagrams to message-queues, workflow-orchestration, long-running-tasks

- id: AT-004
- status: TODO
- type: diagrams
- branch: `agent-task/at-004-concept-diagrams-message-queues`
- commit message: `docs: add Mermaid diagrams for message-queues, workflow-orchestration, long-running-tasks concepts`
- PR title: `docs: add Mermaid diagrams for message-queues, workflow-orchestration, long-running-tasks`
- depends_on: none
- allowed files:
  - `03-hld-concepts/message-queues/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/message-queues/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/workflow-orchestration/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/workflow-orchestration/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/long-running-tasks/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/long-running-tasks/THEORY.md` (add one diagram section only)

**Goal.** These concept folders have no external `.mmd` diagram source: message-queues, workflow-orchestration, long-running-tasks (some pages already hold inline Mermaid blocks in `THEORY.md`; leave those untouched and choose subjects different from what they already show). Add one accurate Mermaid diagram per concept (two if the concept clearly has two distinct flows) under that folder's new `diagrams/` subfolder, with names like `<mechanism>.mmd`. Suggested subjects: message-queues: producer, broker, consumer group with ack/retry/dead-letter flow; workflow-orchestration: state machine of a workflow run with retry and compensation; long-running-tasks: submit, poll or callback, worker lifecycle. Read the concept's `THEORY.md` first and draw only what the page already teaches; diagrams must be technically correct and use plain labels. In each `THEORY.md` add one short section titled `## 📊 Diagrams` near the end (before Related/References if those exist) that explains in 1-2 sentences what each diagram shows and links to it with a relative path such as `./diagrams/<name>.mmd`. Do not paste Mermaid into the Markdown and do not change any other text. Follow `03-hld-concepts/AGENTS.md` (diagrams only as `.mmd`); where it mentions `diagrams/components` or `diagrams/patterns`, the per-concept `diagrams/` folder used by `03-hld-concepts/redis/` is the rule for this task.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. python3 /tmp/mmdcheck.py   (MMD-CHECK from the header, run after the commit)
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
3. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-005: Remove Markdown fences from 9 HLD diagram sources (set A)

- id: AT-005
- status: TODO
- type: diagrams
- branch: `agent-task/at-005-fix-fenced-mmd-ecommerce-file-storage-news-feed`
- commit message: `fix: remove Markdown fences from ecommerce-backend, file-storage and news-feed .mmd sources`
- PR title: `fix: strip Markdown fences from ecommerce-backend, file-storage and news-feed diagrams`
- depends_on: none
- allowed files:
  - `04-hld-projects/ecommerce-backend/diagrams/architecture.mmd`
  - `04-hld-projects/ecommerce-backend/diagrams/database.mmd`
  - `04-hld-projects/ecommerce-backend/diagrams/sequence.mmd`
  - `04-hld-projects/file-storage/diagrams/architecture.mmd`
  - `04-hld-projects/file-storage/diagrams/database.mmd`
  - `04-hld-projects/file-storage/diagrams/sequence.mmd`
  - `04-hld-projects/news-feed/diagrams/architecture.mmd`
  - `04-hld-projects/news-feed/diagrams/database.mmd`
  - `04-hld-projects/news-feed/diagrams/sequence.mmd`

**Goal.** These `.mmd` files wrongly contain a Markdown code fence (a first line of ```` ```mermaid ```` and a closing ```` ``` ````), so they are not valid Mermaid sources and will not render with `mmdc`. Remove only the fence lines so each file starts directly with its diagram keyword (for example `erDiagram`, `sequenceDiagram`, `graph TD`). Change nothing else: no diagram edits, no whitespace cleanup, no renames. If a file has text after the closing fence, stop that file and report it.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. python3 /tmp/mmdcheck.py   (MMD-CHECK from the header, run after the commit)
2. `git diff --stat main...HEAD`  (each file shows 2 deleted lines and nothing added; confirm in the PR body)
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`

---

### AT-006: Remove Markdown fences from 9 HLD diagram sources (set B)

- id: AT-006
- status: TODO
- type: diagrams
- branch: `agent-task/at-006-fix-fenced-mmd-notification-ride-url`
- commit message: `fix: remove Markdown fences from notification-service, ride-sharing and url-shortener .mmd sources`
- PR title: `fix: strip Markdown fences from notification-service, ride-sharing and url-shortener diagrams`
- depends_on: none
- allowed files:
  - `04-hld-projects/notification-service/diagrams/architecture.mmd`
  - `04-hld-projects/notification-service/diagrams/database.mmd`
  - `04-hld-projects/notification-service/diagrams/sequence.mmd`
  - `04-hld-projects/ride-sharing/diagrams/architecture.mmd`
  - `04-hld-projects/ride-sharing/diagrams/database.mmd`
  - `04-hld-projects/ride-sharing/diagrams/sequence.mmd`
  - `04-hld-projects/url-shortener/diagrams/architecture.mmd`
  - `04-hld-projects/url-shortener/diagrams/database.mmd`
  - `04-hld-projects/url-shortener/diagrams/sequence.mmd`

**Goal.** These `.mmd` files wrongly contain a Markdown code fence (a first line of ```` ```mermaid ```` and a closing ```` ``` ````), so they are not valid Mermaid sources and will not render with `mmdc`. Remove only the fence lines so each file starts directly with its diagram keyword (for example `erDiagram`, `sequenceDiagram`, `graph TD`). Change nothing else: no diagram edits, no whitespace cleanup, no renames. If a file has text after the closing fence, stop that file and report it.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. python3 /tmp/mmdcheck.py   (MMD-CHECK from the header, run after the commit)
2. `git diff --stat main...HEAD`  (each file shows 2 deleted lines and nothing added; confirm in the PR body)
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`

---

### AT-007: Remove Markdown fences from 6 diagram sources (set C)

- id: AT-007
- status: TODO
- type: diagrams
- branch: `agent-task/at-007-fix-fenced-mmd-video-streaming-semantic-retrieval`
- commit message: `fix: remove Markdown fences from video-streaming and semantic-retrieval-platform .mmd sources`
- PR title: `fix: strip Markdown fences from video-streaming and semantic-retrieval-platform diagrams`
- depends_on: none
- allowed files:
  - `04-hld-projects/video-streaming/diagrams/architecture.mmd`
  - `04-hld-projects/video-streaming/diagrams/database.mmd`
  - `04-hld-projects/video-streaming/diagrams/sequence.mmd`
  - `06-genai-systems/02-llm-hld-projects/semantic-retrieval-platform/diagrams/acl-filtering.mmd`
  - `06-genai-systems/02-llm-hld-projects/semantic-retrieval-platform/diagrams/cdc-freshness.mmd`
  - `06-genai-systems/02-llm-hld-projects/semantic-retrieval-platform/diagrams/multi-tenant-index.mmd`

**Goal.** These `.mmd` files wrongly contain a Markdown code fence (a first line of ```` ```mermaid ```` and a closing ```` ``` ````), so they are not valid Mermaid sources and will not render with `mmdc`. Remove only the fence lines so each file starts directly with its diagram keyword (for example `erDiagram`, `sequenceDiagram`, `graph TD`). Change nothing else: no diagram edits, no whitespace cleanup, no renames. If a file has text after the closing fence, stop that file and report it. The three `semantic-retrieval-platform` files also use CRLF line endings; convert them to LF in the same edit (`git diff --stat` will then show whole-file changes for those three, which is expected; say so in the PR body).

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. python3 /tmp/mmdcheck.py   (MMD-CHECK from the header, run after the commit)
2. `git diff --stat main...HEAD`  (each file shows 2 deleted lines and nothing added; confirm in the PR body; the three semantic-retrieval-platform files are exempt because of the CRLF-to-LF conversion)
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`

---

### AT-008: Add the 5 missing projects to the HLD diagram source matrix

- id: AT-008
- status: TODO
- type: docs
- branch: `agent-task/at-008-hld-diagram-matrix-sync`
- commit message: `docs: add missing projects to the HLD diagram source matrix`
- PR title: `docs: sync HLD diagram source matrix with all 04-hld-projects folders`
- depends_on: none
- allowed files:
  - `04-hld-projects/hld-diagram-source-matrix.md`

**Goal.** `04-hld-projects/hld-diagram-source-matrix.md` has no row for `distributed-lock`, `distributed-tracing-system`, `key-value-store`, `typeahead-autocomplete` and `unique-id-generator`. For every folder under `04-hld-projects/` (except `tools/`) confirm there is a row; add the missing rows in the exact column format of the neighbouring rows and alphabetical position. For each new row count real inline Mermaid blocks in that project's `DESIGN.md` (lines starting with ```` ```mermaid ````) and real `.mmd` files under the project folder or `diagrams/04-hld-projects/<project>/`, then classify using the legend in the file (do not guess; use the counts). Update the `Current Summary` table and project lists in that file so they include the new rows. Do NOT reclassify or recount pre-existing rows (some are known to be stale, for example rows marked `inline-only` that now have `.mmd` files); instead list every stale row you notice under Not done in the PR body. Do not edit any DESIGN.md or diagram. If the matrix file changed on `main` since you started, re-fetch and redo the rows.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
2. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
3. `for d in 04-hld-projects/*/; do n=$(basename $d); [ "$n" = tools ] || grep -q "/$n/" 04-hld-projects/hld-diagram-source-matrix.md || echo "MISSING $n"; done`  (must print nothing)
4. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-009: Add a checker that validates Mermaid source files

- id: AT-009
- status: TODO
- type: checker
- branch: `agent-task/at-009-mermaid-source-checker`
- commit message: `feat: add check_mermaid_sources.py to validate tracked .mmd files`
- PR title: `feat: add a Mermaid source checker for tracked .mmd files`
- depends_on: none
- allowed files:
  - `scripts/check_mermaid_sources.py` (new)
  - `scripts/tests/test_check_mermaid_sources.py` (new)

**Goal.** Nothing guards the 279 tracked `.mmd` files. On main, 27 of them start with a Markdown fence (invalid Mermaid; 24 are fixed by AT-005 to AT-007, 3 under `voice-assistant` by a separate prompt), 42 use CRLF line endings, and several are 2-3 line stubs. Add `scripts/check_mermaid_sources.py`, standard library only, Python 3.8-safe, in the style of the other `scripts/check_*.py` files (a `main(argv=None)` returning an int, optional `--root <dir>` defaulting to the current directory used as cwd for `git ls-files '*.mmd'`, `if __name__ == "__main__": sys.exit(main())`). Read files as bytes or with `newline=''` (default text mode hides ``) and decode as UTF-8. Report one `path:line: kind: message` line per finding and exit 1 if any, else print `mermaid-sources: ok` plus the file count. Finding kinds: `fenced` (any line starting with three backticks; a fenced file is reported as `fenced` only, not also as `no-diagram-keyword`), `empty` (no content apart from blank and `%%` comment lines), `no-diagram-keyword` (first content line, after skipping blank lines, `%%` comments and an optional `---` front-matter block, does not start with a known Mermaid diagram keyword), `crlf` (file contains CRLF). Do NOT register it in `scripts/check_repo_smoke.py` and do not edit any workflow: on current main it correctly fails and the findings are fixed elsewhere or by the owner. Add `scripts/tests/test_check_mermaid_sources.py` (unittest) with a temp git repo (`git init`, `git add` inside a temp dir, pass via `--root`) covering: a valid file passes; a fenced file is reported with line 1; an empty file; a file with an unknown first keyword; a CRLF file; a repo with no `.mmd` files passes; front-matter plus valid keyword passes. In the PR body list the finding counts per kind the script reports on current main (do not assume numbers; paste what it prints).

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest scripts.tests.test_check_mermaid_sources -v`
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover scripts/tests`
3. `python3 -B scripts/check_mermaid_sources.py | tail -5`  (expected to exit 1 on current main; paste the tail and the per-kind counts)
4. `python3 -c "import ast;[ast.parse(open(f,encoding='utf-8').read(),feature_version=(3,8)) for f in ('scripts/check_mermaid_sources.py','scripts/tests/test_check_mermaid_sources.py')]"`
5. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_tracked_secret_artifacts.py`
6. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-010: Add a per-folder Python test runner

- id: AT-010
- status: TODO
- type: checker
- branch: `agent-task/at-010-isolated-python-test-runner`
- commit message: `feat: add run_python_tests.py to run each Python tests folder in isolation`
- PR title: `feat: add an isolated per-folder Python test runner`
- depends_on: none
- allowed files:
  - `scripts/run_python_tests.py` (new)
  - `scripts/tests/test_run_python_tests.py` (new)

**Goal.** Running pytest once over several project folders fails with module-name collisions: `python3 -m pytest 06-genai-systems/01-llm-lld-projects -q -x` stops with `ModuleNotFoundError: No module named 'tests.test_chunker'`, because many projects use a package or folder literally called `tests`. Add `scripts/run_python_tests.py` (standard library only, Python 3.8-safe, `main(argv=None)` returning an int, `--root <dir>` default current directory). It finds tracked test files with `git ls-files 'test_*.py' '**/test_*.py'`; the unit to run for each file is its path up to and including the first ancestor folder named `tests` if there is one, otherwise its parent folder (de-duplicate units; pytest recurses into subfolders such as `tests/v1-basic`). It runs each unit in its own subprocess with cwd = repo root: `python3 -m pytest -p no:cacheprovider <folder> -q` if pytest is importable, otherwise `python3 -m unittest discover <folder>`. Print one `PASS <folder>` or `FAIL <folder>` line each plus a final summary, and exit 1 if any folder failed. Options: `--list` (print folders, run nothing), `--only <substring>` (repeatable), `--timeout <seconds>` per folder (default 120; a timeout counts as FAIL). Set `PYTHONDONTWRITEBYTECODE=1` in the child environment. Do not register it in `scripts/check_repo_smoke.py`, do not fix any failing project, and do not edit existing tests. First confirm no existing script already runs all Python test folders in isolation (`scripts/check_repo_smoke.py` names only two folders; that hit is expected). If a script that discovers all of them exists, stop and report. The unittest file builds a temp git repo with two tiny test folders (one passing, one failing) and checks `--list`, `--only`, exit codes and the PASS/FAIL lines. In the PR body paste the summary of a full run on main (failures are allowed and expected; do not hide them).

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest scripts.tests.test_run_python_tests -v`
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover scripts/tests`
3. `python3 -B scripts/run_python_tests.py --list | wc -l`
4. `python3 -B scripts/run_python_tests.py --only tic-tac-toe`  (must print PASS)
5. `python3 -c "import ast;[ast.parse(open(f,encoding='utf-8').read(),feature_version=(3,8)) for f in ('scripts/run_python_tests.py','scripts/tests/test_run_python_tests.py')]"`
6. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_tracked_secret_artifacts.py`
7. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-011: Add a custom 404 page to the portal

- id: AT-011
- status: TODO
- type: portal
- branch: `agent-task/at-011-portal-not-found-page`
- commit message: `feat(portal): add a not-found page with navigation back to study sections`
- PR title: `feat(portal): add a custom 404 not-found page`
- depends_on: none
- allowed files:
  - `apps/portal/src/app/not-found.tsx` (new)
  - `apps/portal/tests/not-found-contract.test.mjs` (new)

**Goal.** The portal has `layout.tsx` but no `not-found.tsx`, so a bad URL on the static site shows the framework default. Read `apps/portal/AGENTS.md`, `src/app/layout.tsx`, `src/lib/sections.ts`, `site-config.mjs` and `scripts/check-static-export.mjs` first. Add `src/app/not-found.tsx` as a server component (no `use client`) in the existing Tailwind style, with a short heading, one sentence, and links built from `PORTAL_SECTIONS` in `src/lib/sections.ts` (do not hard-code routes) including the `/start` entry, plus one home link whose literal `/` is the only hard-coded route allowed; use the same `Link` import pattern as other pages so the GitHub Pages base path keeps working. No new dependencies. Add `tests/not-found-contract.test.mjs` using only `node:test`, `node:assert` and `node:fs` (it must NOT import `typescript`, so it runs without `npm ci`): assert the file exists, has a default export function, has no `use client`, imports `PORTAL_SECTIONS`, and contains no hard-coded `href="/theory` style string. Do not edit any other portal file or the export checker.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `node --test apps/portal/tests/not-found-contract.test.mjs`
2. `npm --prefix apps/portal ci`  (BLOCKED if there is no network)
3. `npm --prefix apps/portal run lint`  (BLOCKED if the previous step was)
4. `npm --prefix apps/portal run test`  (BLOCKED if ci was; otherwise all tests must pass)
5. `npm --prefix apps/portal run build`  (BLOCKED if ci was; if it runs, also run `npm --prefix apps/portal run check:export`)
6. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-012: Add INTERVIEW-QA pages to three single-page concept folders

- id: AT-012
- status: TODO
- type: docs
- branch: `agent-task/at-012-orphan-concept-interview-qa`
- commit message: `docs: add interview Q&A for mlops, observability and resilience concept folders`
- PR title: `docs: add INTERVIEW-QA.md to the mlops, observability and resilience concept folders`
- depends_on: none
- allowed files:
  - `03-hld-concepts/mlops/INTERVIEW-QA.md` (new)
  - `03-hld-concepts/observability/INTERVIEW-QA.md` (new)
  - `03-hld-concepts/resilience/INTERVIEW-QA.md` (new)

**Goal.** Three concept folders hold only a few pages and no interview Q&A: `mlops/` (`feature-store-architecture.md`, `model-inference-serving.md`), `observability/` (`distributed-tracing-opentelemetry.md`), `resilience/` (`cascading-failure-defense.md`). Do not rename, move or merge any folder. Read each existing page, then write one `INTERVIEW-QA.md` per folder in the shape of `03-hld-concepts/redis/INTERVIEW-QA.md` (read it first): 8 to 10 questions, each with a strong 3-6 sentence answer that names concrete trade-offs and, where useful, a follow-up probe. Questions must be answerable from the folder's own pages plus standard knowledge; link back to those pages with relative links. Original prose, no invented statistics. Adding these files must not change any inventory count (verify with the inventory check). Known limitation: the portal marks a concept complete only when both `THEORY.md` and `INTERVIEW-QA.md` exist, so these folders stay coming-soon in the portal; do not add a THEORY.md, and mention this under Not done.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
2. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `for f in 03-hld-concepts/mlops 03-hld-concepts/observability 03-hld-concepts/resilience; do echo "$f $(grep -c '^### ' $f/INTERVIEW-QA.md)"; done`  (each at least 8; use `### ` for each question heading)
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-013: Add Mermaid diagrams to elasticsearch, time-series-databases, mongodb

- id: AT-013
- status: TODO
- type: diagrams
- branch: `agent-task/at-013-concept-diagrams-elasticsearch`
- commit message: `docs: add Mermaid diagrams for elasticsearch, time-series-databases, mongodb concepts`
- PR title: `docs: add Mermaid diagrams for elasticsearch, time-series-databases, mongodb`
- depends_on: none
- allowed files:
  - `03-hld-concepts/elasticsearch/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/elasticsearch/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/time-series-databases/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/time-series-databases/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/mongodb/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/mongodb/THEORY.md` (add one diagram section only)

**Goal.** These concept folders have no external `.mmd` diagram source: elasticsearch, time-series-databases, mongodb (some pages already hold inline Mermaid blocks in `THEORY.md`; leave those untouched and choose subjects different from what they already show). Add one accurate Mermaid diagram per concept (two if the concept clearly has two distinct flows) under that folder's new `diagrams/` subfolder, with names like `<mechanism>.mmd`. Suggested subjects: elasticsearch: indexing and search scatter-gather path across shards; time-series-databases: write path from ingest buffer to compressed blocks and downsampling; mongodb: replica set election and write-concern acknowledgement flow. Read the concept's `THEORY.md` first and draw only what the page already teaches; diagrams must be technically correct and use plain labels. In each `THEORY.md` add one short section titled `## 📊 Diagrams` near the end (before Related/References if those exist) that explains in 1-2 sentences what each diagram shows and links to it with a relative path such as `./diagrams/<name>.mmd`. Do not paste Mermaid into the Markdown and do not change any other text. Follow `03-hld-concepts/AGENTS.md` (diagrams only as `.mmd`); where it mentions `diagrams/components` or `diagrams/patterns`, the per-concept `diagrams/` folder used by `03-hld-concepts/redis/` is the rule for this task.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. python3 /tmp/mmdcheck.py   (MMD-CHECK from the header, run after the commit)
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
3. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-014: Add Mermaid diagrams to api-design, microservices-communication, real-time-updates

- id: AT-014
- status: TODO
- type: diagrams
- branch: `agent-task/at-014-concept-diagrams-api-design`
- commit message: `docs: add Mermaid diagrams for api-design, microservices-communication, real-time-updates concepts`
- PR title: `docs: add Mermaid diagrams for api-design, microservices-communication, real-time-updates`
- depends_on: none
- allowed files:
  - `03-hld-concepts/api-design/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/api-design/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/microservices-communication/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/microservices-communication/THEORY.md` (add one diagram section only)
  - `03-hld-concepts/real-time-updates/diagrams/*.mmd` (new, 1-2 files)
  - `03-hld-concepts/real-time-updates/THEORY.md` (add one diagram section only)

**Goal.** These concept folders have no external `.mmd` diagram source: api-design, microservices-communication, real-time-updates (some pages already hold inline Mermaid blocks in `THEORY.md`; leave those untouched and choose subjects different from what they already show). Add one accurate Mermaid diagram per concept (two if the concept clearly has two distinct flows) under that folder's new `diagrams/` subfolder, with names like `<mechanism>.mmd`. Suggested subjects: api-design: versioning and pagination decision flow; microservices-communication: sync request versus async event flow with a timeout and retry; real-time-updates: polling, SSE and WebSocket selection flow. Read the concept's `THEORY.md` first and draw only what the page already teaches; diagrams must be technically correct and use plain labels. In each `THEORY.md` add one short section titled `## 📊 Diagrams` near the end (before Related/References if those exist) that explains in 1-2 sentences what each diagram shows and links to it with a relative path such as `./diagrams/<name>.mmd`. Do not paste Mermaid into the Markdown and do not change any other text. Follow `03-hld-concepts/AGENTS.md` (diagrams only as `.mmd`); where it mentions `diagrams/components` or `diagrams/patterns`, the per-concept `diagrams/` folder used by `03-hld-concepts/redis/` is the rule for this task.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. python3 /tmp/mmdcheck.py   (MMD-CHECK from the header, run after the commit)
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
3. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-015: Deepen the database indexing theory page

- id: AT-015
- status: TODO
- type: docs
- branch: `agent-task/at-015-theory-deepen-indexing`
- commit message: `docs: deepen the database indexing theory page`
- PR title: `docs: expand 00-theory database-concepts/indexing.md`
- depends_on: none
- allowed files:
  - `00-theory/database-concepts/indexing.md`

**Goal.** `00-theory/database-concepts/indexing.md` is only about 480 words, thin next to sibling theory pages (800-1000+ words). Read it and its neighbours in `00-theory/database-concepts/` and `00-theory/AGENTS.md`. Keep the existing headings and correct content and add depth rather than rewriting. Deepen it to roughly 1100-1400 words: how a B-tree index is searched and updated (page splits, write amplification), covering and partial indexes, composite-index column order with a worked example of the leftmost-prefix rule, index selectivity, why an index can be ignored by the planner, hash/GIN/GiST/bitmap families at a conceptual level, LSM versus B-tree trade-offs, and an index-design checklist for an interview. Use tables where they help, follow the emoji heading style of sibling pages only if the existing page already uses it, keep the existing `Related Topics` links working, and add 2 or 3 new relative links to pages that exist. No code blocks of executable code. Standard, well-known facts only; no invented numbers.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
2. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `wc -w 00-theory/database-concepts/indexing.md`  (between 1000 and 1500)
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-016: Deepen the database data modeling theory page

- id: AT-016
- status: TODO
- type: docs
- branch: `agent-task/at-016-theory-deepen-data-modeling`
- commit message: `docs: deepen the database data modeling theory page`
- PR title: `docs: expand 00-theory database-concepts/data-modeling.md`
- depends_on: none
- allowed files:
  - `00-theory/database-concepts/data-modeling.md`

**Goal.** `00-theory/database-concepts/data-modeling.md` is only about 484 words, thin next to sibling theory pages (800-1000+ words). Read it and its neighbours in `00-theory/database-concepts/` and `00-theory/AGENTS.md`. Keep the existing headings and correct content and add depth rather than rewriting. Deepen it to roughly 1100-1400 words: entity-relationship thinking, when to normalize and when to denormalize with a worked example, modelling one-to-many and many-to-many, schema evolution and migrations, modelling for access patterns in a document or wide-column store, keys (natural, surrogate, composite), soft deletes and audit history, and an interview checklist. Use tables where they help, follow the emoji heading style of sibling pages only if the existing page already uses it, keep the existing `Related Topics` links working, and add 2 or 3 new relative links to pages that exist. No code blocks of executable code. Standard, well-known facts only; no invented numbers.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
2. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `wc -w 00-theory/database-concepts/data-modeling.md`  (between 1000 and 1500)
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-017: Add Discord message storage case study

- id: AT-017
- status: TODO
- type: docs
- branch: `agent-task/at-017-case-study-discord-messaging-storage`
- commit message: `docs: add discord messaging storage case study`
- PR title: `docs: add discord-messaging-storage case study`
- depends_on: none
- allowed files:
  - `case-studies/discord-messaging-storage/README.md` (new)
  - `case-studies/README.md`
  - `resources/CONTENT-UI-MAP.md` (Case Studies count only)

**Goal.** Write a case study on how a very large chat service stores trillions of messages: partitioning by channel and time bucket, hot partitions and large-channel problems, the move from Cassandra to ScyllaDB as publicly described by the company, request coalescing in a data-services layer, and what the migration teaches about operations (compaction, GC pauses, repair). Read `case-studies/AGENTS.md` and `case-studies/stripe-ledger-engine/README.md` (shape and depth) first; where the section list in `case-studies/AGENTS.md` differs from the one below, use `AGENTS.md`'s sections and add the others. Create `case-studies/discord-messaging-storage/README.md` with: context and scale, architecture, the key design decisions with the alternatives that were rejected, failure modes and how the system handles them, a `### Scale Metrics` heading (the case-studies README links to `#scale-metrics`), trade-offs table, what to say in an interview (4 questions with strong answers), and a `Sources` section naming the public papers or engineering posts the facts come from (title, publisher, year; no copied text). Only state numbers that are widely published and tie each to a named source; otherwise describe magnitudes qualitatively or as a labelled estimate with arithmetic. Add one row to the table in `case-studies/README.md` (and one to the Pack-to-Case-Study matrix only if a listed HLD project clearly maps to it), and bump the Case Studies count by one in `resources/CONTENT-UI-MAP.md` (exactly the two table rows that state the Case Studies count, currently `15` -> `16`; change nothing else in that file). Target 300-450 lines.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
3. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
4. `wc -l case-studies/discord-messaging-storage/README.md`  (300 or more)
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-018: Add Meta Memcache and TAO case study

- id: AT-018
- status: TODO
- type: docs
- branch: `agent-task/at-018-case-study-meta-memcache-tao`
- commit message: `docs: add meta memcache tao case study`
- PR title: `docs: add meta-memcache-tao case study`
- depends_on: AT-017
- allowed files:
  - `case-studies/meta-memcache-tao/README.md` (new)
  - `case-studies/README.md`
  - `resources/CONTENT-UI-MAP.md` (Case Studies count only)

**Goal.** Write a case study on how a social network serves a read-heavy social graph: the memcache tier (look-aside caching, leases against thundering herds and stale sets, regional pools, cross-region invalidation) and the TAO graph store (objects and associations, write-through cache tiers, leader and follower caches, consistency trade-offs), based on the public papers. Read `case-studies/AGENTS.md` and `case-studies/stripe-ledger-engine/README.md` (shape and depth) first; where the section list in `case-studies/AGENTS.md` differs from the one below, use `AGENTS.md`'s sections and add the others. Create `case-studies/meta-memcache-tao/README.md` with: context and scale, architecture, the key design decisions with the alternatives that were rejected, failure modes and how the system handles them, a `### Scale Metrics` heading (the case-studies README links to `#scale-metrics`), trade-offs table, what to say in an interview (4 questions with strong answers), and a `Sources` section naming the public papers or engineering posts the facts come from (title, publisher, year; no copied text). Only state numbers that are widely published and tie each to a named source; otherwise describe magnitudes qualitatively or as a labelled estimate with arithmetic. Add one row to the table in `case-studies/README.md` (and one to the Pack-to-Case-Study matrix only if a listed HLD project clearly maps to it), and bump the Case Studies count by one in `resources/CONTENT-UI-MAP.md` (exactly the two table rows that state the Case Studies count, currently `16` -> `17`; change nothing else in that file). Target 300-450 lines.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
3. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
4. `wc -l case-studies/meta-memcache-tao/README.md`  (300 or more)
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-019: Add Shopify flash sale case study

- id: AT-019
- status: TODO
- type: docs
- branch: `agent-task/at-019-case-study-shopify-flash-sale`
- commit message: `docs: add shopify flash sale case study`
- PR title: `docs: add shopify-flash-sale case study`
- depends_on: AT-018
- allowed files:
  - `case-studies/shopify-flash-sale/README.md` (new)
  - `case-studies/README.md`
  - `resources/CONTENT-UI-MAP.md` (Case Studies count only)

**Goal.** Write a case study on how a multi-tenant commerce platform survives a flash sale: pod-based isolation of tenants, load shedding and queues, a virtual waiting room or checkout throttling, inventory contention handling, caching strategy for storefronts and graceful degradation, based on public engineering write-ups. Keep claims to what the company has published; avoid exact traffic figures you cannot attribute. Read `case-studies/AGENTS.md` and `case-studies/stripe-ledger-engine/README.md` (shape and depth) first; where the section list in `case-studies/AGENTS.md` differs from the one below, use `AGENTS.md`'s sections and add the others. Create `case-studies/shopify-flash-sale/README.md` with: context and scale, architecture, the key design decisions with the alternatives that were rejected, failure modes and how the system handles them, a `### Scale Metrics` heading (the case-studies README links to `#scale-metrics`), trade-offs table, what to say in an interview (4 questions with strong answers), and a `Sources` section naming the public papers or engineering posts the facts come from (title, publisher, year; no copied text). Only state numbers that are widely published and tie each to a named source; otherwise describe magnitudes qualitatively or as a labelled estimate with arithmetic. Add one row to the table in `case-studies/README.md` (and one to the Pack-to-Case-Study matrix only if a listed HLD project clearly maps to it), and bump the Case Studies count by one in `resources/CONTENT-UI-MAP.md` (exactly the two table rows that state the Case Studies count, currently `17` -> `18`; change nothing else in that file). Target 300-450 lines.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
3. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
4. `wc -l case-studies/shopify-flash-sale/README.md`  (300 or more)
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-020: Add attention variants (MHA, MQA, GQA) concept

- id: AT-020
- status: TODO
- type: docs
- branch: `agent-task/at-020-genai-concept-attention-variants-gqa-mqa`
- commit message: `docs: add attention-variants-gqa-mqa GenAI concept`
- PR title: `docs: add attention-variants-gqa-mqa GenAI concept deep dive`
- depends_on: AT-019
- allowed files:
  - `06-genai-systems/00-concepts/attention-variants-gqa-mqa/README.md` (new)
  - `06-genai-systems/00-concepts/attention-variants-gqa-mqa/INTERVIEW-QA.md` (new)
  - `06-genai-systems/00-concepts/README.md`
  - `resources/CONTENT-UI-MAP.md` (GenAI Concepts count only)

**Goal.** Explain multi-head, multi-query and grouped-query attention: what is shared, KV-cache size per token for each variant (formula plus a worked example with stated layer, head and dimension numbers), quality versus memory trade-off, and why inference serving cares. Cross-link `streaming-kv-cache` and `inference-serving`. Read `06-genai-systems/AGENTS.md`, `resources/templates/genai-concept-template.md` and one finished concept folder (`06-genai-systems/00-concepts/inference-serving/`) first. Create `06-genai-systems/00-concepts/attention-variants-gqa-mqa/README.md` and `INTERVIEW-QA.md` (8 or more strong Q&A) following the template headings. Facts must be standard and checkable; show formulas with a worked numeric example and state assumptions. No executable code. Add one row for the concept to the Concept Index table in `06-genai-systems/00-concepts/README.md`, and bump the GenAI Concepts count by one in `resources/CONTENT-UI-MAP.md` (exactly the two table rows that state it, currently `18` -> `19`; change nothing else there). Link at least two related existing concept folders with relative links.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
3. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
4. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-021: Add preference alignment (RLHF, PPO, DPO) concept

- id: AT-021
- status: TODO
- type: docs
- branch: `agent-task/at-021-genai-concept-dpo-preference-optimization`
- commit message: `docs: add dpo-preference-optimization GenAI concept`
- PR title: `docs: add dpo-preference-optimization GenAI concept deep dive`
- depends_on: AT-020
- allowed files:
  - `06-genai-systems/00-concepts/dpo-preference-optimization/README.md` (new)
  - `06-genai-systems/00-concepts/dpo-preference-optimization/INTERVIEW-QA.md` (new)
  - `06-genai-systems/00-concepts/README.md`
  - `resources/CONTENT-UI-MAP.md` (GenAI Concepts count only)

**Goal.** Explain the alignment stage after supervised fine-tuning: reward modelling from preference pairs, PPO-based RLHF at a conceptual level, and Direct Preference Optimization (the idea that the policy and a frozen reference model replace the explicit reward model, with the loss written out and each term explained), plus data needs, failure modes (reward hacking, over-optimization) and when to choose which. Cross-link `fine-tuning-and-adaptation` and `model-adaptation-lora`. Read `06-genai-systems/AGENTS.md`, `resources/templates/genai-concept-template.md` and one finished concept folder (`06-genai-systems/00-concepts/inference-serving/`) first. Create `06-genai-systems/00-concepts/dpo-preference-optimization/README.md` and `INTERVIEW-QA.md` (8 or more strong Q&A) following the template headings. Facts must be standard and checkable; show formulas with a worked numeric example and state assumptions. No executable code. Add one row for the concept to the Concept Index table in `06-genai-systems/00-concepts/README.md`, and bump the GenAI Concepts count by one in `resources/CONTENT-UI-MAP.md` (exactly the two table rows that state it, currently `19` -> `20`; change nothing else there). Link at least two related existing concept folders with relative links.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
2. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
3. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
4. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-022: Deepen the chatgpt-inference case study

- id: AT-022
- status: TODO
- type: docs
- branch: `agent-task/at-022-case-study-expand-chatgpt-inference`
- commit message: `docs: deepen the chatgpt-inference case study`
- PR title: `docs: expand the chatgpt-inference case study`
- depends_on: none
- allowed files:
  - `case-studies/chatgpt-inference/README.md`

**Goal.** `case-studies/chatgpt-inference/README.md` is 189 lines while mature studies run about 480. Deepen it to roughly 400 lines without padding: request lifecycle from API to token stream, batching and scheduling, KV-cache memory pressure, load balancing and queueing, capacity reasoning with a worked estimate (assumptions stated, labelled illustrative), failure and degradation modes, cost levers, and interview Q&A. Keep existing correct content and structure (including the existing `Scale Metrics` heading); add sections rather than rewriting. Original prose only; add a `Sources` section naming public posts or papers (title, publisher, year).

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
2. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `wc -l case-studies/chatgpt-inference/README.md`  (between 380 and 460)
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-023: Deepen the github-copilot case study

- id: AT-023
- status: TODO
- type: docs
- branch: `agent-task/at-023-case-study-expand-github-copilot`
- commit message: `docs: deepen the github-copilot case study`
- PR title: `docs: expand the github-copilot case study`
- depends_on: none
- allowed files:
  - `case-studies/github-copilot/README.md`

**Goal.** `case-studies/github-copilot/README.md` is 179 lines while mature studies run about 480. Deepen it to roughly 400 lines without padding: editor-to-service request path, context assembly from open files and neighbours, latency budget for inline completions (debounce, cancellation, streaming), caching and model routing, telemetry and acceptance-rate feedback, security and privacy controls (filtering, secret handling), failure modes, trade-offs and interview Q&A. Only state facts that GitHub or its model providers have published publicly; label estimates. Keep existing correct content; add sections rather than rewriting. Original prose only; add a `Sources` section naming public posts or papers (title, publisher, year).

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_markdown_links.py`
2. `git diff --name-only main...HEAD -- '*.md' | xargs -r python3 -B scripts/check_readability_style.py   (run after the commit; the default scope of this checker is a fixed file list and would skip your files)`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `wc -l case-studies/github-copilot/README.md`  (between 380 and 460)
5. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-024: Implement v2-extended for the semantic-embedding-cache GenAI LLD project

- id: AT-024
- status: TODO
- type: code
- branch: `agent-task/at-024-genai-lld-semantic-embedding-cache-v2`
- commit message: `feat: add v2-extended Python track for semantic-embedding-cache`
- PR title: `feat: add v2-extended Python implementation for semantic-embedding-cache`
- depends_on: none
- allowed files:
  - `06-genai-systems/01-llm-lld-projects/semantic-embedding-cache/python/v2-extended/*.py` (new, filenames ending `_v2.py`, plus `__init__.py` if the retriever-ranker pattern uses one)
  - `06-genai-systems/01-llm-lld-projects/semantic-embedding-cache/python/tests/test_*_v2.py` (new)

**Goal.** `semantic-embedding-cache` (a cache that stores embeddings and answers near-duplicate queries by similarity) has only `python/v1-basic/`; the AGENTS rule is v1-basic, v2-extended, v3-optimized. Read the project's `PROBLEM.md`, `DESIGN.md`, `FOLLOW-UPS.md` and `PITFALLS.md` and the v1 code and tests. Implement `python/v2-extended/` as a real step up that addresses the weaknesses those docs already name (for example thread or async safety, eviction or expiry, configurable policies, metrics hooks, input validation); pick 2 or 3 improvements, keep the v1 public API names where sensible, do not copy v1 unchanged, and give every v2 module a DISTINCTIVE filename ending in `_v2` (for example `<v1_module>_v2.py`) so it never collides with the v1 module of the same name when both are imported in one pytest run; follow the pattern in `06-genai-systems/01-llm-lld-projects/retriever-ranker/python/` (`v2-extended/` plus `tests/test_<module>_v2.py`), and explain the chosen improvements in a module docstring. Python 3.8-safe, standard library only, type hints, docstrings on public classes. Add `python/tests/test_<module>_v2.py` matching the style already used by that project's tests (pytest functions or unittest, whichever the existing test file uses) and its `sys.path` handling with at least 8 tests that fail if the v2-specific behaviour is removed, plus tests for edge cases. Do not modify v1 files, existing tests, or any Markdown.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -p no:cacheprovider 06-genai-systems/01-llm-lld-projects/semantic-embedding-cache/python/tests -q`  (v1 and v2 tests all pass; the output must show N passed with N greater than 0 and include the new v2 tests; if pytest is missing, say BLOCKED rather than using a fallback that may run zero tests)
2. `python3 -c "import ast,glob;[ast.parse(open(f,encoding='utf-8').read(),feature_version=(3,8)) for f in glob.glob('06-genai-systems/01-llm-lld-projects/semantic-embedding-cache/python/**/*.py',recursive=True)]"`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_tracked_secret_artifacts.py`
5. `git status --short`  (no `__pycache__` or other leftovers)
6. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-025: Implement v2-extended for the context-window-manager GenAI LLD project

- id: AT-025
- status: TODO
- type: code
- branch: `agent-task/at-025-genai-lld-context-window-manager-v2`
- commit message: `feat: add v2-extended Python track for context-window-manager`
- PR title: `feat: add v2-extended Python implementation for context-window-manager`
- depends_on: none
- allowed files:
  - `06-genai-systems/01-llm-lld-projects/context-window-manager/python/v2-extended/*.py` (new, filenames ending `_v2.py`, plus `__init__.py` if the retriever-ranker pattern uses one)
  - `06-genai-systems/01-llm-lld-projects/context-window-manager/python/tests/test_*_v2.py` (new)

**Goal.** `context-window-manager` (priority-based context compaction under a token budget) has only `python/v1-basic/`; the AGENTS rule is v1-basic, v2-extended, v3-optimized. Read the project's `PROBLEM.md`, `DESIGN.md`, `FOLLOW-UPS.md` and `PITFALLS.md` and the v1 code and tests. Implement `python/v2-extended/` as a real step up that addresses the weaknesses those docs already name (for example thread or async safety, eviction or expiry, configurable policies, metrics hooks, input validation); pick 2 or 3 improvements, keep the v1 public API names where sensible, do not copy v1 unchanged, and give every v2 module a DISTINCTIVE filename ending in `_v2` (for example `<v1_module>_v2.py`) so it never collides with the v1 module of the same name when both are imported in one pytest run; follow the pattern in `06-genai-systems/01-llm-lld-projects/retriever-ranker/python/` (`v2-extended/` plus `tests/test_<module>_v2.py`), and explain the chosen improvements in a module docstring. Python 3.8-safe, standard library only, type hints, docstrings on public classes. Add `python/tests/test_<module>_v2.py` matching the style already used by that project's tests (pytest functions or unittest, whichever the existing test file uses) and its `sys.path` handling with at least 8 tests that fail if the v2-specific behaviour is removed, plus tests for edge cases. Do not modify v1 files, existing tests, or any Markdown.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -p no:cacheprovider 06-genai-systems/01-llm-lld-projects/context-window-manager/python/tests -q`  (v1 and v2 tests all pass; the output must show N passed with N greater than 0 and include the new v2 tests; if pytest is missing, say BLOCKED rather than using a fallback that may run zero tests)
2. `python3 -c "import ast,glob;[ast.parse(open(f,encoding='utf-8').read(),feature_version=(3,8)) for f in glob.glob('06-genai-systems/01-llm-lld-projects/context-window-manager/python/**/*.py',recursive=True)]"`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_tracked_secret_artifacts.py`
5. `git status --short`  (no `__pycache__` or other leftovers)
6. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-026: Implement v2-extended for the token-streaming-server GenAI LLD project

- id: AT-026
- status: TODO
- type: code
- branch: `agent-task/at-026-genai-lld-token-streaming-server-v2`
- commit message: `feat: add v2-extended Python track for token-streaming-server`
- PR title: `feat: add v2-extended Python implementation for token-streaming-server`
- depends_on: none
- allowed files:
  - `06-genai-systems/01-llm-lld-projects/token-streaming-server/python/v2-extended/*.py` (new, filenames ending `_v2.py`, plus `__init__.py` if the retriever-ranker pattern uses one)
  - `06-genai-systems/01-llm-lld-projects/token-streaming-server/python/tests/test_*_v2.py` (new)

**Goal.** `token-streaming-server` (streaming tokens to clients with backpressure) has only `python/v1-basic/`; the AGENTS rule is v1-basic, v2-extended, v3-optimized. Read the project's `PROBLEM.md`, `DESIGN.md`, `FOLLOW-UPS.md` and `PITFALLS.md` and the v1 code and tests. Implement `python/v2-extended/` as a real step up that addresses the weaknesses those docs already name (for example thread or async safety, eviction or expiry, configurable policies, metrics hooks, input validation); pick 2 or 3 improvements, keep the v1 public API names where sensible, do not copy v1 unchanged, and give every v2 module a DISTINCTIVE filename ending in `_v2` (for example `<v1_module>_v2.py`) so it never collides with the v1 module of the same name when both are imported in one pytest run; follow the pattern in `06-genai-systems/01-llm-lld-projects/retriever-ranker/python/` (`v2-extended/` plus `tests/test_<module>_v2.py`), and explain the chosen improvements in a module docstring. Python 3.8-safe, standard library only, type hints, docstrings on public classes. Add `python/tests/test_<module>_v2.py` matching the style already used by that project's tests (pytest functions or unittest, whichever the existing test file uses) and its `sys.path` handling with at least 8 tests that fail if the v2-specific behaviour is removed, plus tests for edge cases. Do not modify v1 files, existing tests, or any Markdown.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -p no:cacheprovider 06-genai-systems/01-llm-lld-projects/token-streaming-server/python/tests -q`  (v1 and v2 tests all pass; the output must show N passed with N greater than 0 and include the new v2 tests; if pytest is missing, say BLOCKED rather than using a fallback that may run zero tests)
2. `python3 -c "import ast,glob;[ast.parse(open(f,encoding='utf-8').read(),feature_version=(3,8)) for f in glob.glob('06-genai-systems/01-llm-lld-projects/token-streaming-server/python/**/*.py',recursive=True)]"`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_tracked_secret_artifacts.py`
5. `git status --short`  (no `__pycache__` or other leftovers)
6. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-027: Implement v2-extended for the ai-safety-guardrails GenAI LLD project

- id: AT-027
- status: TODO
- type: code
- branch: `agent-task/at-027-genai-lld-ai-safety-guardrails-v2`
- commit message: `feat: add v2-extended Python track for ai-safety-guardrails`
- PR title: `feat: add v2-extended Python implementation for ai-safety-guardrails`
- depends_on: none
- allowed files:
  - `06-genai-systems/01-llm-lld-projects/ai-safety-guardrails/python/v2-extended/*.py` (new, filenames ending `_v2.py`, plus `__init__.py` if the retriever-ranker pattern uses one)
  - `06-genai-systems/01-llm-lld-projects/ai-safety-guardrails/python/tests/test_*_v2.py` (new)

**Goal.** `ai-safety-guardrails` (layered input and output safety checks) has only `python/v1-basic/`; the AGENTS rule is v1-basic, v2-extended, v3-optimized. Read the project's `PROBLEM.md`, `DESIGN.md`, `FOLLOW-UPS.md` and `PITFALLS.md` and the v1 code and tests. Implement `python/v2-extended/` as a real step up that addresses the weaknesses those docs already name (for example thread or async safety, eviction or expiry, configurable policies, metrics hooks, input validation); pick 2 or 3 improvements, keep the v1 public API names where sensible, do not copy v1 unchanged, and give every v2 module a DISTINCTIVE filename ending in `_v2` (for example `<v1_module>_v2.py`) so it never collides with the v1 module of the same name when both are imported in one pytest run; follow the pattern in `06-genai-systems/01-llm-lld-projects/retriever-ranker/python/` (`v2-extended/` plus `tests/test_<module>_v2.py`), and explain the chosen improvements in a module docstring. Python 3.8-safe, standard library only, type hints, docstrings on public classes. Add `python/tests/test_<module>_v2.py` matching the style already used by that project's tests (pytest functions or unittest, whichever the existing test file uses) and its `sys.path` handling with at least 8 tests that fail if the v2-specific behaviour is removed, plus tests for edge cases. Do not modify v1 files, existing tests, or any Markdown.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -p no:cacheprovider 06-genai-systems/01-llm-lld-projects/ai-safety-guardrails/python/tests -q`  (v1 and v2 tests all pass; the output must show N passed with N greater than 0 and include the new v2 tests; if pytest is missing, say BLOCKED rather than using a fallback that may run zero tests)
2. `python3 -c "import ast,glob;[ast.parse(open(f,encoding='utf-8').read(),feature_version=(3,8)) for f in glob.glob('06-genai-systems/01-llm-lld-projects/ai-safety-guardrails/python/**/*.py',recursive=True)]"`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_tracked_secret_artifacts.py`
5. `git status --short`  (no `__pycache__` or other leftovers)
6. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-028: Implement v2-extended for the vector-store-inverted-index GenAI LLD project

- id: AT-028
- status: TODO
- type: code
- branch: `agent-task/at-028-genai-lld-vector-store-inverted-index-v2`
- commit message: `feat: add v2-extended Python track for vector-store-inverted-index`
- PR title: `feat: add v2-extended Python implementation for vector-store-inverted-index`
- depends_on: none
- allowed files:
  - `06-genai-systems/01-llm-lld-projects/vector-store-inverted-index/python/v2-extended/*.py` (new, filenames ending `_v2.py`, plus `__init__.py` if the retriever-ranker pattern uses one)
  - `06-genai-systems/01-llm-lld-projects/vector-store-inverted-index/python/tests/test_*_v2.py` (new)

**Goal.** `vector-store-inverted-index` (a vector store combined with an inverted index) has only `python/v1-basic/`; the AGENTS rule is v1-basic, v2-extended, v3-optimized. Read the project's `PROBLEM.md`, `DESIGN.md`, `FOLLOW-UPS.md` and `PITFALLS.md` and the v1 code and tests. Implement `python/v2-extended/` as a real step up that addresses the weaknesses those docs already name (for example thread or async safety, eviction or expiry, configurable policies, metrics hooks, input validation); pick 2 or 3 improvements, keep the v1 public API names where sensible, do not copy v1 unchanged, and give every v2 module a DISTINCTIVE filename ending in `_v2` (for example `<v1_module>_v2.py`) so it never collides with the v1 module of the same name when both are imported in one pytest run; follow the pattern in `06-genai-systems/01-llm-lld-projects/retriever-ranker/python/` (`v2-extended/` plus `tests/test_<module>_v2.py`), and explain the chosen improvements in a module docstring. Python 3.8-safe, standard library only, type hints, docstrings on public classes. Add `python/tests/test_<module>_v2.py` matching the style already used by that project's tests (pytest functions or unittest, whichever the existing test file uses) and its `sys.path` handling with at least 8 tests that fail if the v2-specific behaviour is removed, plus tests for edge cases. Do not modify v1 files, existing tests, or any Markdown.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -p no:cacheprovider 06-genai-systems/01-llm-lld-projects/vector-store-inverted-index/python/tests -q`  (v1 and v2 tests all pass; the output must show N passed with N greater than 0 and include the new v2 tests; if pytest is missing, say BLOCKED rather than using a fallback that may run zero tests)
2. `python3 -c "import ast,glob;[ast.parse(open(f,encoding='utf-8').read(),feature_version=(3,8)) for f in glob.glob('06-genai-systems/01-llm-lld-projects/vector-store-inverted-index/python/**/*.py',recursive=True)]"`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_tracked_secret_artifacts.py`
5. `git status --short`  (no `__pycache__` or other leftovers)
6. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-029: Implement v2-extended for the streaming-token-aggregator GenAI LLD project

- id: AT-029
- status: TODO
- type: code
- branch: `agent-task/at-029-genai-lld-streaming-token-aggregator-v2`
- commit message: `feat: add v2-extended Python track for streaming-token-aggregator`
- PR title: `feat: add v2-extended Python implementation for streaming-token-aggregator`
- depends_on: none
- allowed files:
  - `06-genai-systems/01-llm-lld-projects/streaming-token-aggregator/python/v2-extended/*.py` (new, filenames ending `_v2.py`, plus `__init__.py` if the retriever-ranker pattern uses one)
  - `06-genai-systems/01-llm-lld-projects/streaming-token-aggregator/python/tests/test_*_v2.py` (new)

**Goal.** `streaming-token-aggregator` (aggregating a token stream into chunks and events) has only `python/v1-basic/`; the AGENTS rule is v1-basic, v2-extended, v3-optimized. Read the project's `PROBLEM.md`, `DESIGN.md`, `FOLLOW-UPS.md` and `PITFALLS.md` and the v1 code and tests. Implement `python/v2-extended/` as a real step up that addresses the weaknesses those docs already name (for example thread or async safety, eviction or expiry, configurable policies, metrics hooks, input validation); pick 2 or 3 improvements, keep the v1 public API names where sensible, do not copy v1 unchanged, and give every v2 module a DISTINCTIVE filename ending in `_v2` (for example `<v1_module>_v2.py`) so it never collides with the v1 module of the same name when both are imported in one pytest run; follow the pattern in `06-genai-systems/01-llm-lld-projects/retriever-ranker/python/` (`v2-extended/` plus `tests/test_<module>_v2.py`), and explain the chosen improvements in a module docstring. Python 3.8-safe, standard library only, type hints, docstrings on public classes. Add `python/tests/test_<module>_v2.py` matching the style already used by that project's tests (pytest functions or unittest, whichever the existing test file uses) and its `sys.path` handling with at least 8 tests that fail if the v2-specific behaviour is removed, plus tests for edge cases. Do not modify v1 files, existing tests, or any Markdown.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -p no:cacheprovider 06-genai-systems/01-llm-lld-projects/streaming-token-aggregator/python/tests -q`  (v1 and v2 tests all pass; the output must show N passed with N greater than 0 and include the new v2 tests; if pytest is missing, say BLOCKED rather than using a fallback that may run zero tests)
2. `python3 -c "import ast,glob;[ast.parse(open(f,encoding='utf-8').read(),feature_version=(3,8)) for f in glob.glob('06-genai-systems/01-llm-lld-projects/streaming-token-aggregator/python/**/*.py',recursive=True)]"`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_tracked_secret_artifacts.py`
5. `git status --short`  (no `__pycache__` or other leftovers)
6. git diff --stat main...HEAD   (must list only the Allowed files)

---

### AT-030: Implement v2-extended for the speculative-decoding-cache GenAI LLD project

- id: AT-030
- status: TODO
- type: code
- branch: `agent-task/at-030-genai-lld-speculative-decoding-cache-v2`
- commit message: `feat: add v2-extended Python track for speculative-decoding-cache`
- PR title: `feat: add v2-extended Python implementation for speculative-decoding-cache`
- depends_on: none
- allowed files:
  - `06-genai-systems/01-llm-lld-projects/speculative-decoding-cache/python/v2-extended/*.py` (new, filenames ending `_v2.py`, plus `__init__.py` if the retriever-ranker pattern uses one)
  - `06-genai-systems/01-llm-lld-projects/speculative-decoding-cache/python/tests/test_*_v2.py` (new)

**Goal.** `speculative-decoding-cache` (caching draft-and-verify speculative decoding results) has only `python/v1-basic/`; the AGENTS rule is v1-basic, v2-extended, v3-optimized. Read the project's `PROBLEM.md`, `DESIGN.md`, `FOLLOW-UPS.md` and `PITFALLS.md` and the v1 code and tests. Implement `python/v2-extended/` as a real step up that addresses the weaknesses those docs already name (for example thread or async safety, eviction or expiry, configurable policies, metrics hooks, input validation); pick 2 or 3 improvements, keep the v1 public API names where sensible, do not copy v1 unchanged, and give every v2 module a DISTINCTIVE filename ending in `_v2` (for example `<v1_module>_v2.py`) so it never collides with the v1 module of the same name when both are imported in one pytest run; follow the pattern in `06-genai-systems/01-llm-lld-projects/retriever-ranker/python/` (`v2-extended/` plus `tests/test_<module>_v2.py`), and explain the chosen improvements in a module docstring. Python 3.8-safe, standard library only, type hints, docstrings on public classes. Add `python/tests/test_<module>_v2.py` matching the style already used by that project's tests (pytest functions or unittest, whichever the existing test file uses) and its `sys.path` handling with at least 8 tests that fail if the v2-specific behaviour is removed, plus tests for edge cases. Do not modify v1 files, existing tests, or any Markdown.

**Acceptance checks** (run from the repo root; paste real results into the PR body):
1. `PYTHONDONTWRITEBYTECODE=1 python3 -B -m pytest -p no:cacheprovider 06-genai-systems/01-llm-lld-projects/speculative-decoding-cache/python/tests -q`  (v1 and v2 tests all pass; the output must show N passed with N greater than 0 and include the new v2 tests; if pytest is missing, say BLOCKED rather than using a fallback that may run zero tests)
2. `python3 -c "import ast,glob;[ast.parse(open(f,encoding='utf-8').read(),feature_version=(3,8)) for f in glob.glob('06-genai-systems/01-llm-lld-projects/speculative-decoding-cache/python/**/*.py',recursive=True)]"`
3. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_content_inventory.py`
4. `PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/check_tracked_secret_artifacts.py`
5. `git status --short`  (no `__pycache__` or other leftovers)
6. git diff --stat main...HEAD   (must list only the Allowed files)
