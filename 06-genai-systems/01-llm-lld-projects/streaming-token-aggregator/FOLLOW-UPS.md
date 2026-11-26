# Follow-up Questions: Streaming Token Aggregator

*Note: These questions cover optional extensions to the core behavior designed to probe deeper into production readiness and protocol-level trade-offs. They are optional Staff follow-ups beyond the mandatory interview baseline.*
Once the candidate finishes the core design, use these questions to probe deeper into production readiness and protocol-level trade-offs.

## 1. SSE vs. WebSockets vs. gRPC Streams
**Question:** We used Server-Sent Events (SSE) here. How would this design change if we used WebSockets or gRPC Server-Streaming instead?

**Expected Answer:**
- **WebSockets:** WebSockets are bi-directional. While overkill for purely streaming tokens *out*, they are useful if the client needs to interrupt generation (e.g., sending a "stop" message on the same connection). The core ring buffer logic wouldn't change much, but the formatter would switch from SSE text to WebSocket frames (text or binary).
- **gRPC:** gRPC uses HTTP/2 streams natively. It handles framing and backpressure automatically at the protocol level. We wouldn't need to manually format string envelopes, we would just `yield` protobuf messages. However, gRPC isn't natively supported in web browsers without a proxy (gRPC-Web), making SSE generally easier for frontend web consumption.
- **SSE:** Best for simple, unidirectional text streams over standard HTTP/1.1 or HTTP/2.

## 2. Client Cancellation Propagation
**Question:** If the user closes their browser tab mid-generation, how do we stop the LLM from wasting compute generating the rest of the response?

**Expected Answer:**
When the client disconnects, the consumer thread attempting to write to the closed socket will eventually raise an exception (e.g., `BrokenPipeError` or `ConnectionResetError`). 
The aggregator needs a mechanism to signal this back up to the producer. This usually involves:
1. Setting a `_cancelled = True` flag on the aggregator object.
2. The LLM producer thread explicitly checking this flag on every loop iteration, or passing a `CancellationToken` object deep into the model inference engine.
3. If cancelled, the producer aborts generation and frees the GPU memory.

## 3. Reconnects and `Last-Event-ID`
**Question:** If the user's mobile connection drops for 2 seconds and they reconnect, how do we resume the stream without starting the LLM generation over from scratch?

**Expected Answer:**
SSE supports an automatic `Last-Event-ID` header upon reconnection, provided the server sent `id: <index>` fields in previous events.
However, the simple Ring Buffer aggregator drops old tokens. It cannot replay history.
To solve this:
1. The aggregator must tag events with an ID (e.g., token index).
2. A higher-level state store (like Redis or an in-memory session cache) must temporarily store the complete generated text for the active session.
3. Upon reconnection, the new request handler queries the cache for tokens > `Last-Event-ID` and streams those first, before attaching to the *live* ring buffer for new tokens.
