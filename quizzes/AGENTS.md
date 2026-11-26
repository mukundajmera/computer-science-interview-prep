# AGENTS Guidance — quizzes

## Scope
Applies to quiz content in `quizzes/` and answer keys in `quizzes/answers/`.

## Structure Requirements
- Keep quiz files (`*-quiz.md`) focused on question lists; maintain matching answer files in `answers/`.
- Update `quizzes/README.md` tables (question counts, difficulty, coverage) whenever quizzes change.
- Ensure language and topics align with current repository content.

## Maintenance Workflow
- Synchronize quizzes and answer keys when modifying questions.
- Validate Markdown formatting (lists, tables) for readability.
- Cross-link to relevant sections (design patterns, LLD projects) to aid revision.

## GenAI Coverage
- When new GenAI content ships in `06-genai-systems/`, consider adding quiz questions to cover GenAI system design topics (RAG, safety, evaluation, agentic workflows).
- Maintain matching answer keys in `answers/` for any new quiz questions.

## Restrictions & Gotchas
- Do not add executable code or interactive tooling.
- Preserve naming conventions to keep references intact.
- Highlight significant quiz updates in PR descriptions so study plans can be adjusted if necessary.
