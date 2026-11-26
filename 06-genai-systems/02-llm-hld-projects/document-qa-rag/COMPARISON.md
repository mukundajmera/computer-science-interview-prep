# Document Q&A RAG - Comparison

## RAG vs Standard Enterprise Search (e.g., Elasticsearch)

| Concern | Document Q&A RAG | Standard Enterprise Search |
|---|---|---|
| Result format | Synthesized natural language answers | List of relevant document links/snippets |
| Query understanding | High (understands semantic intent and complex questions) | Medium (keyword matching with some semantic capabilities) |
| Multi-turn context | Supported (conversational follow-ups) | Usually unsupported (stateless queries) |
| Latency | Higher (retrieval + LLM generation time) | Lower (fast index lookup) |

## RAG vs LLM Fine-Tuning

| Concern | Document Q&A RAG | LLM Fine-Tuning |
|---|---|---|
| Knowledge updates | Real-time (simply index new documents) | Slow (requires retraining/fine-tuning the model) |
| Hallucinations | Lower (answers grounded in retrieved context) | Higher (model relies on parametric memory) |
| Access control | Native (filter retrieved docs by user permissions) | Difficult (model may leak facts to unauthorized users) |
| Cost | Lower upfront, scales with usage (inference + vector DB) | High upfront (compute for training) + inference costs |

## RAG vs Extractive QA (e.g., BERT QA)

| Concern | Document Q&A RAG | Extractive QA |
|---|---|---|
| Answer generation | Generative (can synthesize across multiple documents) | Extractive (pulls exact spans from a single text) |
| Reasoning ability | High (can summarize, compare, and rephrase) | Low (only highlights existing text) |
| Context length | Very large (128K+ tokens with modern LLMs) | Small (typically 512 tokens) |
| Implementation | Vector DB + Generative LLM API | Custom ML model deployment |
