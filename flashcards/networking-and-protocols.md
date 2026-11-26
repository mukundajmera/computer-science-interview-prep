
# Networking and Protocols Flashcards

40 question-only flashcards for networking and protocols interview execution.

---

## HTTP Evolution (10 Cards)

### Card 1
Front: What was the primary limitation of HTTP/1.0 regarding TCP connections?

### Card 2
Front: How did HTTP/1.1 attempt to solve the connection overhead of HTTP/1.0?

### Card 3
Front: What is HTTP-layer Head-of-Line (HoL) blocking in the context of HTTP/1.1?

### Card 4
Front: Why was HTTP pipelining in HTTP/1.1 rarely successful in practice?

### Card 5
Front: How does HTTP/2 solve HTTP-layer HoL blocking?

### Card 6
Front: What is the purpose of HPACK in HTTP/2?

### Card 7
Front: What is Server Push in HTTP/2?

### Card 8
Front: Despite multiplexing, what type of Head-of-Line blocking does HTTP/2 still suffer from?

### Card 9
Front: Why does HTTP/2 suffer from TCP-layer HoL blocking?

### Card 10
Front: What fundamental transport protocol does HTTP/3 (QUIC) use instead of TCP?

## QUIC and HTTP/3 (10 Cards)

### Card 11
Front: How does QUIC completely eliminate Head-of-Line blocking across streams?

### Card 12
Front: What cryptographic protocol is built directly into QUIC?

### Card 13
Front: How many Round Trip Times (RTT) are required for a standard TCP + TLS 1.3 handshake?

### Card 14
Front: How does QUIC achieve a 1-RTT initial handshake?

### Card 15
Front: What is 0-RTT session resumption in QUIC?

### Card 16
Front: What is the primary security risk associated with 0-RTT session resumption in QUIC?

### Card 17
Front: What type of requests are safe to send during a 0-RTT resumption?

### Card 18
Front: In traditional TCP, what 4-tuple identifies a connection?

### Card 19
Front: Why do mobile networks cause issues for traditional TCP connections during handovers?

### Card 20
Front: How does QUIC's 64-bit Connection ID enable seamless connection migration?

## Modern Protocols Comparison (10 Cards)

### Card 21
Front: What is the primary difference in directionality between WebSockets and Server-Sent Events (SSE)?

### Card 22
Front: Which protocol is better suited for a real-time trading application: SSE or WebSockets?

### Card 23
Front: How does Server-Sent Events (SSE) handle reconnections compared to WebSockets?

### Card 24
Front: What underlying protocol does gRPC use for transport?

### Card 25
Front: What serialization format is typically used with gRPC?

### Card 26
Front: Why might gRPC be preferred over REST for internal microservices communication?

### Card 27
Front: What are the main limitations of using gRPC directly from a web browser?

### Card 28
Front: In what scenario might a corporate firewall force a fallback from HTTP/3 to HTTP/2?

### Card 29
Front: Why was QUIC built on top of UDP rather than creating an entirely new IP protocol layer?

### Card 30
Front: What are the overhead characteristics of WebSockets after the initial HTTP handshake is complete?

## Deep Dives and Trade-offs (10 Cards)

### Card 31
Front: How does QUIC handle congestion control if UDP has no native congestion control mechanisms?

### Card 32
Front: What is the difference in how HTTP/2 and HTTP/3 handle stream prioritization?

### Card 33
Front: Why is HTTP/3 particularly advantageous for mobile users on unreliable networks?

### Card 34
Front: Can you describe a scenario where Server-Sent Events (SSE) is preferable to WebSockets for LLM token streaming?

### Card 35
Front: What happens to a multiplexed HTTP/2 connection if a single TCP packet is dropped?

### Card 36
Front: What happens to a multiplexed HTTP/3 connection if a single UDP datagram is dropped?

### Card 37
Front: How does HTTP/1.1 persistent connections (`Connection: keep-alive`) impact server resource utilization?

### Card 38
Front: What is the role of the TLS 1.3 server hello in the QUIC handshake process?

### Card 39
Front: Why are older APIs often left on HTTP/1.1 instead of upgrading to HTTP/2 or HTTP/3?

### Card 40
Front: What are the implications of QUIC encrypting almost all packet headers compared to TCP?
