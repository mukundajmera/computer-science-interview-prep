# AGENTS Guidance — 02-lld-projects

## Scope
Covers all low-level design projects under `02-lld-projects/`.

## Repository Intent
Deliver interview-ready LLD exercises with progressive solutions in Java and Python.

## Directory Structure Expectations
- Each project directory must include:
  - `PROBLEM.md`, `APPROACH.md`, `DESIGN.md`, and `CODE-WALKTHROUGH.md` where provided.
  - `java/` and `python/` folders, each containing versioned subdirectories (`v1-basic`, `v2-extended`, `v3-optimized` or existing equivalents) plus a `tests/` folder.
- Preserve numbering and naming consistent with the root `README.md` difficulty matrix.

## Coding Standards
- Follow `.github/CONTRIBUTING.md` for language conventions.
- Keep Java and Python implementations functionally aligned; document any intentional divergence in project docs.
- Reset singletons or static caches between tests using provided helpers (`resetInstance`, etc.).
- Avoid introducing external dependencies—solutions must rely on standard libraries.

## Testing
- **Java:** compile relevant sources (`javac project/java/v#/../*.java`) and execute tests via `java -jar junit-platform-console-standalone.jar --scan-classpath --classpath project/java`.
- **Python:** run `python -m pytest project/python/tests -v` or fallback `python -m unittest discover project/python/tests`.
- Ensure tests target the correct version folders; many rely on explicit classpath/sys.path manipulation.

## Documentation & Templates
- Maintain the v1→v2→v3 narrative in project docs; update tables and difficulty classifications when adding or promoting projects.
- Treat `HOW-TO-APPROACH.md` as canonical for practice steps; adjust only after verifying downstream references.
- Cross-link to design pattern implementations and relevant theory sections to reinforce learning flow.

## Portal & GenAI Integration
- New LLD projects are auto-discovered by the portal from `02-lld-projects/`; no manual registry entry in `apps/portal/src/content/registry.ts` is required. Optionally update the `DIFFICULTY` map in `registry.ts` if you need a non-default difficulty.
- Some LLD patterns (e.g., rate limiter, caching) have GenAI counterparts in `06-genai-systems/01-llm-lld-projects/`. Cross-link where relevant.
- For full end-to-end instructions, see [`resources/CONTRIBUTOR-PLAYBOOK.md`](../resources/CONTRIBUTOR-PLAYBOOK.md).

## Stability Guarantees
- Do not rename version folders (`v1-basic/`, `v2-extended/`, `v3-optimized/`); stable paths are required for tests and documentation.
- Do not rename project folder names (e.g., `parking-lot/`, `elevator-system/`); the portal, cross-references, and study plans link to them.
- Demo entry points (`*Demo.*`) must still compile/run after changes.
- Keep project README summaries synchronized with repository-level trackers (`CONCEPTS.md`, study plans).
