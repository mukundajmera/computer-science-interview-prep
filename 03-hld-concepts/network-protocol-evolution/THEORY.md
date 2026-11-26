# Network Protocol Evolution

## Evolution Timeline

*   **HTTP/1.0**: Single request per TCP connection. Once the response was delivered, the connection was closed. This resulted in high overhead for establishing TCP handshakes and slow start penalties for every single resource.
*   **HTTP/1.1**: Introduced **persistent connections** (`Connection: keep-alive`), allowing multiple sequential requests over a single TCP connection. However, it still suffered from HTTP-layer Head-of-Line (HoL) blocking, meaning requests had to be processed sequentially; a slow request blocked all subsequent requests on that connection. Pipelining was introduced but rarely supported or successful due to proxy issues.
*   **HTTP/2**: Solved HTTP-layer HoL blocking by introducing **binary framing** and **multiplexing**. Multiple streams can be sent simultaneously over a single TCP connection. It uses HPACK for header compression and supports Server Push. However, it relies on TCP, which means it suffers from **TCP-layer HoL blocking**: if a single TCP packet is lost, all multiplexed streams are blocked until that packet is retransmitted and acknowledged, because TCP guarantees in-order delivery.
*   **HTTP/3 (QUIC)**: Replaces TCP with **QUIC** (Quick UDP Internet Connections), a transport layer built on top of UDP. QUIC handles multiplexing, encryption (TLS 1.3 is built-in), and congestion control itself. It completely eliminates HoL blocking across streams because streams are independent: a lost packet only delays the specific stream it belongs to, while other streams continue to process.

## Head-of-Line (HoL) Blocking Breakdown

*   **HTTP/1.1 (HTTP-layer HoL blocking)**: Requests are processed strictly sequentially on a single connection. If a large image request is sent first, the subsequent small CSS file request cannot be sent or processed until the image finishes.
*   **HTTP/2 (TCP-layer HoL blocking)**: Multiplexes streams over one TCP connection. If packet 3 (belonging to Stream A) is lost, and packet 4 (belonging to Stream B) arrives, TCP will buffer packet 4 and not deliver it to the application layer until packet 3 is retransmitted. Stream B is unfairly delayed by Stream A's packet loss.
*   **HTTP/3 QUIC (Zero-HoL blocking)**: Built on UDP, multiplexing is handled by QUIC. If a UDP datagram containing data for Stream A is lost, only Stream A is blocked waiting for retransmission. Stream B's data arriving in subsequent datagrams is immediately delivered to the application because QUIC manages streams independently without a global in-order constraint.

## Connection Handshake & Latency

*   **TCP + TLS 1.3 (2-RTT)**: Establishing a secure connection traditionally requires 1 Round Trip Time (RTT) for the TCP handshake (SYN, SYN-ACK, ACK), followed by another 1 RTT for the TLS 1.3 handshake, totaling 2-RTT before application data can be sent. (With older TLS 1.2, it was 3-RTT).
*   **QUIC (1-RTT or 0-RTT)**: QUIC combines the transport and cryptographic handshakes.
    *   **Initial Handshake (1-RTT)**: The client sends connection parameters and TLS client hello in the very first packet. The server responds with transport parameters and TLS server hello. Data can be sent immediately after.
    *   **Session Resumption (0-RTT)**: If the client has previously connected to the server, it can use cached cryptographic material to send application data in the very first packet (along with the handshake), achieving 0-RTT latency. This is crucial for mobile performance.

## Connection Migration

In traditional TCP, a connection is identified by a 4-tuple: `(Source IP, Source Port, Destination IP, Destination Port)`. If a mobile device switches from a Wi-Fi network to a cellular network, its Source IP changes. This breaks the TCP connection, requiring a complete renegotiation (handshakes, slow start), causing noticeable delays or dropped calls.

**QUIC solves this using a 64-bit Connection ID**. The connection is identified by this ID rather than the 4-tuple. When a mobile device changes its IP address, it simply continues sending QUIC packets with the same Connection ID from the new IP. The server recognizes the ID and seamlessly migrates the connection without any handshakes or interruptions.

## Modern Protocol Matrix

