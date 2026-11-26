# AGENTS Guidance — flashcards

## Scope
Governs flashcard decks and export assets within `flashcards/`.

## Content Standards
- Maintain question-only Markdown decks; do not add answers to primary files.
- Update card counts, descriptions, and difficulty notes in `flashcards/README.md` whenever decks change.
- Align questions with repository topics and cross-link to supporting materials where helpful.

## Exports & Integrations
- Keep `anki-export/` instructions up to date if deck structure changes.
- Avoid committing large binary exports; rely on Markdown sources and documented export steps.

## Quality Checklist
- Verify Markdown tables render correctly.
- Ensure emoji/status markers remain consistent with repository style.
- Double-check numbering and totals after edits.

## GenAI Coverage
- When new GenAI concepts or projects ship in `06-genai-systems/`, consider adding flashcards to cover key GenAI interview questions (RAG, safety, evaluation, model routing).
- Follow the same deck format and update card counts in `flashcards/README.md`.

## Restrictions
- No executable scripts or tooling belongs here.
- Preserve directory layout (`anki-export/`, deck files) to avoid breaking automation or documentation references.
