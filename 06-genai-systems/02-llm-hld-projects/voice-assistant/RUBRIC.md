# Real-Time Voice Assistant: Evaluation Rubric

This rubric provides guidelines for evaluating candidate designs in a system design interview context. It looks for understanding of WebRTC, latency optimization techniques like streaming, and cost management for compute-heavy models.

## Interview Guide

### 1. Requirements & Problem Scoping (10-15 min)
*   **Good Signal:** The candidate quickly identifies the strict latency requirements for real-time voice and the need for full-duplex communication (barge-in).
*   **Red Flags:** Fails to clarify if the system is cascaded or speech-to-speech. Ignores the difference between text latency and audio latency.

### 2. High-Level Architecture (15-20 min)
*   **Good Signal:** Proposes a WebRTC-based architecture with edge components for VAD/transport and central components for heavy inference. Explains how barge-in halts ongoing generation.
*   **Red Flags:** Uses HTTP/REST for audio streaming. Misses VAD/endpointing entirely.

### 3. Deep Dives (10-15 min)
*   **Good Signal:** Can break down a realistic latency budget (e.g., 50ms network, 150ms ASR, 100ms LLM TTFT, 100ms TTS TTFA = 400ms total). Discusses the trade-offs of streaming chunk sizes.
*   **Red Flags:** Assumes LLMs process audio natively without understanding the underlying modality conversions or S2S models.

### 4. Edge Cases & Cost (5-10 min)
*   **Good Signal:** Can estimate cost per minute of active conversation, considering both compute (GPUs) and bandwidth (WebRTC). Discusses handling noisy environments (VAD false positives).
*   **Red Flags:** Ignores the high cost of persistent WebRTC connections and continuous ASR transcription.

## Section: Performance and Cost Evaluation

The rubric evaluates the architecture on latency, cost, and conversational fluidity. A successful design must demonstrably reduce TTFA through techniques like edge VAD and streamed processing (targeting < 800ms [Source: Industry Benchmarks]). The candidate should articulate trade-offs between cascaded and end-to-end models (e.g., a 200ms latency advantage for E2E [Source: Speech Tech Review]). Furthermore, the system must handle edge cases like barge-in gracefully, updating conversation history accurately. Cost optimization strategies, such as adaptive chunking or model quantization (which can reduce memory footprint by 50% [Source: ML Optimization Guides]), should also be factored into the overall score.
