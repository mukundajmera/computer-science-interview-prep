# Prompt Builder - Common Pitfalls

## Common pitfalls
1. Unescaped curly braces in code blocks or JSON examples causing template parsing crashes.
2. Silent omission of missing template variables resulting in incomplete prompts sent to LLMs.
3. Prompt injection vulnerability by directly concatenating raw user strings into system instructions.
4. Mutating shared prompt template instances across concurrent user requests.
5. Inability to estimate rendered token size before sending, resulting in unexpected context overflows.

## Why these fail interviews
- Neglects core security vulnerabilities (prompt injection, data exfiltration).
- Fragile string manipulation that breaks on JSON or programming code inputs.

## Mitigations
- Validate required variables explicitly and raise descriptive KeyError / ValidationError.
- Escape literal braces (e.g. `{{` and `}}`).
- Maintain immutability of template configurations.
- Clear separation between system prompt instructions and untrusted user variables.

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Design details](./DESIGN.md)
