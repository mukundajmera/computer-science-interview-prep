# Design: Token Streaming Server

## Architecture Overview

The Token Streaming Server acts as an asynchronous middleware component. It consumes an async token stream from an injected `LLMProvider`, processes and buffers the tokens, and yields formatted Server-Sent Events (SSE) to the downstream web framework transport.

### Injected Interfaces & Approximations

To ensure testability and isolation, the server relies on the following standard-library approximated interfaces:

- `LLMProvider`: An abstract interface providing an `async_generate(prompt: str, tenant_id: str)` method that returns an async generator yielding strings, and an `abort()` method to cancel generation.
- `Clock`: An abstract interface to provide deterministic time (e.g., `time.time()` in production, or a mock in tests) to support heartbeat timing.
- `Tokenizer` (Approximation): Since real tokenizers are complex, we approximate this by using simple string boundary checks (e.g., splitting on spaces or punctuation) to determine chunk flushes.

### The Asynchronous Pipeline

The core processing loop, typically implemented as an `async def stream_response(...)` generator:

1. **Initialization:** A request starts. A local string buffer is initialized.
2. **Event Loop:** We iterate `async for token in provider.async_generate(...)`.
3. **Heartbeat Wrapper:** The generation pull is wrapped in `asyncio.wait_for(..., timeout=15)`. If it times out, we catch `TimeoutError`, yield a heartbeat `event: ping\ndata: {}\n\n`, and resume the loop.
4. **Buffering:** When a token arrives, it is appended to the local buffer.
5. **Flushing:** We check the buffer against our `Tokenizer` approximation. If a semantic boundary is found (e.g., the string ends in a space), we format the buffer as SSE (`data: {buffer}\n\n`), yield it, and clear the buffer.
6. **Completion:** When the generator naturally exhausts, any remaining buffer is flushed, followed by a final termination event (e.g., `data: [DONE]\n\n`).

### Failure & Cancellation Handling

- **Client Disconnect:** Web frameworks typically raise an `asyncio.CancelledError` inside the generator when the client socket drops. The server wraps the main loop in a `try...except asyncio.CancelledError:` block. In the `except` block, it calls `provider.abort()` to halt the backend LLM.
- **Provider Exceptions:** If the `LLMProvider` raises an error (e.g., rate limit, model overload), the server catches it, yields an SSE error event (`event: error\ndata: {"message": "..."}\n\n`), and cleanly exits the generator.

### Privacy & Tenant Boundaries

- **Tenant Isolation:** The `LLMProvider` requires a `tenant_id` for generation. The streaming server enforces that tokens yielded to a specific connection were generated using that connection's `tenant_id`, preventing cross-tenant leakage.
- **Ephemeral State:** The token buffer is strictly a local variable within the async generator's scope. When the coroutine finishes or cancels, the buffer falls out of scope and is garbage collected. No tokens are written to disk or long-term caches by this component.

## Semantic Guarantees

- **Order:** Tokens are yielded strictly in the order they are generated.
- **Lossless:** Unless an error occurs, no tokens are dropped; they are either buffered or flushed.
- **Unimplemented Guarantees:** This microcomponent does not handle embedding generation, tokenization, production-grade safety filtering (redaction, PII scrubbing), or distributed load balancing. These are assumed to be handled by other dedicated components in the pipeline.

## Reference Contracts

### Python Interface
```python
from abc import ABC, abstractmethod
from typing import AsyncGenerator

class LLMProvider(ABC):
    @abstractmethod
    async def async_generate(self, prompt: str, tenant_id: str) -> AsyncGenerator[str, None]:
        pass
        
    @abstractmethod
    def abort(self) -> None:
        pass
```

### Java Interface
```java
import java.util.concurrent.Flow;

public interface LLMProvider {
    Flow.Publisher<String> generateAsync(String prompt, String tenantId);
    void abort();
}
```
