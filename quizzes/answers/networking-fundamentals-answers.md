# Networking Fundamentals Answers

## Question 1

1. **B** - Layer 3 (Network)

**Explanation:** Layer 3 (the Network layer) is responsible for logical addressing (e.g., IP addresses) and routing packets across multiple different networks to their final destination.
**Distractor breakdowns:** Option A is incorrect because Layer 2 (Data Link) handles node-to-node frame delivery within the same local network using MAC addresses. Option C is incorrect because Layer 4 (Transport) handles host-to-host data transfer and reliability. Option D is incorrect because Layer 7 interfaces directly with end-user applications.

## Question 2

2. **D** - It provides a unique hardware identifier for a network interface card at the Data Link layer

**Explanation:** A Media Access Control (MAC) address is a unique identifier assigned to a network interface controller (NIC) for communications at the Data Link layer (Layer 2) of a network segment. It is used for local delivery of frames within a single network.
**Distractor breakdowns:** Option A describes routing, which is handled by IP addresses (Layer 3). Option B describes port numbers (Layer 4). Option C describes a TLS certificate (Layer 7).

## Question 3

3. **B** - To map an IP address to a physical MAC address on a local network

**Explanation:** The Address Resolution Protocol (ARP) operates at Layer 2/3 and is used to resolve a known network layer address (like an IPv4 address) into an unknown data link layer address (MAC address) on a local network segment.
**Distractor breakdowns:** Option A describes DNS. Option C describes DHCP. Option D describes the function of an IP router.

## Question 4

4. **D** - IPv6 uses 128-bit addresses, vastly increasing the available address space compared to IPv4's 32-bit addresses

**Explanation:** IPv4 uses 32-bit addresses, limiting the internet to approximately 4.3 billion unique IPs. IPv6 uses 128-bit addresses, providing a vastly larger address space to accommodate the growing number of connected devices.
**Distractor breakdowns:** Option A is incorrect because IPv6 heavily relies on DNS (using AAAA records). Option B is incorrect; they are not directly inter-compatible and require translation (like NAT64). Option C is incorrect because IPv6 still uses both TCP and UDP.

## Question 5

5. **C** - Layer 4 (Transport)

**Explanation:** TCP is a transport layer protocol that provides reliable delivery of a stream of bytes. It operates at Layer 4 of the OSI model, above the network layer (IP) and below the application layer.
**Distractor breakdowns:** Option A is incorrect because Layer 2 handles MAC addressing and frames. Option B is incorrect because Layer 3 is IP. Option D is incorrect because Layer 7 handles application-specific protocols like HTTP.

## Question 6

6. **B** - SYN, SYN-ACK, ACK

**Explanation:** The TCP 3-way handshake involves three steps: 1) The client sends a SYN (synchronize) packet. 2) The server responds with a SYN-ACK (synchronize-acknowledge). 3) The client sends an ACK (acknowledge). This establishes the connection and synchronizes sequence numbers.
**Distractor breakdowns:** Options A, C, and D list incorrect packet sequences or incorporate FIN, which is used for termination, not initialization.

## Question 7

7. **C** - They allow the receiver to reassemble packets in the correct order and identify missing packets

**Explanation:** TCP assigns a sequence number to every byte of data sent. This allows the receiver to reassemble packets in the correct order, even if they arrive out of sequence. It also allows the receiver to identify missing packets and request retransmission.
**Distractor breakdowns:** Option A is incorrect; sequence numbers do not provide QoS prioritization. Option B is incorrect; they do not encrypt payloads. Option D is incorrect; segment size is determined by MSS, not sequence numbers.

## Question 8

8. **D** - A sliding window mechanism where the receiver advertises its available buffer space

**Explanation:** TCP flow control ensures a fast sender does not overwhelm a slow receiver. It uses a sliding window mechanism where the receiver includes a 'window size' value in its ACK packets, advertising its available buffer space. The sender will not send more unacknowledged data than this window size.
**Distractor breakdowns:** Option A is incorrect; routers do not enforce hard byte limits per TCP spec for flow control. Option B is for congestion control, not flow control. Option C is a rate-limiting algorithm, not TCP flow control.

## Question 9

9. **C** - A 4-way handshake using FIN and ACK packets

**Explanation:** A graceful TCP connection termination involves a 4-way handshake. When one side is done sending data, it sends a FIN packet. The other side acknowledges (ACK) this FIN, then sends its own FIN when it is done, which is subsequently acknowledged (ACK) by the first side.
**Distractor breakdowns:** Option A describes an abrupt, forceful termination (RST), not a graceful one. Option B is an error state. Option D describes the 3-way initialization handshake, not termination.

## Question 10

10. **A** - It contains no sequence numbers or acknowledgment fields

**Explanation:** UDP is a minimal, connectionless transport protocol. Unlike TCP, UDP datagrams do not contain sequence numbers or acknowledgment fields, meaning there is no mechanism to guarantee delivery or ordering.
**Distractor breakdowns:** Options B, C, and D describe features of TCP (flow control, connection establishment, guaranteed ordering), not UDP.

