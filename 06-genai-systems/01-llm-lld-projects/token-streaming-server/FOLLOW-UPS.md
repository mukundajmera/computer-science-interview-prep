# Staff Follow-Ups: Token Streaming Server

These extensions are strictly optional follow-ups for candidates who complete the baseline early. They discuss unimplemented features such as distributed queues, dynamic throttling, and real tokenizer integration.

See baseline implementation: [streaming_server.py](./python/v1-basic/streaming_server.py).

### Extension 1: Distributed Generation Queues (Unimplemented, Optional)
*Context:* The current baseline assumes the LLM provider runs in the same async process as the HTTP server.
*Follow-up Question:* How would you modify this pipeline if the LLM inference engine runs on a dedicated GPU cluster, and you must stream tokens back over a message broker?
*Expected Discussion:*
- Subscribing to a unique channel (e.g., via sockets) per request.
- Handling distributed cancellation (sending a specific "ABORT" message to the queue rather than just calling a local `.abort()` method).
- **Trade-off:** Decoupling adds network latency and complexity, but allows independent scaling of the HTTP tier and GPU tier.
- **Python Concept:** `await socket.recv()` inside the async generator loop.
- **Java Concept:** `socket.getInputStream().read(...)` running in a dedicated `ExecutorService` thread.

### Extension 2: Dynamic Backpressure Throttling (Unimplemented, Optional)
*Context:* The baseline implicitly relies on `async for` blocking to provide backpressure.
*Follow-up Question:* If a client is consuming tokens extremely slowly, how could we explicitly pause the upstream generator rather than just blocking the socket write?
*Expected Discussion:*
- Monitoring TCP socket buffer sizes or explicit ack signals.
- Signaling the `LLMProvider` interface to pause inference context swapping until the network queue drains.
- **Trade-off:** Explicit backpressure improves memory safety under heavy load, but requires complex bidirectional signaling that can be difficult to tune.
- **Python Concept:** `await provider.pause()` if `processed_token_count - ack_count > THRESHOLD`.
- **Java Concept:** `provider.pause()` if a bounded `BlockingQueue` exceeds capacity.

### Extension 3: Real Tokenizer Integration (Unimplemented, Optional)
*Context:* The current codebase uses a standard library string approximation (`Tokenizer.is_boundary`).
*Follow-up Question:* If we were to integrate a real sub-word tokenizer, what complexities would that introduce to chunk buffering?
*Expected Discussion:*
- Sub-word tokens often cross visual character boundaries (e.g., emojis or non-English scripts taking multiple byte tokens).
- Decoding byte streams into valid UTF-8 strings before yielding SSE events to prevent frontend rendering errors on incomplete unicode characters.
- **Trade-off:** True tokenization ensures exact semantic rendering, but adds CPU overhead and requires maintaining state for partial byte-sequences across chunks.
- **Python Concept:** Accumulating `bytes` and using `buffer.decode('utf-8', errors='strict')` in a try-catch block to wait for a complete character.
- **Java Concept:** Accumulating `byte[]` and using `new String(bytes, StandardCharsets.UTF_8)` with a `CharsetDecoder` to detect malformed partial sequences.
