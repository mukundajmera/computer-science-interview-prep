# Common Pitfalls: Token Streaming Server

This document outlines concrete counterexamples based on the baseline implementation.

See reference implementation: [streaming_server.py](./python/v1-basic/streaming_server.py).

### Pitfall 1: Buffering Everything (Breaking O(N) Streaming)
If a candidate accumulates all tokens in a list or string and only yields them after the generator exhausts, they have essentially broken the stream. 
- **Consequence:** The server's space complexity becomes $O(N)$ instead of $O(M)$ (where $M$ is chunk size), and the client receives no intermediate updates, eliminating the latency benefits of streaming.
- **Trade-off Analysis:** While buffering everything simplifies the code (no chunking logic), it ruins the low-latency user experience expected from LLMs and increases memory pressure on the server.
- **Python Mitigation:** Yield chunks incrementally instead of returning one large string.
- **Java Mitigation:** Use a `Writer` or `OutputStream` to flush intermediate `String` chunks incrementally.

### Pitfall 2: Missing Cancellation Handlers
Failing to catch client disconnect signals.
- **Consequence:** If the HTTP client drops the connection, the generator might silently keep running in the background. The server process becomes a zombie, consuming GPU/LLM resources for a request no one is listening to.
- **Trade-off Analysis:** Ignoring cancellation is easier to write, but fatal for production resource management, as dropped connections will tie up limited GPU concurrency.
- **Python Mitigation:** 
  ```python
  except asyncio.CancelledError:
      provider.abort()
      raise
  ```
- **Java Mitigation:** 
  ```java
  catch (InterruptedException | IOException e) {
      provider.abort();
      throw e;
  }
  ```

### Pitfall 3: Failing to Clear Local State (Privacy Leak)
Relying on implicit garbage collection without actively clearing sensitive context.
- **Consequence:** In multi-tenant async environments, if the generator scope is inadvertently captured by a closure or logging framework, sensitive user tokens could be leaked.
- **Trade-off Analysis:** Explicit variable clearing adds boilerplate, but is a defensive programming practice that guarantees sensitive references are nulled out before natural garbage collection occurs.
- **Python Mitigation:** 
  ```python
  finally:
      chunk_buffer = None
      generator = None
  ```
- **Java Mitigation:** 
  ```java
  finally {
      chunk_buffer = null;
      generator = null;
  }
  ```

### Pitfall 4: Missing Heartbeats
Assuming the LLM will always produce tokens continuously without pausing.
- **Consequence:** If the LLM stalls for 30+ seconds (e.g., retrieving context), intermediate proxies (like AWS ALB or NGINX) will drop the idle connection.
- **Trade-off Analysis:** Adding a timeout wrapper introduces concurrency complexity, but is strictly required to prevent connection drops in real-world infrastructure.
- **Python Mitigation:** 
  ```python
  try:
      token = await asyncio.wait_for(generator.__anext__(), timeout=HEARTBEAT_TIMEOUT)
  except asyncio.TimeoutError:
      yield "event: ping\ndata: {}\n\n"
  ```
- **Java Mitigation:** 
  ```java
  try {
      String token = future.get(HEARTBEAT_TIMEOUT, TimeUnit.SECONDS);
  } catch (TimeoutException e) {
      out.write("event: ping\ndata: {}\n\n");
      out.flush();
  }
  ```

### Pitfall 5: Dropping the Remainder Buffer
Forgetting to flush the remaining string buffer after the generator exits.
- **Consequence:** If the last generated tokens don't naturally end in a boundary character (like a space or period), those tokens are dropped, leading to truncated client outputs.
- **Trade-off Analysis:** The overhead of a final check is negligible, ensuring correctness and completeness of the streamed response.
- **Python Mitigation:** 
  ```python
  if chunk_buffer:
      yield f"data: {chunk_buffer}\n\n"
  ```
- **Java Mitigation:** 
  ```java
  if (chunk_buffer != null && !chunk_buffer.isEmpty()) {
      out.write("data: " + chunk_buffer + "\n\n");
      out.flush();
  }
  ```
