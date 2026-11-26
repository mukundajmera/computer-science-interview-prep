# AI Coding Copilot

## Problem Statement

Design an AI-powered coding assistant (like GitHub Copilot) that integrates into IDEs to provide real-time code completions, inline suggestions, chat-based code Q&A, and code generation from natural language descriptions. The system must handle millions of developers with ultra-low latency for inline completions while managing context from large codebases.

---

## Functional Requirements

1. **Inline Code Completion**: Ghost-text suggestions as the developer types (like autocomplete)
2. **Chat-Based Code Q&A**: Conversational interface for code explanations, debugging, refactoring
3. **Code Generation**: Generate code from natural language comments or descriptions
4. **Multi-Language Support**: Python, JavaScript, TypeScript, Java, Go, C++, Rust, and more
5. **Context Awareness**: Use open files, project structure, and imports for relevant suggestions
6. **Accept/Reject Tracking**: Track suggestion acceptance rate for quality measurement
7. **IDE Integration**: VS Code, JetBrains, Neovim via extensions/plugins

---

## Non-Functional Requirements

| Requirement | Target |
|-------------|--------|
| Availability | 99.9% |
| Inline completion latency | < 300ms (first token) |
| Chat response latency | < 1 second (first token) |
| Throughput | 1 million concurrent developers |
| Suggestion quality | > 30% acceptance rate |
| Scalability | Handle typing-speed request rates per user |

---

## Interview-Mode Constraints and Evaluation Criteria

In AI-enabled coding interviews, this system is also judged by how candidates operate while using AI tools. Add these execution constraints:

| Dimension | Interview expectation |
|-----------|-----------------------|
| Problem-solving & approach | Candidate clarifies requirements and proposes phased implementation before prompting |
| Control over AI | Candidate drives architecture and accepts/rejects generated code intentionally |
| Verification discipline | Candidate validates generated output via tests, walkthroughs, and edge-case checks |
| Communication | Candidate narrates intent, changes, and trade-offs throughout execution |

Typical interview variants:
1. **Structured platform rounds**: fixed environment, multi-phase tasks on starter code.
2. **Open-ended rounds**: candidate IDE/tools, greenfield or lightly scaffolded implementation.

---

## GenAI-Specific Requirements

| Requirement | Target |
|-------------|--------|
| Code correctness | > 85% syntactically valid suggestions |
| Security | No generation of known vulnerability patterns |
| License compliance | No verbatim reproduction of copyrighted code |
| Context window | Up to 128K tokens for large files |
| Completion length | 1–50 tokens (inline), up to 4K tokens (chat) |
| Cost per suggestion | < $0.001 (inline), < $0.01 (chat) |

---

## Assumptions

- **Users**: 2 million registered developers, 500K DAU
- **Inline completions**: 100 requests/user/hour (typing-triggered) → ~50M requests/day
- **Chat interactions**: 10 messages/user/day → 5M messages/day
- **Average file context**: 2,000 tokens (current file) + 1,000 tokens (related files)
- **Model**: Fast model for inline (Codestral/GPT-4o-mini), powerful model for chat (GPT-4o/Claude)
- **Trigger**: Debounced at 300ms after typing pause

---

## Out of Scope

- Full CI/CD integration
- Code review automation (separate product)
- Repository-level indexing at onboarding (v1)
- Custom model fine-tuning per organization
- Voice-to-code interface

---

## Sample Interactions

```
1. Inline Completion (ghost text):
   Trigger: User types "def calculate_"
   Context: Current file, cursor position, imports
   Response: "total_price(items: list[dict]) -> float:"
   Latency: < 300ms

2. Chat Q&A:
   POST /api/v1/chat
   Request: { "message": "Explain what this function does and suggest improvements",
              "codeContext": "def merge_sort(arr):..." }
   Response (streaming): "This function implements merge sort... I'd suggest..."

3. Code Generation from Comment:
   Trigger: User types "// Function to validate email address using regex"
   Response: Complete function implementation
```

---

## Clarifying Questions to Ask

1. "What's the target latency for inline completions vs chat responses?"
2. "How many concurrent users do we need to support?"
3. "What programming languages should we prioritize?"
4. "Do we need to handle private codebases or only public code patterns?"
5. "What's the acceptable cost per suggestion?"
6. "Should we support Fill-in-the-Middle (FIM) or just left-to-right completion?"
7. "Do we need organization-level customization?"
8. "What IDE platforms are priority?"

---

## Key Design Challenges

| Challenge | Why It's Hard |
|-----------|---------------|
| Ultra-low latency | 300ms budget for inline completions is extremely tight |
| Context selection | Must choose the most relevant code from large projects |
| Two request modes | Inline (fast, short) vs chat (slower, detailed) need different models |
| High request rate | Every keystroke could trigger a request (need debouncing) |
| Code correctness | Suggestions must be syntactically valid and contextually appropriate |
| License compliance | Must not reproduce copyrighted code verbatim |
| Cost at scale | 50M inline requests/day must be extremely cheap per request |

---

## Version Roadmap

| Version | Features |
|---------|----------|
| v1-basic | Inline completion, single-file context, one model, basic debouncing |
| v2-smart | Multi-file context, FIM support, model routing, chat, accept/reject tracking |
| v3-enterprise | Org-level customization, repo indexing, on-prem deployment, fine-tuning |
