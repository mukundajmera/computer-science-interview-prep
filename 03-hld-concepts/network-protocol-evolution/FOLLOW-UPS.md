# Network Protocol Evolution - Follow-Up Questions

## Follow-up questions

1.  **Explain the security implications of 0-RTT session resumption in QUIC. How do you prevent replay attacks?**
    *   *Focus:* Understanding that 0-RTT lacks forward secrecy and freshness guarantees on the first flight. Prevention involves only allowing idempotent operations (like GET) during the 0-RTT phase.
2.  **If you are building a real-time collaborative document editor (like Google Docs), would you choose WebSockets or gRPC? Why?**
    *   *Focus:* Analyzing the trade-offs of full-duplex communication in browsers. WebSockets are natively supported in all browsers, whereas gRPC requires `grpc-web` translation proxies.
3.  **How does QUIC handle congestion control given that it is built on top of UDP, which has no native congestion control?**
    *   *Focus:* Knowing that QUIC reimplements congestion control (similar to TCP Reno/CUBIC/BBR) entirely in the user space / application layer, giving it more flexibility to evolve than kernel-space TCP.
4.  **Describe how Server-Sent Events (SSE) work over an HTTP connection. How does it handle reconnections compared to WebSockets?**
    *   *Focus:* Explaining the `text/event-stream` content type, chunked transfer encoding, and the built-in browser standard for the `EventSource` API which automatically reconnects and sends the `Last-Event-ID`.
5.  **Why did the industry choose to build QUIC on top of UDP rather than creating an entirely new IP protocol layer?**
    *   *Focus:* The concept of "middlebox ossification." Firewalls and NAT routers on the public internet only understand TCP and UDP. A new protocol would be dropped globally. Building on UDP was the only practical way to deploy a new transport protocol.

## Variants and extensions

*   **Streaming LLM Tokens:** Designing the transport layer for a ChatGPT-like interface. Why is SSE preferred over WebSockets here? (Because data is strictly unidirectional server-to-client after the initial prompt).
*   **Mobile Network Handover:** Tracing the exact sequence of events when a user streaming Netflix walks out of their house and switches from Wi-Fi to 5G. How does QUIC's Connection ID maintain the stream without rebuffering?

## Interviewer probes to prepare

*   *If the candidate suggests HTTP/3 for everything:* "What happens if a corporate firewall blocks all UDP traffic except port 53 (DNS)? How does the client recover?"
*   *If the candidate struggles with HoL blocking:* "Walk me through what happens at the packet level in HTTP/2 if the TCP packet containing the CSS file is dropped, but the packet containing the JS file arrives successfully."
