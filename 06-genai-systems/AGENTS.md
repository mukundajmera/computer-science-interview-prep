# AGENTS Guidance — 06-genai-systems

## Scope
Applies to all content under `06-genai-systems/`, including GenAI concepts, LLM-focused LLD projects, and GenAI HLD case studies.

## Section Structure
The section is organized into three pillars:

| Subfolder | Purpose | Primary Language |
|-----------|---------|------------------|
| `00-concepts/` | GenAI-specific concepts, patterns, and trade-offs (Markdown) | N/A (docs only) |
| `01-llm-lld-projects/` | Targeted LLD exercises for GenAI components | Python-first |
| `02-llm-hld-projects/` | Full GenAI system designs following the HLD design template | N/A (docs + code) |
| `diagrams/` | Mermaid `.mmd` diagram sources for GenAI architectures | N/A |

## Concepts (`00-concepts/`)
- Each concept gets its own folder (e.g., `rag-architecture/`, `vector-databases/`, `llm-safety/`) with a `README.md`.
- Structure each concept doc with: **📚 Theory**, **🏗️ How It Works**, **⚖️ Trade-offs**, **🎯 When to Use**, **🔗 Cross-links**.
- Cross-link to relevant classical concepts in `03-hld-concepts/` (e.g., caching → semantic caching, rate-limiting → token budgeting). Use paths relative to the file being edited—from a concept README at `00-concepts/<topic>/README.md` the correct path is `../../../03-hld-concepts/...`.
- Cross-link to GenAI HLD projects that use the concept. From a concept README, use `../../02-llm-hld-projects/<project>/`.
- Include diagrams as Mermaid `.mmd` files in `diagrams/`; link via relative paths.
- Maintain status indicators (`✅` complete, `🔜` coming soon) in the subfolder `README.md`.

## LLD Projects (`01-llm-lld-projects/`)
- **Python-first**: GenAI stacks are predominantly Python. Provide Python implementations as the primary language.
- Java implementations are welcome but not required; if provided, maintain parity.
- Each project gets its own folder (e.g., `document-chunker/`, `embedding-service/`, `vector-retriever/`).
- Follow versioned tracks where appropriate: `v1-basic/`, `v2-extended/`, `v3-optimized/`.
- Include `PROBLEM.md` (requirements), code under `python/` (and optionally `java/`), and tests under `python/tests/`.
- Keep components small and realistic—each project should represent a single microcomponent of a larger GenAI system.
- Use only Python standard library; avoid external dependencies unless maintainer-approved.
- Provide type hints, docstrings, and complexity annotations consistent with `.github/CONTRIBUTING.md`.
- Cross-link to the GenAI concepts that the component implements.

## HLD Projects (`02-llm-hld-projects/`)
- Follow the standard outline from `04-hld-projects/DESIGN-TEMPLATE.md` with these GenAI-specific additions:
  - **Model Selection & Routing**: Which LLM(s), why, and how requests are routed.
  - **RAG Pipeline** (if applicable): Ingestion, chunking, embedding, retrieval, reranking.
  - **Safety & Guardrails**: Input/output filtering, hallucination mitigation, toxicity checks.
  - **Evaluation & Observability**: Metrics, feedback loops, A/B testing, red-teaming.
  - **Cost & Latency Analysis**: Token budgets, caching strategies, scaling economics.
- Each project gets its own folder (e.g., `rag-enterprise-search/`, `ai-copilot/`).
- Include `PROBLEM.md`, `DESIGN.md`, `APPROACH.md`, and a `diagrams/` subfolder.
- Cross-link to relevant GenAI concepts and classical HLD concepts. Use paths relative to the file being edited—from a project doc at `02-llm-hld-projects/<project>/DESIGN.md` the correct paths are `../../00-concepts/<topic>/` for GenAI concepts and `../../../03-hld-concepts/...` for classical concepts.
- Store diagrams as Mermaid `.mmd` files in the project's `diagrams/` subfolder.

