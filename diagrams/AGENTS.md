# AGENTS Guidance — diagrams

## Scope
Applies to Mermaid diagram sources within `diagrams/`.

## Standards
- Organize diagrams under existing folders (`components/`, `patterns/creational`, `patterns/structural`, `patterns/behavioral`).
- Name files descriptively to match related documentation (`observer.mmd`, `api-gateway.mmd`).
- Keep diagrams synchronized with textual descriptions; update both when content changes.

## Rendering Workflow
- Mermaid `.mmd` source files are the canonical committed diagram artifacts.
- Validate syntax locally with Mermaid preview or CLI before committing when tooling is available.
- Render temporary assets with Mermaid CLI, e.g., `mmdc -i input.mmd -o /tmp/output.svg`.
- Do not commit generated SVG/PNG files unless the task explicitly asks for an export artifact.

## Quality Checklist
- Maintain consistent styling (direction, labels, stereotypes) across diagrams.
- Ensure diagrams remain legible and reflect accurate relationships.
- Avoid duplicating diagrams; reuse shared components where possible via references.

## GenAI Diagrams
- GenAI architecture diagrams (RAG pipelines, agent workflows, etc.) also live in `06-genai-systems/diagrams/` and per-project `diagrams/` subfolders, as established by `06-genai-systems/AGENTS.md`.
- Shared or cross-cutting diagrams that are referenced from multiple sections should live in this top-level `diagrams/` folder.
- When a GenAI diagram is referenced from both classical and GenAI sections, store it here and link from both locations to avoid duplication.

## Restrictions
- Do not store generated SVG/PNG outputs by default; keep rendered assets in `/tmp` for validation or attach them outside the repository when needed.
- Keep diagrams version-controlled; avoid embedding them directly inside Markdown via base64 or external URLs.
