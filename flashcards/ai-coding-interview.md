# 🤖 AI Coding Interview Flashcards

> **24 flashcard questions for owning AI-assisted coding interviews**

---

## Planning Ownership (6 Cards)

### Card 1
**Front:** What aspects of a prompt should you clarify with stakeholders before writing any code?

Back: The primary focus is on orchestrating the AI tools effectively while maintaining strong engineering fundamentals. Treat the AI as a junior pair programmer that requires constant verification. Effective prompting requires setting clear constraints and formatting rules to minimize deviations from the desired architecture.

Back: Effective prompting involves setting constraints, providing examples (few-shot prompting), and specifying the expected output format to reduce hallucinations and ensure usable code.

---

### Card 2
**Front:** How do you separate responsibilities between prompt design, API orchestration, and system wiring when assigning ownership?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review. Effective prompting requires setting clear constraints and formatting rules to minimize deviations from the desired architecture.

Back: Effective prompting involves setting constraints, providing examples (few-shot prompting), and specifying the expected output format to reduce hallucinations and ensure usable code.

---

### Card 3
**Front:** Which constraints or evaluation criteria do you capture before choosing an AI-assisted solution approach?

Back: The primary focus is on orchestrating the AI tools effectively while maintaining strong engineering fundamentals. Treat the AI as a junior pair programmer that requires constant verification.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'evaluation', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 4
**Front:** How do you document assumptions about the AI model's capabilities and failure modes during planning?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'about', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 5
**Front:** What signals let you know the problem scope is well-defined enough to start coding with the model?

Back: The primary focus is on orchestrating the AI tools effectively while maintaining strong engineering fundamentals. Treat the AI as a junior pair programmer that requires constant verification.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'signals', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 6
**Front:** How do you decide which components you own versus which are handled by platform tooling or other teams?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'handled', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

## Prompting / Execution (6 Cards)

### Card 7
**Front:** What prompting strategy ensures the generated code respects performance or complexity constraints?

Back: The primary focus is on orchestrating the AI tools effectively while maintaining strong engineering fundamentals. Treat the AI as a junior pair programmer that requires constant verification. Effective prompting requires setting clear constraints and formatting rules to minimize deviations from the desired architecture.

Back: Effective prompting involves setting constraints, providing examples (few-shot prompting), and specifying the expected output format to reduce hallucinations and ensure usable code.

---

### Card 8
**Front:** How do you tell the model to favor readability and maintainability over terseness?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'model', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 9
**Front:** What verification steps do you run on the model's plan before letting it generate implementation?

Back: The primary focus is on orchestrating the AI tools effectively while maintaining strong engineering fundamentals. Treat the AI as a junior pair programmer that requires constant verification.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'steps', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 10
**Front:** What guardrails do you embed to prevent the model from hallucinating unsupported APIs or dependencies?

Back: The primary focus is on orchestrating the AI tools effectively while maintaining strong engineering fundamentals. Treat the AI as a junior pair programmer that requires constant verification.

Back: Implement guardrails by explicitly instructing the AI on what libraries it can use, what security practices to follow, and verifying the output against these constraints.

---

### Card 11
**Front:** How do you handle dependencies or libraries the model cannot import directly?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'model', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 12
**Front:** What execution metrics do you track while iterating on prompts to improve coverage and correctness?

Back: The primary focus is on orchestrating the AI tools effectively while maintaining strong engineering fundamentals. Treat the AI as a junior pair programmer that requires constant verification. Effective prompting requires setting clear constraints and formatting rules to minimize deviations from the desired architecture.

Back: Effective prompting involves setting constraints, providing examples (few-shot prompting), and specifying the expected output format to reduce hallucinations and ensure usable code.

---

## Verification / Testing (6 Cards)

### Card 13
**Front:** Which tests confirm that the AI-assisted solution handles edge cases the model might miss?

Back: The primary focus is on orchestrating the AI tools effectively while maintaining strong engineering fundamentals. Treat the AI as a junior pair programmer that requires constant verification. Independent verification through integration and fuzz testing is mandatory to catch edge cases the model missed.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'model', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 14
**Front:** How do you isolate the tests affected by randomness or non-determinism in the model output?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review. Independent verification through integration and fuzz testing is mandatory to catch edge cases the model missed.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'randomness', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 15
**Front:** What role does fuzz testing play in validating AI-generated code?

Back: The primary focus is on orchestrating the AI tools effectively while maintaining strong engineering fundamentals. Treat the AI as a junior pair programmer that requires constant verification. Independent verification through integration and fuzz testing is mandatory to catch edge cases the model missed.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'validating', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 16
**Front:** How do you design regression tests to detect prompt drift over time?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review. Effective prompting requires setting clear constraints and formatting rules to minimize deviations from the desired architecture.

Back: Effective prompting involves setting constraints, providing examples (few-shot prompting), and specifying the expected output format to reduce hallucinations and ensure usable code.

---

### Card 17
**Front:** How do you document test failures that force prompt adjustments or guardrail tuning?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review. Effective prompting requires setting clear constraints and formatting rules to minimize deviations from the desired architecture.

Back: Effective prompting involves setting constraints, providing examples (few-shot prompting), and specifying the expected output format to reduce hallucinations and ensure usable code.

---

### Card 18
**Front:** How do you ensure telemetry captures response latency and error rates for AI calls used in tests?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review. Independent verification through integration and fuzz testing is mandatory to catch edge cases the model missed.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'error', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

## Communication / Recovery (6 Cards)

### Card 19
**Front:** How do you communicate uncertainty about an AI suggestion to interviewers or reviewers?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'suggestion', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 20
**Front:** What signals trigger a rollback or pause when deploying AI-generated code in a demo or production path?

Back: The primary focus is on orchestrating the AI tools effectively while maintaining strong engineering fundamentals. Treat the AI as a junior pair programmer that requires constant verification.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'rollback', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 21
**Front:** How do you explain trade-offs between writing manual code and relying on AI assistance?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'between', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 22
**Front:** How do you inform stakeholders when AI output changes assumptions or requirements mid-stream?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'requirements', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 23
**Front:** What recovery steps do you take when AI-generated code diverges from the spec during a coding session?

Back: The primary focus is on orchestrating the AI tools effectively while maintaining strong engineering fundamentals. Treat the AI as a junior pair programmer that requires constant verification.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'coding', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---

### Card 24
**Front:** How do you coordinate debugging when AI-generated logs lack clear provenance?

Back: You achieve this by providing explicit constraints, comprehensive API contracts, and context-rich prompts. Following generation, you must rigorously verify the output through unit testing and manual code review.

Back: Using AI for coding requires treating the AI as a pair programmer: you must provide clear context, verify its outputs rigorously, and maintain full ownership of the final code. Specifically, regarding 'ai-generated', you must carefully evaluate the trade-offs and ensure your approach aligns with the overall goals.

---