## Question 11

11. **C** - It directs the recursive resolver to the appropriate Top-Level Domain (TLD) server

**Explanation:** The Root Name Server is the first step in translating hostnames to IP addresses. It responds to the recursive resolver by directing it to the appropriate Top-Level Domain (TLD) server (e.g., the .com or .org server) based on the query.
**Distractor breakdowns:** Option A describes the Authoritative Name Server. Option B describes a recursive resolver or local cache. Option D also describes an Authoritative Name Server.

## Question 12

12. **A** - It provides the definitive answer for the IP address of a specific domain

**Explanation:** The Authoritative Name Server is the final step in the DNS resolution process. It holds the actual DNS records (like A, AAAA, CNAME) for a specific domain name and provides the definitive (authoritative) answer to the resolver.
**Distractor breakdowns:** Option B describes the root server. Option C describes specific TLD servers. Option D describes the recursive resolver.

## Question 13

13. **C** - Resolvers cache responses for a duration specified by the record's TTL (Time To Live)

**Explanation:** DNS heavily relies on caching to reduce latency. When a DNS record is returned, it includes a TTL (Time To Live) value, which specifies how many seconds the response should be cached before the resolver must query the authoritative server again.
**Distractor breakdowns:** Option A is incorrect; root servers do not cache all global queries. Option B is incorrect; authoritative servers answer queries but don't cache client IPs to pre-fetch. Option D is incorrect; caching indefinitely would break dynamic IP updates.

## Question 14

14. **B** - TLS (Transport Layer Security)

**Explanation:** TLS (Transport Layer Security) is the standard cryptographic protocol used to secure web communications (HTTPS). It provides encryption, authentication (usually via certificates), and data integrity.
**Distractor breakdowns:** Option A secures shell access, not general web traffic. Option C operates at the network layer (e.g., for VPNs). Option D is unencrypted file transfer.

## Question 15

15. **D** - It reduces the handshake from two round-trips to one round-trip (1-RTT) in most cases

**Explanation:** TLS 1.3 significantly improves performance by reducing the initial handshake from two round-trips (2-RTT) down to one round-trip (1-RTT) in most cases, accelerating connection setup.
**Distractor breakdowns:** Option A is incorrect; TLS 1.3 removes (rather than adds) insecure MD5/SHA-1. Option B is incorrect; it reduces RTT, it doesn't increase it. Option C is incorrect; it removes static RSA in favor of forward secrecy (e.g., Ephemeral Diffie-Hellman).

## Question 16

16. **D** - It allows multiple requests and responses to be sent concurrently over a single TCP connection

**Explanation:** HTTP/2 multiplexing allows multiple requests and responses to be interleaved and sent concurrently over a single TCP connection. This mitigates the HTTP/1.1 issue where requests had to be processed sequentially or required multiple TCP connections.
**Distractor breakdowns:** Option A describes HTTP/3 (QUIC). Option B describes HTTP/1.1 workarounds. Option C is true of HTTP/2 but describes header compression, not multiplexing.

## Question 17

17. **B** - The server preemptively sending resources to the client that it anticipates the client will need

**Explanation:** HTTP/2 Server Push allows a server to preemptively send resources (like CSS or JavaScript files) to the client's cache before the client explicitly requests them, anticipating that the client will need them to render the page.
**Distractor breakdowns:** Options A, C, and D are unrelated to the HTTP/2 Server Push feature.

## Question 18

18. **A** - It occurs when a lost packet delays the delivery of subsequent packets, even if they belong to different logical streams

**Explanation:** TCP Head-of-Line (HoL) blocking occurs because TCP guarantees in-order delivery of bytes. If a packet is lost, TCP buffers all subsequent packets until the missing one is retransmitted and received. In HTTP/2, this means a single packet loss stalls all multiplexed streams on that connection.
**Distractor breakdowns:** Option B is unrelated. Option C is incorrect; HTTP/2 suffers from TCP HoL blocking (which is why HTTP/3 was created). Option D is incorrect; UDP does not guarantee order and thus does not suffer from TCP HoL blocking.

## Question 19

19. **B** - UDP, to enable user-space congestion control and eliminate TCP HoL blocking

**Explanation:** HTTP/3 uses QUIC, which is built on top of UDP. By using UDP, QUIC bypasses the OS kernel's TCP stack, allowing it to implement its own user-space congestion control, manage independent streams, and completely eliminate TCP Head-of-Line blocking.
**Distractor breakdowns:** Option A is incorrect; it uses UDP. Option C is incorrect; SCTP is not used for HTTP/3. Option D is incorrect; ICMP is for diagnostics (e.g., ping).

## Question 20

20. **D** - It reduces overall connection establishment latency

**Explanation:** In traditional HTTPS, the TCP handshake and TLS handshake are separate, taking 2-3 round trips. QUIC integrates the transport and cryptographic handshakes, allowing them to occur simultaneously. This reduces connection establishment latency to 1-RTT for new connections.
**Distractor breakdowns:** Option A is incorrect; certificates are still required. Option B is incorrect; it doesn't prevent all DDoS. Option C is incorrect; QUIC still runs over IP.

