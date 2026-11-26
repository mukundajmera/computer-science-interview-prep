# Networking Fundamentals Quiz

27 questions focused on networking fundamentals, progressing from core concepts to applied trade-offs.

Time: 35 minutes
Difficulty: Medium-Hard

---

## Section 1: Network Layer and Fundamentals

### Question 1
In the OSI model, which layer is responsible for routing packets between different networks?

A) Layer 2 (Data Link)
B) Layer 3 (Network)
C) Layer 4 (Transport)
D) Layer 7 (Application)

### Question 2
What role does the MAC address play in networking?

A) It determines the shortest path across the global internet to a destination
B) It identifies the application process running on a host via a port number
C) It establishes a secure cryptographic identity for a server
D) It provides a unique hardware identifier for a network interface card at the Data Link layer

### Question 3
What is the primary function of the Address Resolution Protocol (ARP)?

A) To map a domain name to an IP address across the internet
B) To map an IP address to a physical MAC address on a local network
C) To automatically assign IP addresses to devices on a network
D) To route packets between different subnets

### Question 4
Which of the following is true regarding IPv4 and IPv6?

A) IPv6 removes the need for DNS infrastructure
B) IPv4 and IPv6 devices can communicate directly without any translation mechanisms
C) IPv6 completely replaces TCP with UDP for all internet traffic
D) IPv6 uses 128-bit addresses, vastly increasing the available address space compared to IPv4's 32-bit addresses

## Section 2: Transport Layer

### Question 5
In the OSI model, at which layer does the TCP protocol operate?

A) Layer 2 (Data Link)
B) Layer 3 (Network)
C) Layer 4 (Transport)
D) Layer 7 (Application)

### Question 6
Which of the following best describes the standard TCP 3-way handshake?

A) SYN, ACK, FIN
B) SYN, SYN-ACK, ACK
C) SYN, ACK, SYN-ACK
D) ACK, SYN, SYN-ACK

### Question 7
How do TCP sequence numbers ensure reliability?

A) They determine the priority of packets for Quality of Service (QoS)
B) They encrypt the payload to prevent man-in-the-middle attacks
C) They allow the receiver to reassemble packets in the correct order and identify missing packets
D) They limit the maximum size of a TCP segment

### Question 8
Which flow control mechanism does TCP use to prevent the sender from overwhelming the receiver?

A) A hard limit of 1500 bytes per second enforced by the router
B) Explicit congestion notification (ECN) packets sent by intermediate switches
C) A token bucket filter that limits the sender's transmission rate
D) A sliding window mechanism where the receiver advertises its available buffer space

### Question 9
What happens during a graceful TCP connection termination?

A) A single RST packet is sent by the client
B) The server unilaterally drops the connection without notification
C) A 4-way handshake using FIN and ACK packets
D) A 3-way handshake using SYN and ACK packets

### Question 10
What is a primary characteristic of a UDP datagram?

A) It contains no sequence numbers or acknowledgment fields
B) It includes a built-in mechanism for flow control
C) It establishes a dedicated channel before transmitting data
D) It guarantees that packets will arrive in the order they were sent

## Section 3: Application Layer and DNS

### Question 11
In DNS resolution, what is the role of the Root Name Server?

A) It holds the final IP address mapping for all domains
B) It acts as a local cache for the client's DNS queries
C) It directs the recursive resolver to the appropriate Top-Level Domain (TLD) server
D) It manages the authoritative records for a specific domain

### Question 12
What does an Authoritative Name Server do in the DNS hierarchy?

A) It provides the definitive answer for the IP address of a specific domain
B) It serves as the entry point for all global DNS queries
C) It manages the .com, .org, and .net namespaces exclusively
D) It queries other DNS servers on behalf of the client

### Question 13
How does DNS handle caching to improve performance?

A) Root servers cache all queries globally to avoid database lookups
B) Authoritative servers cache client IPs to pre-fetch future requests
C) Resolvers cache responses for a duration specified by the record's TTL (Time To Live)
D) Browsers permanently cache IP addresses until the user clears them

### Question 14
Which protocol provides encryption, authentication, and data integrity for web traffic?

A) SSH (Secure Shell)
B) TLS (Transport Layer Security)
C) IPsec (Internet Protocol Security)
D) FTP (File Transfer Protocol)

### Question 15
What is a key improvement of TLS 1.3 over TLS 1.2?

A) It adds support for MD5 and SHA-1 hashing algorithms
B) It requires a minimum of 3-RTT for initial connection establishment
C) It introduces the RSA key exchange for better security
D) It reduces the handshake from two round-trips to one round-trip (1-RTT) in most cases

## Section 4: Advanced Protocols and Applied Trade-offs

### Question 16
How does HTTP/2 multiplexing improve upon HTTP/1.1?

A) It replaces TCP with UDP for faster data transmission
B) It uses multiple TCP connections to fetch resources in parallel
C) It compresses headers using HPACK to reduce bandwidth
D) It allows multiple requests and responses to be sent concurrently over a single TCP connection

