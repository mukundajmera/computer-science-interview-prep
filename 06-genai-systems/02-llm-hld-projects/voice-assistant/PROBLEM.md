# Real-Time Voice Assistant: Problem Statement

The goal is to design a high-level architecture for a real-time conversational voice assistant capable of low latency interactions, barge-in (interruption) handling, and high concurrency. The problem involves deciding between cascaded architectures (ASR -> LLM -> TTS) and end-to-end speech-to-speech models, selecting appropriate transport protocols like WebRTC, and managing endpointing to know when the user has finished speaking.

## Section: Interactive AI Constraints

The core problem is delivering a highly responsive, conversational AI experience over variable network conditions. Users expect interactions comparable to human conversations, which necessitates a stringent latency budget (e.g., < 800ms TTFA) [Source: Voice Assistant Latency Studies]. The challenge is balancing this requirement against the computational intensity of generative models and the financial cost of running continuous speech processing pipelines at scale (often exceeding $10,000/month for large deployments [Source: Cloud Architecture Cost Models]). Managing interruptions (barge-in) within 150ms and accurately determining turn-taking boundaries further complicate the problem space [Source: Real-Time Communication Standards].
