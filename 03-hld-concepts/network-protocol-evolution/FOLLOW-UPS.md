# Network Protocol Evolution — Follow-Up Questions

Targeted interview follow-ups grouped by seniority level. Each question includes a brief expected-answer hint aligned with [THEORY.md](THEORY.md), [COMPARISON.md](COMPARISON.md), and [INTERVIEW-QA.md](INTERVIEW-QA.md).

> **Related docs:** [Theory](THEORY.md) · [Comparison](COMPARISON.md) · [Interview Q&A](INTERVIEW-QA.md) · [Common Pitfalls](PITFALLS.md)

## Mid-Level

1. **HTTP/2 introduced multiplexing to solve Head-of-Line (HoL) blocking. Why does HoL blocking still happen in HTTP/2, and what happens at the packet level when one packet is lost?**
   * *Expected-answer hint:* HTTP/2 eliminates HTTP-layer HoL blocking by interleaving binary frames from multiple streams on one TCP connection, but TCP still enforces strict in-order delivery. If a single TCP packet for Stream A is dropped, the OS buffers arriving packets for Stream B until Stream A's packet is retransmitted, stalling all streams on that socket.

2. **You are building a live notification feed or an LLM token-streaming UI. Why would you choose Server-Sent Events (SSE) over WebSockets, and how does SSE handle disconnects?**
   * *Expected-answer hint:* After the initial client request, data flows strictly from server to client, so SSE avoids WebSocket's stateful proxy configuration and full-duplex overhead by running over standard HTTP (`text/event-stream`). The browser's `EventSource` API automatically reconnects and sends the `Last-Event-ID` header so the server can resume missed events.

3. **Why does walking from Wi-Fi to 5G stall a video stream over HTTP/2, and how does HTTP/3 (QUIC) avoid that interruption?**
   * *Expected-answer hint:* TCP identifies a connection by its 4-tuple `(Source IP, Source Port, Dest IP, Dest Port)`, so a client IP change breaks the socket and forces fresh TCP/TLS handshakes and slow start. QUIC identifies connections using a 64-bit Connection ID in the packet header, letting the client keep sending packets from the new IP without renegotiating the session.

4. **Why did the creators of QUIC build it on top of UDP instead of defining a brand-new transport protocol directly on top of IP?**
   * *Expected-answer hint:* Middlebox ossification: decades of firewalls, NAT routers, and load balancers only recognize TCP and UDP and silently drop unknown IP protocol numbers. Encapsulating QUIC inside UDP lets it traverse the existing internet while allowing transport features to evolve in user space.

## Senior-Level

5. **Explain the security trade-off of QUIC/TLS 1.3 0-RTT session resumption. How do you prevent replay attacks in production?**
   * *Expected-answer hint:* 0-RTT encrypts application data in the first packet using cached session keys before the server supplies a fresh nonce, so an attacker who intercepts that packet can replay it multiple times. Restrict 0-RTT strictly to idempotent requests (such as `GET` for static assets) and reject 0-RTT early data on state-mutating endpoints like payments or writes.

6. **If you are building a real-time collaborative document editor in the browser, would you choose WebSockets or gRPC? Why?**
   * *Expected-answer hint:* Choose WebSockets because browsers natively support full-duplex persistent WebSocket connections for low-latency bidirectional edits. Standard gRPC depends on raw HTTP/2 framing and trailers that browsers do not expose directly, requiring a `gRPC-Web` translation proxy that adds hops and restricts native bidirectional streaming.

7. **How does QUIC provide reliable delivery and congestion control when UDP itself offers neither?**
   * *Expected-answer hint:* QUIC implements packet numbering, acknowledgments, loss recovery, and pluggable congestion control (such as CUBIC or BBR) entirely in user space on top of UDP. Keeping transport logic in user space lets applications ship congestion-control improvements at release cadence instead of waiting for OS kernel updates.

8. **You enable HTTP/3 for an enterprise web and mobile app, but some corporate Wi-Fi networks block all non-DNS UDP traffic. How do clients discover HTTP/3 and recover cleanly?**
   * *Expected-answer hint:* Clients start over standard TCP (HTTP/1.1 or HTTP/2), read the server's `Alt-Svc` response header advertising HTTP/3 on UDP, and race a background QUIC handshake against the active TCP session. If UDP times out or is rejected with ICMP unreachable, the client stays on HTTP/2 over TCP transparently with zero user-facing failure.

## Staff-Level

9. **Why does a traditional L4 load balancer cause uneven traffic distribution for gRPC or long-lived HTTP/2 services, and how do you fix it?**
   * *Expected-answer hint:* An L4 load balancer makes routing decisions once per TCP connection, so a client multiplexing thousands of RPCs over one persistent HTTP/2 channel pins all traffic to a single backend instance even after autoscaling adds new pods. Solve this with an L7 HTTP/2-aware proxy (such as Envoy), client-side load balancing via service discovery, or periodic connection cycling (`MAX_CONNECTION_AGE`).

10. **How do QUIC Connection IDs interact with stateless L4 load balancers and Anycast routing when a mobile client migrates IP addresses?**
    * *Expected-answer hint:* If a stateless L4 load balancer hashes the packet's 4-tuple, a client's IP change will route its migrated QUIC packets to a different backend server that lacks the session keys. Production edge fleets embed an encrypted server or worker routing identifier inside the QUIC Connection ID so L4 load balancers route consistently by CID across IP changes.

11. **Why did HTTP/3 replace HTTP/2's HPACK header compression with QPACK, and what trade-off does QPACK introduce?**
    * *Expected-answer hint:* HPACK updates a single shared dynamic table strictly in transmission order, which would reintroduce cross-stream HoL blocking over QUIC's out-of-order independent streams. QPACK decouples table updates onto dedicated unidirectional encoder/decoder streams and lets implementations cap blocked streams, trading slightly lower compression ratios for zero cross-stream stalling.

12. **Under what network or host conditions can HTTP/3 underperform HTTP/2, and how would you roll out HTTP/3 safely across a global CDN?**
    * *Expected-answer hint:* On clean, high-bandwidth wired links, user-space UDP processing and encryption can consume more CPU than kernel-offloaded TCP (TSO/GSO/GRO), and some ISPs rate-limit UDP bursts. Roll out HTTP/3 incrementally via `Alt-Svc` cohorts, comparing p50/p99 TTFB, connection error rates, and edge CPU per Gbps against an HTTP/2 holdback while keeping automatic TCP fallback active.

## Cross-Links

- [Theory](THEORY.md)
- [Comparison](COMPARISON.md)
- [Interview Q&A](INTERVIEW-QA.md)
- [Common Pitfalls](PITFALLS.md)
