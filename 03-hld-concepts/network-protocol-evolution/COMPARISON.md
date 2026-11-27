# Network Protocol Evolution — Comparison

A structured comparison of the main application and transport protocols covered in [THEORY.md](THEORY.md) and [INTERVIEW-QA.md](INTERVIEW-QA.md), focused on the trade-offs that come up in system design interviews.

> **Related docs:** [Theory](THEORY.md) · [Interview Q&A](INTERVIEW-QA.md) · [Common Pitfalls](PITFALLS.md) · [Follow-Up Questions](FOLLOW-UPS.md)

## Protocol Comparison Matrix

| Protocol (Transport) | Head-of-Line (HoL) Blocking | Connection Setup Cost | Multiplexing | Server Push / Streaming | Proxy & Firewall Friendliness | Typical Use |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **HTTP/1.1** (TCP) | **HTTP-layer HoL** — requests run sequentially on a connection (pipelining failed in practice due to proxy issues) | **2-RTT** with TCP + TLS 1.3 (3-RTT with TLS 1.2); keep-alive reuses the socket, browsers open ~6 connections per origin | None; clients open parallel TCP connections for concurrency | None natively (relies on polling or long polling) | **Highest** — universally understood by legacy proxies, CDNs, and corporate firewalls | Legacy APIs, simple public REST endpoints, static file serving |
| **HTTP/2** (TCP) | **TCP-layer HoL** — solves HTTP-layer HoL, but one lost TCP packet stalls all multiplexed streams until retransmitted | **2-RTT** with TCP + TLS 1.3 (3-RTT with TLS 1.2) + ALPN negotiation during TLS | **Yes** — binary framing multiplexes many concurrent streams over one TCP connection with HPACK header compression | Supports HTTP/2 Server Push (largely deprecated in browsers) and full-duplex streaming frames | **High** — runs over TCP/443; most modern CDNs and reverse proxies support it (older proxies downgrade to HTTP/1.1) | Modern web apps, REST/GraphQL APIs, parallel multipart uploads |
| **HTTP/3 (QUIC)** (UDP) | **None across streams** — independent QUIC streams mean a dropped UDP datagram blocks only its own stream | **1-RTT** initial handshake (combined transport + TLS 1.3); **0-RTT** session resumption (idempotent requests only due to replay risk) | **Yes** — native to QUIC over UDP, paired with QPACK header compression and 64-bit Connection ID migration | Supports bidirectional and unidirectional QUIC streams; server push exists in spec but is rarely used | **Moderate** — some corporate firewalls block or throttle non-DNS UDP, requiring `Alt-Svc` discovery and fallback to HTTP/2 | Mobile apps switching Wi-Fi/5G, video streaming, lossy or high-RTT networks |
| **WebSocket** (TCP) | **TCP-layer HoL** — single ordered byte stream; a dropped packet delays all subsequent frames | **~3-RTT** — TCP + TLS 1.3 (2-RTT) plus HTTP `Upgrade: websocket` handshake (1-RTT) | None natively — one frame stream per socket (app must multiplex logical channels itself) | **Full-duplex** bidirectional streaming with minimal per-frame overhead (a few bytes) | **Moderate** — `wss://` traverses port 443, but stateful connections need proxy `Upgrade` support and sticky/L4-aware load balancing | Real-time chat, multiplayer gaming, live trading feeds, collaborative editors |
| **SSE** (HTTP over TCP) | **HTTP-layer HoL** on HTTP/1.1 (limited to ~6 browser connections/origin); **TCP-layer HoL** when multiplexed over HTTP/2 | **2-RTT** with TCP + TLS 1.3 (or 0 extra RTT when reusing an open HTTP/2 connection) | None on HTTP/1.1; multiplexed as an HTTP/2 stream when served over HTTP/2 | **Unidirectional** server-to-client push (`text/event-stream`) with automatic browser reconnect (`EventSource` + `Last-Event-ID`) | **High** — plain HTTP/HTTPS passes corporate proxies easily, though buffering proxies must disable response buffering | Live feeds, notifications, sports/stock tickers, LLM token streaming |
| **gRPC** (HTTP/2 over TCP) | **TCP-layer HoL** — inherits HTTP/2's single-TCP-connection packet-loss stalling across active RPC streams | **2-RTT** with TCP + TLS 1.3 + HTTP/2 settings; amortized over long-lived pooled channels | **Yes** — full HTTP/2 stream multiplexing with compact Protobuf binary payloads | **All four modes** — unary, server streaming, client streaming, and bidirectional streaming | **High internally, limited in browsers** — needs L7 HTTP/2-aware load balancing inside clusters and `gRPC-Web` proxies for browsers | Internal microservices communication, polyglot backends, service-to-service streaming |

## HTTP Version Evolution: Transport & Latency Details