### Question 17
In the context of HTTP/2, what is server push?

A) A mechanism for uploading large files to the server asynchronously
B) The server preemptively sending resources to the client that it anticipates the client will need
C) A way for the server to update its own DNS records dynamically
D) The server forcing the client to close its TCP connection

### Question 18
Which of the following is true about TCP Head-of-Line (HoL) blocking?

A) It occurs when a lost packet delays the delivery of subsequent packets, even if they belong to different logical streams
B) It happens when a client sends too many concurrent DNS queries
C) It is completely eliminated in HTTP/2 due to multiplexing
D) It only affects UDP traffic on congested networks

### Question 19
Which underlying transport protocol does HTTP/3 (QUIC) use, and why?

A) TCP, to guarantee backwards compatibility with older network appliances
B) UDP, to enable user-space congestion control and eliminate TCP HoL blocking
C) SCTP, to provide multi-streaming at the network layer
D) ICMP, to reduce the overhead of connection handshakes entirely

### Question 20
What problem does QUIC solve by integrating the cryptographic handshake with the transport handshake?

A) It makes TLS certificates unnecessary for secure communication
B) It prevents all forms of distributed denial-of-service (DDoS) attacks
C) It allows QUIC to be routed over Layer 2 networks without IP
D) It reduces overall connection establishment latency

### Question 21
What is '0-RTT' in the context of TLS 1.3, and what is its primary security trade-off?

A) It eliminates DNS resolution; the trade-off is reduced fault tolerance
B) It removes encryption for faster speed; the trade-off is exposing payload data
C) It allows sending encrypted data in the first flight to a known server; the trade-off is vulnerability to replay attacks
D) It requires servers to reply within 0 milliseconds; the trade-off is high CPU usage

### Question 22
How does TCP CUBIC determine when to reduce its congestion window?

A) By measuring the delay gradient of RTT
B) By reacting to packet loss events (e.g., duplicate ACKs or timeouts)
C) By monitoring the bottleneck bandwidth continuously
D) By receiving explicit congestion notifications (ECN) only

### Question 23
Which congestion control algorithm builds a model of the network path based on bottleneck bandwidth and round-trip propagation time?

A) Tahoe
B) Reno
C) CUBIC
D) BBR

### Question 24
Why is UDP often preferred over TCP for live video streaming?

A) Occasional packet loss is acceptable, but delays caused by TCP retransmissions are not
B) UDP provides higher video quality by compressing the data more efficiently
C) UDP automatically encrypts video streams to prevent piracy
D) ISPs throttle TCP traffic more aggressively than UDP traffic

### Question 25
When designing a distributed rate limiter with tight latency budgets (e.g., <5ms), why might an engineering team choose a Redis-based approach over relying strictly on TCP congestion control?

A) Redis can intrinsically guarantee exactly-once delivery of HTTP requests, which TCP cannot
B) TCP congestion control operates purely host-to-host and cannot enforce application-level business rules (like user API quotas) across a distributed cluster
C) TCP congestion control only works over IPv6, whereas Redis supports both IPv4 and IPv6
D) Redis bypasses the OSI model entirely by using raw Ethernet frames for inter-node communication

### Question 26
In modern microservices architectures, which of the following best describes the purpose of a Service Mesh (such as Istio or Linkerd) in relation to the network layer?

A) It replaces the physical network routers and switches with software-defined equivalents for better hardware utilization.
B) It acts as a centralized load balancer that routes all external user traffic directly to the backend databases.
C) It abstracts reliable network communication, observability, and security away from the application code by injecting a sidecar proxy alongside each service instance.
D) It provides a globally distributed CDN to cache static assets and reduce origin server load.

### Question 27
When implementing real-time bidirectional communication between a web client and server, what is the primary advantage of WebSockets over HTTP Long Polling?

A) WebSockets use UDP to guarantee ordered message delivery, whereas HTTP Long Polling relies on TCP which suffers from Head-of-Line blocking.
B) WebSockets establish a single persistent TCP connection for continuous, low-overhead bidirectional data frames, whereas Long Polling incurs the overhead of establishing new HTTP requests for each server-to-client message.
C) WebSockets intrinsically provide end-to-end payload encryption at the Application layer, whereas Long Polling sends data in plaintext unless routed through a VPN.
D) WebSockets eliminate the need for DNS resolution by hardcoding the server's IP address into the browser's networking stack, significantly reducing latency.

### Question 28
In Border Gateway Protocol (BGP), what is the primary purpose of the Autonomous System (AS) Path attribute?

A) It encrypts the BGP routing table updates to prevent route hijacking
B) It is used to calculate the shortest geographical distance between two data centers
C) It prevents routing loops by recording the sequence of ASes a route has traversed, and is used for route selection
D) It automatically assigns IPv6 addresses to new Autonomous Systems joining the internet