| Protocol | Transport | Model | Key Features | Best Use Cases |
| :--- | :--- | :--- | :--- | :--- |
| **HTTP/1.1** | TCP | Request-Response | Ubiquitous, simple | Legacy APIs, static websites |
| **HTTP/2** | TCP | Multiplexed | Binary framing, Header compression | Modern web apps, APIs |
| **gRPC** | HTTP/2 (TCP) | RPC | Protobuf, bi-directional streaming, strongly typed | Microservices communication, polyglot environments |
| **WebSockets** | TCP | Full-Duplex | Persistent connection, low overhead after handshake | Chat apps, live gaming, real-time trading |
| **Server-Sent Events (SSE)** | HTTP (TCP) | Unidirectional Push | Server-to-client streaming, auto-reconnect | Live feeds, notifications, LLM token streaming |
| **HTTP/3 (QUIC)** | UDP | Multiplexed | 0-RTT, Connection Migration, No HoL blocking | Mobile apps, unreliable networks, video streaming |

## Scoring Rubric

| Dimension | Weight | Strong Signal |
| :--- | :--- | :--- |
| **Protocol Evolution** | 20% | Accurately describes the transition from HTTP/1.1 to HTTP/2 to HTTP/3 and the specific problems each version solved. |
| **HoL Blocking Analysis** | 30% | Deeply understands the difference between HTTP-layer HoL blocking (HTTP/1.1) and TCP-layer HoL blocking (HTTP/2), and how QUIC solves it natively via independent UDP streams. |
| **Handshake Latency** | 20% | Can articulate the RTT savings of QUIC's combined handshake and explain the mechanics and risks of 0-RTT session resumption. |
| **Connection Migration** | 10% | Explains the 4-tuple problem of TCP and how QUIC's Connection ID allows seamless network handover for mobile clients. |
| **Protocol Selection** | 20% | Correctly matches modern protocols (gRPC, WebSockets, SSE) to specific use cases, citing trade-offs like directionality, overhead, and transport characteristics. |

## Performance Bands

*   **Strong (5)**: Masterful understanding of transport protocols. Flawlessly compares HTTP/2 and HTTP/3. Can analyze edge cases like 0-RTT replay attacks and accurately select protocols for nuanced real-world scenarios.
*   **Average (3)**: Understands the basic evolution and the concept of HoL blocking. Knows that QUIC uses UDP and is faster. Can map common protocols to standard use cases.
*   **Weak (1)**: Confuses HTTP and TCP layer issues. Unclear on why HTTP/2 still suffers from HoL blocking. Cannot clearly articulate the differences between WebSockets and SSE.

## Common Pitfalls

1.  **Claiming HTTP/2 solved all HoL blocking**: A very common mistake. HTTP/2 only solved HTTP-layer HoL blocking. It introduced TCP-layer HoL blocking because all streams are multiplexed over a single TCP connection.
    *   *Mitigation*: Always distinguish between HTTP-layer and transport-layer blocking.
2.  **Misunderstanding 0-RTT security**: Failing to mention that 0-RTT in QUIC/TLS 1.3 is susceptible to replay attacks. It should only be used for idempotent requests (e.g., GET requests).
    *   *Mitigation*: When discussing 0-RTT, immediately caveat it with the replay attack risk.
3.  **Using WebSockets for everything real-time**: Proposing WebSockets for simple unidirectional server-to-client updates when Server-Sent Events (SSE) would be lighter, simpler, and naturally support auto-reconnection over standard HTTP.
    *   *Mitigation*: Ask about the directionality of the data flow before choosing between WebSockets and SSE.
4.  **Assuming QUIC is always faster**: Ignoring the fact that some corporate firewalls block unknown UDP traffic, forcing fallbacks to TCP/HTTP/2.

## Follow-up Questions

1.  **Explain the security implications of 0-RTT session resumption in QUIC. How do you prevent replay attacks?**
2.  **If you are building a real-time collaborative document editor (like Google Docs), would you choose WebSockets or gRPC? Why?**
3.  **How does QUIC handle congestion control given that it is built on top of UDP, which has no native congestion control?**
4.  **Describe how Server-Sent Events (SSE) work over an HTTP connection. How does it handle reconnections compared to WebSockets?**
5.  **Why did the industry choose to build QUIC on top of UDP rather than creating an entirely new IP protocol layer?**
