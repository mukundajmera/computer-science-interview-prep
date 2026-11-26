# Network Protocol Evolution - Interview Q&A

## 1. Protocol Selection: Real-Time Trading Platform

**Q: You are designing the market data feed for a high-frequency trading application. Clients need sub-millisecond updates for stock prices. Which protocol do you choose: WebSockets, Server-Sent Events (SSE), or HTTP short polling?**

**A:** I would choose **WebSockets**.
*   **Why WebSockets?** Once the initial HTTP handshake is complete, WebSockets provide a persistent, full-duplex TCP connection with very minimal framing overhead (just a few bytes per message). This is critical for minimizing latency in high-frequency trading.
*   **Why not SSE?** While SSE is great for server-to-client push, it relies on HTTP. It has slightly more overhead per message than WebSockets due to HTTP headers/chunking, and it is strictly unidirectional. If clients need to quickly subscribe/unsubscribe to specific ticker symbols dynamically, WebSockets' bidirectional nature handles this more elegantly over the same connection.
*   **Why not Short Polling?** Unacceptable overhead. Creating a new TCP/TLS connection (or even reusing a keep-alive connection with full HTTP headers) for every price tick would overwhelm the server and introduce massive latency.

## 2. Protocol Selection: Live Streaming LLM Tokens

**Q: You are building a ChatGPT clone. When a user sends a prompt, the server generates the response token by token. Which protocol should you use to stream these tokens back to the browser?**

**A:** I would choose **Server-Sent Events (SSE)**.
*   **Why SSE?** The data flow is strictly unidirectional (server pushing tokens to the client) after the initial prompt (which is just a standard HTTP POST request). SSE is designed exactly for this. It runs over standard HTTP, uses the `text/event-stream` content type, and is natively supported by the browser's `EventSource` API, making implementation trivial.
*   **Why not WebSockets?** WebSockets provide full-duplex communication, which is unnecessary here since the client only listens after sending the prompt. WebSockets also require custom proxy configurations for load balancing (maintaining sticky sessions/long-lived connections) and handle reconnections manually, whereas SSE is standard HTTP and the browser handles reconnections automatically.

## 3. Head-of-Line Blocking in HTTP/2

**Q: HTTP/2 introduced multiplexing to solve Head-of-Line (HoL) blocking. Did it succeed? Explain the nuance.**

**A:** It only partially succeeded. It solved **HTTP-layer HoL blocking**, but exposed **TCP-layer HoL blocking**.
*   In HTTP/1.1, if a client requested a large image and then a small CSS file on the same connection, the CSS file was blocked until the image finished downloading (HTTP HoL blocking).
*   HTTP/2 solved this by multiplexing both requests into independent "streams" of binary frames over a single TCP connection.
*   However, TCP guarantees in-order delivery of packets. If a TCP packet containing a frame for the large image is lost on the network, the OS will buffer all subsequent packets (even those containing the CSS file frames) until the lost packet is retransmitted. Thus, the CSS stream is unfairly delayed by packet loss in the image stream. This is TCP-layer HoL blocking.

## 4. How HTTP/3 (QUIC) Solves HoL Blocking

**Q: How does HTTP/3 solve the TCP-layer HoL blocking problem found in HTTP/2?**

**A:** HTTP/3 replaces TCP with **QUIC**, which is built on top of **UDP**.
*   UDP is a datagram protocol; it does not guarantee in-order delivery.
*   QUIC implements multiplexing and reliability in the application/user space rather than relying on the kernel's TCP stack.
*   In QUIC, streams are completely independent. If a UDP packet containing data for Stream A is lost, only Stream A is blocked waiting for retransmission. If subsequent UDP packets contain data for Stream B, QUIC immediately delivers Stream B's data to the application. This achieves true Zero-HoL blocking across streams.

## 5. Mobile Connection Reliability (Connection Migration)

**Q: A user is watching a video stream on their phone while walking out of their house, transitioning from Wi-Fi to a 5G cellular network. How does HTTP/3 handle this compared to HTTP/2?**

**A:** HTTP/3 provides a seamless transition due to **Connection Migration**, whereas HTTP/2 will drop the connection.
*   **HTTP/2 (TCP):** A TCP connection is tied to the 4-tuple (Source IP, Source Port, Dest IP, Dest Port). When switching to 5G, the phone's Source IP changes. The TCP connection breaks. The app must detect the failure, establish a new TCP handshake, a new TLS handshake, and suffer TCP slow-start again. The video rebuffers.
*   **HTTP/3 (QUIC):** QUIC identifies connections using a 64-bit **Connection ID** embedded in the packet header, independent of the IP address. When the IP changes, the client simply continues sending QUIC packets with the same Connection ID from the new IP. The server recognizes the ID and seamlessly updates the address mapping without renegotiating the handshakes or resetting congestion control. The video continues without interruption.

