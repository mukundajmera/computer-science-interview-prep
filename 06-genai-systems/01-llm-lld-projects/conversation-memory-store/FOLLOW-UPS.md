# Conversation Memory Store - Follow-Up Questions

## Follow-up questions
1. How would you persist conversation history across distributed worker nodes?
2. How would you handle vector search over conversation memory to retrieve relevant past turns?
3. How do you implement hierarchical summarization for multi-session long-term memory?
4. How would you support multi-modal messages (e.g. image inputs and audio transcripts)?
5. How would you enforce privacy and GDPR compliance (e.g. forget-me / turn deletion)?

## Variants and extensions
- Entity Memory: extracting key facts and entities about the user.
- Vector-augmented Memory: embedding turns and performing hybrid semantic search.
- Ephemeral vs Persistent storage tiers.

## Interviewer probes to prepare
- "Why use the Strategy pattern for memory management?"
- "How do you guarantee that system instructions are never dropped during truncation?"
- "What are the trade-offs between sliding window and summary memory?"

## Cross-links
- [Problem statement](./PROBLEM.md)
- [Design details](./DESIGN.md)
