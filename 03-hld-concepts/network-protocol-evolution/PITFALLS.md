# Network Protocol Evolution - Common Pitfalls

## 1. Confusing HTTP-layer vs. TCP-layer Head-of-Line Blocking
* **Failure Signal:** The candidate claims HTTP/2 "solved Head-of-Line (HoL) blocking entirely."
* **Root Cause:** Failing to distinguish between application-layer sequencing and transport-layer reliability. HTTP/2 solved HTTP-level HoL blocking via multiplexing, but exposed TCP-layer HoL blocking because all multiplexed streams traverse a single TCP connection.
* **Mitigation:** Always clarify that HTTP/2 suffers from TCP-level HoL blocking (one dropped packet halts all streams). Mention HTTP/3 (QUIC) as the true solution because it handles multiplexing independently per stream over UDP.
* **Validation Signal:** The candidate can explain how a single dropped packet affects multiple parallel image downloads differently in HTTP/1.1, HTTP/2, and HTTP/3.

## 2. Defaulting to WebSockets for All Real-time Features
* **Failure Signal:** Proposing WebSockets for a live sports ticker or a simple notification feed.
* **Root Cause:** Treating "real-time" as a monolithic requirement and defaulting to the most complex protocol. WebSockets provide full-duplex communication, which is overkill for unidirectional server-to-client updates and requires complex stateful load balancing.
* **Mitigation:** Analyze the directionality of data flow. Use Server-Sent Events (SSE) for unidirectional push (like live tickers or LLM tokens) because it works over standard HTTP and handles reconnections automatically.
* **Validation Signal:** The candidate asks, "Is the real-time data flowing bidirectionally or only from the server to the client?" before choosing a protocol.

## 3. Ignoring the 0-RTT Security Caveat (Replay Attacks)
* **Failure Signal:** Touting QUIC/TLS 1.3's 0-RTT as a magical latency cure without mentioning security risks.
* **Root Cause:** Focusing purely on performance while ignoring cryptographic side effects. 0-RTT data can be intercepted and replayed by an attacker because the server hasn't established freshness yet.
* **Mitigation:** Explicitly state that 0-RTT must only be used for idempotent requests (e.g., standard GET requests for static assets), never for state-mutating requests (e.g., POSTing a payment).
* **Validation Signal:** The candidate adds a caveat about idempotency when discussing 0-RTT session resumption.

## 4. Overlooking Corporate Firewall and UDP Blocking
* **Failure Signal:** Designing a B2B application that relies exclusively on HTTP/3 and failing to provide a fallback strategy.
* **Root Cause:** Assuming the public internet acts the same as corporate or restricted networks. Many enterprise firewalls aggressively drop non-DNS UDP traffic for security reasons, breaking QUIC connections.
* **Mitigation:** Design systems to attempt HTTP/3 via `Alt-Svc` headers but seamlessly gracefully fallback to HTTP/2 over TCP if the UDP handshake fails or times out.
* **Validation Signal:** The candidate discusses `Alt-Svc` headers or graceful degradation paths when deploying HTTP/3 to production.