## 6. The 0-RTT Security Trade-off

**Q: QUIC supports 0-RTT session resumption, allowing data to be sent in the very first packet. What is the major security risk associated with 0-RTT, and how do we mitigate it?**

**A:** The major risk is **Replay Attacks**.
*   **The Risk:** In 0-RTT, the client encrypts data using keys from a previous session. Because the server hasn't yet provided a fresh random nonce (which happens in the 1-RTT handshake), an attacker who intercepts this packet can simply copy it and send it to the server multiple times ("replay" it). The server will successfully decrypt it and process it multiple times.
*   **Mitigation:** 0-RTT must **only be used for idempotent requests** (e.g., HTTP GET requests for static assets where duplicate requests have no adverse effect). It must never be used for state-mutating requests (e.g., an HTTP POST to transfer money), as a replay attack would execute the transfer multiple times.

## 7. Overcoming Middlebox Ossification

**Q: If TCP has limitations, why didn't the creators of QUIC just design a brand new transport protocol (like TCP or UDP) directly on top of IP, rather than building on top of UDP?**

**A:** The reason is **Middlebox Ossification**.
*   The internet is filled with middleboxes (firewalls, NAT routers, load balancers). Over decades, these devices have been hardcoded to only recognize and route TCP and UDP traffic.
*   If you invent a brand new protocol (e.g., protocol number 143 on top of IP), 99% of the routers on the internet will simply drop the packets because they don't recognize the protocol header.
*   To deploy a new protocol globally, it had to be disguised as existing traffic. By wrapping QUIC inside standard UDP packets, middleboxes forward it without issues.

## 8. gRPC vs REST for Internal Microservices

**Q: You are migrating a monolithic application to microservices. For synchronous service-to-service communication, would you choose REST (JSON over HTTP/1.1) or gRPC?**

**A:** I would strongly lean toward **gRPC** for internal communication.
*   **Performance:** gRPC uses Protocol Buffers (Protobuf), a highly compressed binary format, which is much faster to serialize/deserialize than JSON. It also runs on HTTP/2 by default, benefiting from multiplexing.
*   **Strong Typing:** Protobuf enforces strict contracts (schemas) between services. This prevents the runtime errors common with loosely-typed JSON payloads.
*   **Code Generation:** gRPC automatically generates client and server stubs in multiple languages, saving development time.
*   *Note:* I would still use REST/GraphQL for external-facing APIs where human readability and broad client compatibility (browsers) are more important.

## 9. Handling Large File Uploads

**Q: How would you design a system to upload a 50GB 4K video file from a client to an S3 bucket? What protocol features are relevant here?**

**A:** I would use **Multipart Uploads over HTTP** (specifically HTTP/2 or HTTP/3).
1.  **Chunking:** The client splits the 50GB file into smaller chunks (e.g., 10MB each).
2.  **Parallel Uploads:** Using HTTP/2 or HTTP/3 multiplexing, the client can upload multiple chunks simultaneously over the same connection, maximizing bandwidth utilization without the overhead of multiple TCP handshakes.
3.  **Resiliency:** If a connection drops, the client only needs to retry the specific 10MB chunks that failed, rather than restarting the entire 50GB upload.
4.  **Pre-signed URLs:** To save server bandwidth, the backend generates S3 Pre-signed URLs for each chunk, allowing the client to upload directly to S3 via HTTP PUT requests.

## 10. Fallback Strategies for HTTP/3

**Q: You decide to enable HTTP/3 for your mobile application. Since it relies on UDP, what happens if the user is on a corporate Wi-Fi network that blocks all UDP traffic?**

**A:** We must implement a robust fallback mechanism.
*   **Alt-Svc Header:** The initial connection usually happens over standard TCP (HTTP/1.1 or HTTP/2). The server responds with an `Alt-Svc` (Alternative Service) header indicating it supports HTTP/3 on a specific UDP port.
*   **Racing:** The client will then attempt to open a QUIC connection in the background while continuing to use the TCP connection.
*   **Fallback:** If the UDP handshake times out or is explicitly rejected (ICMP unreachable) due to the firewall, the client abandons the QUIC attempt and simply continues using the established HTTP/2-over-TCP connection. The user experiences no failure, only slightly higher latency.
