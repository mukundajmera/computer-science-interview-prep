# Interview Q&A: WebSockets

## 1) WebSockets vs long polling?
WebSockets keep one bidirectional channel; long polling repeatedly opens HTTP requests with higher overhead.
- **WebSockets** establish a single, long-lived TCP connection that remains open, allowing for full-duplex (two-way) communication with very low latency. The framing overhead is minimal once the connection is established.
- **Long Polling** involves the client sending an HTTP request and the server holding it open until data is available. Once the server responds, the client must immediately send a new HTTP request to re-establish the connection. This constant connection cycling incurs significant overhead from HTTP headers, TCP handshakes, and TLS negotiation, leading to higher latency and wasted server resources.

## 2) How do you scale WebSocket servers?
Use sticky routing for connection ownership and a pub/sub layer (Redis/Kafka) for fan-out across nodes.
Because WebSocket connections are stateful, a standard round-robin load balancer won't work for message delivery. If Client A (on Node 1) sends a message to Client B (on Node 2), Node 1 cannot send it directly.
Instead, we use a distributed backplane (like Redis Pub/Sub, NATS, or Kafka). When Node 1 receives the message, it publishes it to the backplane. Node 2, which maintains Client B's connection, subscribes to the relevant channel, receives the message, and forwards it to Client B. This decoupling allows horizontal scaling of the connection-holding nodes.

## 3) How do you detect dead connections?
Application ping/pong heartbeats and timeout-based cleanup.
Relying solely on TCP keep-alives or waiting for `FIN`/`RST` packets is insufficient, as intermediate routers or sudden client power loss can leave the server holding a "zombie" connection indefinitely.
The standard approach is to use WebSocket control frames. The server periodically sends a `0x9` Ping frame. The client is obligated to respond with a `0xA` Pong frame. The server tracks these timestamps. If a connection misses multiple consecutive heartbeats (e.g., no response for 30-60 seconds), the server forcefully terminates the connection to reclaim the file descriptor and memory.

## 4) What is the reconnection strategy?
Exponential backoff with jitter to prevent reconnect storms.
During a server deployment or a brief network partition, tens of thousands of WebSocket clients might disconnect simultaneously. If they all try to reconnect instantly, the resulting flood of TCP handshakes and authentication requests (a "thundering herd") will overwhelm the load balancers and backend services, causing a cascading failure.
To prevent this, clients must use exponential backoff (waiting 1s, 2s, 4s, 8s, etc.) combined with full jitter (randomizing the delay within that window). This smears the reconnection attempts over time, allowing the infrastructure to recover gracefully.

## 5) How many connections can a single server handle?
It depends heavily on kernel tuning and memory.
The theoretical limit is bound by ephemeral ports (if acting as a client) or file descriptors. By default, Linux limits file descriptors (e.g., 1024). You must increase `ulimit -n` and `fs.file-max`.
More importantly, memory is the bottleneck. Even idle connections require TCP socket buffers. If `net.ipv4.tcp_rmem` and `tcp_wmem` are default (e.g., ~64KB each), 1 million connections require ~128GB of RAM just for the kernel buffers. For high-density servers (like chat applications), these buffers are often tuned down to 16KB-32KB to pack more connections onto a single machine.

## 6) What is the security purpose of the WebSocket mask key?
It prevents proxy cache poisoning.
All client-to-server WebSocket frames must have their payload masked (XORed) with a random 4-byte key included in the frame header.
If a malicious client sends a payload that looks exactly like a valid HTTP `GET` request, a poorly implemented intermediate transparent HTTP proxy might misinterpret the payload as a new HTTP request and cache the response. By masking the payload, the data appears as random noise to the proxy, preventing this specific class of protocol confusion attack. Server-to-client frames do not require masking.

## 7) How does the WebSocket handshake work?
It upgrades an HTTP connection using a specific key exchange.
The client sends an HTTP `GET` request with `Upgrade: websocket` and a random `Sec-WebSocket-Key` (base64 encoded).
The server, if it supports WebSockets, responds with an HTTP `101 Switching Protocols`. To prove it understood the request and prevent caching intermediaries from serving stale upgrade responses, the server must calculate the `Sec-WebSocket-Accept` header. It does this by concatenating the client's key with a specific RFC-defined GUID, taking the SHA-1 hash, and encoding it in base64.

## 8) When would you choose Server-Sent Events (SSE) over WebSockets?
When communication is strictly unidirectional (server-to-client).
WebSockets provide full-duplex communication, which is necessary for chat apps or games.
If the application only needs to receive updates from the server (e.g., a real-time news feed, stock ticker, or progress bar), SSE is a simpler alternative. SSE operates over standard HTTP, leverages built-in browser connection retry logic, and multiplexes easily over HTTP/2, whereas WebSockets require a distinct protocol upgrade and custom client-side retry handling.

## 9) Which projects rely on WebSockets?
- [Chat Service](../../04-hld-projects/chat-service/)
- [Ride Sharing](../../04-hld-projects/ride-sharing/)
- [File Storage](../../04-hld-projects/file-storage/)