| Characteristic | HTTP/1.1 | HTTP/2 | HTTP/3 (QUIC) |
| :--- | :--- | :--- | :--- |
| **Underlying Transport** | TCP | TCP | UDP (QUIC in user space) |
| **Framing & Headers** | Plain text, uncompressed repeated headers | Binary framing, HPACK header compression | Binary QUIC frames, QPACK header compression |
| **HoL Blocking Scope** | HTTP-layer (request blocks request) | TCP-layer (lost packet blocks all streams) | Per-stream only (zero cross-stream HoL) |
| **Secure Setup Latency** | 2-RTT (TCP + TLS 1.3) | 2-RTT (TCP + TLS 1.3) | 1-RTT initial; 0-RTT resumption (idempotent only) |
| **Network Handover (Wi-Fi to 5G)** | Breaks connection (4-tuple changes) | Breaks connection (4-tuple changes) | Seamless via 64-bit Connection ID migration |
| **Impact of 1 Lost Packet** | Halts current and all queued requests | Halts every multiplexed stream on the socket | Halts only the single affected stream |

## Real-Time & Streaming Protocols: Quick Trade-Offs

| Characteristic | WebSocket | Server-Sent Events (SSE) | gRPC |
| :--- | :--- | :--- | :--- |
| **Directionality** | Full-duplex (client and server) | Server-to-client only (client sends via normal HTTP) | Unary, client-, server-, or bidirectional streaming |
| **Payload Format** | Text or binary frames | UTF-8 text (`text/event-stream`) | Strongly typed binary (Protocol Buffers) |
| **Browser Support** | Native (`WebSocket` API) | Native (`EventSource` API) | Requires `gRPC-Web` translation proxy |
| **Reconnection** | Manual (app must build backoff, heartbeats, and cursor replay) | Automatic (`EventSource` reconnects and sends `Last-Event-ID`) | Handled by client channel / retry policies |
| **Load Balancing** | Stateful long-lived connections; requires L4/sticky handling | Standard HTTP L7 proxies (disable buffering) | Requires L7 HTTP/2-aware LB (L4 pins all streams to one backend) |

## Network Degradation & Fallback Behavior

| Protocol | Under Packet Loss | On Wi-Fi to Cellular Handover | Behind Restrictive Corporate Firewalls |
| :--- | :--- | :--- | :--- |
| **HTTP/1.1** | Stalls the affected TCP socket; other parallel sockets keep moving | Connection drops; requires new TCP + TLS handshake | Works reliably over TCP/443 |
| **HTTP/2** | One lost packet stalls all multiplexed streams on the shared TCP socket | Connection drops; requires new TCP + TLS handshake | Works over TCP/443; legacy proxies may downgrade to HTTP/1.1 |
| **HTTP/3 (QUIC)** | Only the stream owning the lost datagram waits; other streams proceed | Migrates seamlessly using the 64-bit Connection ID | Non-DNS UDP may be dropped; race via `Alt-Svc` and fall back to HTTP/2 |
| **WebSocket** | Stalls subsequent frames on the TCP stream until retransmission | Connection drops; app must reconnect and replay missed messages | Some proxies strip `Upgrade` headers or reap idle sockets; fall back to SSE/long polling |
| **SSE** | Stalls the HTTP stream until TCP recovers | Connection drops; `EventSource` auto-reconnects with `Last-Event-ID` | Passes standard HTTP proxies; set `Cache-Control: no-cache` and disable proxy buffering |
| **gRPC** | Stalls all multiplexed RPCs on the shared HTTP/2 TCP channel | Connection drops; client channel reconnects and retries idempotent RPCs | Fine inside data centers with L7 proxies; browsers require `gRPC-Web` over HTTP/1.1 or HTTP/2 |

## When I Would Pick Which

In practice, production systems combine these protocols by boundary—typically HTTP/2 or HTTP/3 at the edge, SSE or WebSocket for push, and gRPC between internal services:

- **Pick HTTP/1.1** when you need maximum compatibility with legacy clients, simple curl-friendly debugging, or minimal infrastructure around low-concurrency webhooks and static assets where multiplexing adds no measurable gain.
- **Pick HTTP/2** as the default for public web applications, REST/GraphQL APIs, and CDN-backed asset delivery on reliable networks—you get multiplexing and HPACK compression over TCP/443 without UDP firewall surprises.
- **Pick HTTP/3 (QUIC)** for mobile-first apps, video streaming, or users on high-latency and lossy cellular networks where 1-RTT/0-RTT setup, zero cross-stream HoL blocking, and Connection ID migration visibly cut stalls—always paired with `Alt-Svc` fallback to HTTP/2 for restrictive corporate networks.
- **Pick WebSocket** when a browser or mobile client needs low-latency, high-frequency **bidirectional** messaging over a persistent channel—such as live chat, collaborative document editing, multiplayer games, or active trading terminals with dynamic ticker subscriptions.
- **Pick SSE** when the client only needs **unidirectional** server-to-client updates—such as LLM token streaming, live score tickers, dashboards, or notification feeds—so you stay on standard HTTP with built-in browser reconnection instead of managing stateful WebSocket infrastructure.
- **Pick gRPC** for synchronous **internal microservice-to-microservice** calls and polyglot backends where strict Protobuf contracts, code generation, low serialization overhead, and native HTTP/2 streaming matter more than human-readable JSON or direct browser access.

## Cross-Links

- [Theory](THEORY.md)
- [Interview Q&A](INTERVIEW-QA.md)
- [Common Pitfalls](PITFALLS.md)
- [Follow-Up Questions](FOLLOW-UPS.md)