## Diagrams
- All diagram sources live in `diagrams/` as `.mmd` files.
- Use descriptive filenames (e.g., `rag-pipeline.mmd`, `agent-workflow.mmd`).
- Optionally regenerate companion assets locally using: `npx -p @mermaid-js/mermaid-cli mmdc -i diagrams/<file>.mmd -o diagrams/<file>.svg`.
- Commit only the Mermaid `.mmd` sources; do not check in generated `.svg` files. If you use a custom command, document it in the PR description.

## Cross-Linking Expectations
- Update `06-genai-systems/README.md` status tables whenever content ships.
- When adding GenAI concepts, check whether `CONCEPTS.md` (root) needs a new entry.
- When adding HLD projects, update the root `README.md` progress tracker.
- Link back to classical sections (`03-hld-concepts/`, `04-hld-projects/`, `01-design-patterns/`) wherever GenAI builds on classical patterns.

## Naming Conventions
- Folder names: lowercase, hyphen-separated (e.g., `rag-architecture`, `document-chunker`).
- Python modules: `snake_case` with type hints and docstrings.
- Classes: `PascalCase`; constants: `UPPER_SNAKE_CASE`.
- Follow all conventions from `.github/CONTRIBUTING.md`.

## Testing Practices

### Python Tests
- Use `unittest` (standard library) for all GenAI LLD tests; `pytest` is also acceptable.
- Place tests under `<project>/python/tests/test_<module>.py`.
- Existing tests typically modify `sys.path` at module import time (top of the test file) to point at the target version directory (e.g., `v1-basic/`), and then perform imports inside `setUp()`/tests. Adjusting `sys.path` inside `setUp()` is also acceptable; alternatively, add `__init__.py` files and use relative imports, or configure the test runner's `--rootdir` / `PYTHONPATH` centrally.
- Cover at minimum:
  - **Unit tests** for individual component behaviour (chunker logic, embedding stubs, retrieval ranking).
  - **Edge cases**: empty inputs, oversized documents, malformed prompts, missing metadata.
  - **Error handling**: verify that `ValueError` / `TypeError` are raised for invalid states.
  - **Integration tests**: component pipelines (e.g., chunker → metadata extractor → indexer).
- For GenAI-specific scenarios, add tests that validate:
  - **RAG pipelines**: correct chunk retrieval order, score thresholds, top-k behaviour.
  - **Safety filters**: blocked vs. allowed content, policy rule evaluation.
  - **Evaluation harnesses**: metric computation accuracy, edge-case scoring.
  - **Agent workflows**: tool selection, planning step sequences, memory recall.
- Run tests with: `python -m pytest 06-genai-systems/01-llm-lld-projects/<project>/python/tests -v`
  or: `python -m unittest discover 06-genai-systems/01-llm-lld-projects/<project>/python/tests`.
- Clean up any generated artifacts before committing.

### Java Tests (Optional)
- When Java implementations are provided, follow the same JUnit 5 conventions used in `02-lld-projects/`.
- Place tests under `<project>/java/tests/` and run with the `junit-platform-console-standalone.jar` runner.

## Agent-Based Maintenance Flows

This section documents how to leverage Copilot (or other AI coding agents) to maintain and evolve `06-genai-systems/` over time.

### Generating New LLD Projects
1. **Prompt template** – ask the agent to scaffold a new LLD project:
   ```
   Create a new GenAI LLD project "<project-name>" under
   06-genai-systems/01-llm-lld-projects/<project-name>/ with:
   - PROBLEM.md (requirements, constraints, interview context)
   - APPROACH.md (design decisions, trade-offs)
   - DESIGN.md (component diagram, data flow)
   - python/v1-basic/ (initial implementation with type hints & docstrings)
   - python/tests/test_<module>.py (unittest suite covering core, edge, and error cases)
   Follow conventions in 06-genai-systems/AGENTS.md and .github/CONTRIBUTING.md.
   ```