## Question 21

21. **C** - It allows sending encrypted data in the first flight to a known server; the trade-off is vulnerability to replay attacks

**Explanation:** 0-RTT resumption in TLS 1.3 allows a client to send encrypted application data on the very first round trip if it has communicated with the server previously. The primary trade-off is vulnerability to replay attacks, as an attacker could capture and resend the 0-RTT packet.
**Distractor breakdowns:** Options A, B, and D invent incorrect mechanisms and trade-offs unrelated to TLS 1.3 0-RTT.

## Question 22

22. **B** - By reacting to packet loss events (e.g., duplicate ACKs or timeouts)

**Explanation:** TCP CUBIC is a loss-based congestion control algorithm. It increases its congestion window using a cubic function but determines that congestion has occurred and reduces its window only when it detects packet loss, typically via duplicate ACKs or timeouts.
**Distractor breakdowns:** Option A describes delay-based algorithms (like Vegas). Option C describes BBR. Option D is incorrect as it ignores standard packet loss metrics.

## Question 23

23. **D** - BBR

**Explanation:** BBR (Bottleneck Bandwidth and Round-trip propagation time) builds a model of the network path by continuously estimating the bottleneck bandwidth and the round-trip time, rather than relying solely on packet loss like older algorithms.
**Distractor breakdowns:** Options A (Tahoe), B (Reno), and C (CUBIC) are loss-based congestion control algorithms.

## Question 24

24. **A** - Occasional packet loss is acceptable, but delays caused by TCP retransmissions are not

**Explanation:** In live video streaming, timeliness is paramount. If a video frame is lost, it's better to skip it and play the next frame rather than stall the video waiting for a TCP retransmission. UDP avoids the latency introduced by TCP's connection overhead and retransmissions.
**Distractor breakdowns:** Option B is incorrect; UDP does not compress data. Option C is incorrect; UDP does not encrypt data. Option D is incorrect; ISPs do not universally throttle TCP over UDP.

## Question 25

25. **B** - TCP congestion control operates purely host-to-host and cannot enforce application-level business rules (like user API quotas) across a distributed cluster

**Explanation:** TCP congestion control manages the flow of packets host-to-host to prevent network collapse, but it has no knowledge of application semantics like user IDs, API keys, or pricing tiers. A distributed rate limiter (like Token Bucket in Redis) is required to enforce business-level API quotas across a cluster of application servers.
**Distractor breakdowns:** Option A is incorrect; Redis does not guarantee exactly-once delivery of HTTP requests. Option C is incorrect; TCP works over IPv4 and IPv6. Option D is completely nonsensical.

## Question 26

26. **C** - It abstracts reliable network communication, observability, and security away from the application code by injecting a sidecar proxy alongside each service instance.

**Explanation:** A Service Mesh operates at the application and transport layers (L7/L4) to manage service-to-service communication within a cluster. By using sidecar proxies, it handles retries, mTLS encryption, tracing, and advanced load balancing, freeing developers from implementing these networking concerns directly in their application code.
**Distractor breakdowns:** Option A describes Software-Defined Networking (SDN) infrastructure, not a service mesh. Option B describes an API Gateway or a traditional reverse proxy, but service meshes primarily focus on internal, east-west traffic, and certainly shouldn't route external users directly to databases. Option D describes a Content Delivery Network (CDN).

## Question 27

27. **B** - WebSockets establish a single persistent TCP connection for continuous, low-overhead bidirectional data frames, whereas Long Polling incurs the overhead of establishing new HTTP requests for each server-to-client message.

**Explanation:** WebSockets upgrade a standard HTTP connection into a persistent, full-duplex TCP connection, eliminating the HTTP header overhead for subsequent messages and allowing true real-time communication. HTTP Long Polling requires the client to repeatedly open new HTTP requests, holding them open until the server responds, which adds significant latency and overhead when reconnecting.
**Distractor breakdowns:** Option A is incorrect because WebSockets run over TCP, not UDP. Option C is incorrect because both WebSockets (WSS) and Long Polling (HTTPS) rely on TLS for encryption; the WebSocket protocol itself doesn't provide it. Option D is incorrect because WebSockets still require standard DNS resolution for domain names.

## Question 28

28. **C** - It prevents routing loops by recording the sequence of ASes a route has traversed, and is used for route selection

**Explanation:** BGP uses the AS Path attribute primarily to detect and prevent routing loops. When a BGP router receives a route advertisement containing its own AS number in the AS Path, it rejects the route. The AS Path length is also a key metric used in BGP's best-path selection algorithm.
**Distractor breakdowns:** Option A is incorrect because standard BGP does not intrinsically encrypt routing updates (though extensions like RPKI help with security/origin validation, they are not the AS Path). Option B is incorrect; BGP is a path-vector protocol focused on policy and AS hops, not physical geographical distance. Option D is incorrect; IP address assignment is handled by Regional Internet Registries (RIRs), not by BGP attributes.