2. **Review checklist** – after generation, verify:
   - [ ] Folder name is lowercase, hyphen-separated.
   - [ ] Python code uses `snake_case` modules, `PascalCase` classes, type hints, and docstrings.
   - [ ] No external dependencies introduced without maintainer approval.
   - [ ] Cross-links to relevant GenAI concepts (`00-concepts/`) are present.
   - [ ] Tests pass: `python -m pytest <project>/python/tests -v`.
   - [ ] `01-llm-lld-projects/README.md` and `06-genai-systems/README.md` progress tracker updated.

### Generating New HLD Projects
1. **Prompt template** – ask the agent to scaffold a new HLD project:
   ```
   Create a new GenAI HLD project "<project-name>" under
   06-genai-systems/02-llm-hld-projects/<project-name>/ with:
   - PROBLEM.md, DESIGN.md, APPROACH.md
   - diagrams/ subfolder with Mermaid .mmd sources
   Follow the GenAI design template at 02-llm-hld-projects/GENAI-DESIGN-TEMPLATE.md
   and include sections for Model Selection, RAG Pipeline, Safety & Guardrails,
   Evaluation & Observability, and Cost & Latency Analysis.
   ```
2. **Review checklist** – after generation, verify:
   - [ ] All GenAI-specific design sections are present (Model Selection, RAG, Safety, Evaluation, Cost).
   - [ ] Cross-links to GenAI concepts and classical HLD concepts use correct relative paths.
   - [ ] Diagrams are `.mmd` only (no committed `.svg`).
   - [ ] `02-llm-hld-projects/README.md` and `06-genai-systems/README.md` progress tracker updated.
   - [ ] Root `README.md` progress tracker updated if applicable.

### Periodic Refresh of Existing Content
Best practices in GenAI evolve rapidly. Use the following maintenance cadence:

| Cadence | Action | Example |
|---------|--------|---------|
| **Quarterly** | Review concept docs for outdated patterns | Replace deprecated RAG patterns, update safety framework references |
| **Quarterly** | Refresh LLD projects with newer techniques | Add v2/v3 tracks reflecting improved chunking, retrieval, or evaluation strategies |
| **Semi-annually** | Re-evaluate HLD designs against industry trends | Incorporate new model routing strategies, updated cost models, emerging agent patterns |
| **On-demand** | Respond to major framework releases | Update stubs/patterns when significant shifts occur (e.g., new evaluation standards, safety regulations) |

**Refresh workflow:**
1. Open an issue describing which content is outdated and what the new best practice is.
2. Use Copilot to draft updates, referencing the original content and the new approach.
3. Verify cross-links still resolve correctly after the update.
4. Run `resources/CONSISTENCY-AUDIT.md` GenAI checks (see below).
5. Update status indicators (`✅`/`🔜`) in `README.md` files.

## Portal Integration
- The portal automatically discovers GenAI concepts, LLD projects, and HLD projects by scanning the `06-genai-systems/*` directories; no manual registry updates are needed for routine content additions.
- Manual edits to `apps/portal/src/content/registry.ts` are only required when changing discovery logic or adding a new route/section in the portal.
- Content-only edits to existing Markdown files require no portal changes.
- For full end-to-end instructions, see [`resources/CONTRIBUTOR-PLAYBOOK.md`](../resources/CONTRIBUTOR-PLAYBOOK.md).

## Restrictions & Gotchas
- Retain `🔜 Coming Soon` placeholders until content is fully delivered.
- Do not introduce external Python packages (e.g., `langchain`, `openai`) without maintainer approval; use standard library and illustrative stubs.
- Keep folder names stable to avoid breaking cross-references.
- This section is Python-first but not Python-only; maintain Java parity when implementations are provided.
- Coordinate template changes with `04-hld-projects/DESIGN-TEMPLATE.md`; do not diverge silently.
