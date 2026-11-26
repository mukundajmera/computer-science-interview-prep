# Network Protocol Evolution - Comparison

## Modern Protocol Comparison Matrix

| Protocol | Transport | Communication Model | Key Strength | Primary Weakness | Ideal Use Case |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **HTTP/1.1** | TCP | Request-Response | Ubiquitous support, simple text-based format | High overhead, HTTP-layer HoL blocking | Legacy APIs, simple static websites |
| **HTTP/2** | TCP | Multiplexed | Header compression (HPACK), binary framing | TCP-layer HoL blocking on poor networks | Standard web applications, modern APIs |
| **HTTP/3 (QUIC)** | UDP | Multiplexed | 0-RTT, Connection Migration, Zero HoL blocking | Blocked by some corporate firewalls | Mobile apps, video streaming, flaky networks |
| **gRPC** | TCP (HTTP/2) | RPC (Unary & Streaming) | High performance, strongly-typed (Protobuf), bi-directional | Harder to debug (binary), requires client library | Internal microservices, polyglot environments |
| **WebSockets** | TCP | Full-Duplex | Persistent connection, very low overhead after handshake | Stateful, requires specialized load balancing | Real-time chat, multiplayer gaming, live trading |
| **SSE** | TCP (HTTP) | Unidirectional Push | Simple standard HTTP, automatic reconnections | Server-to-client only, browser connection limits | Live score updates, notification feeds, LLM token streaming |

## HTTP Version Differences: Head-of-Line Blocking

| Characteristic | HTTP/1.1 | HTTP/2 | HTTP/3 (QUIC) |
| :--- | :--- | :--- | :--- |
| **Underlying Transport** | TCP | TCP | UDP |
| **Multiplexing** | No (Pipelining failed) | Yes (Binary Framing) | Yes (Native to QUIC) |
| **HoL Blocking Type** | HTTP-layer | TCP-layer | None |
| **Impact of 1 Lost Packet** | Halts current & all subsequent requests | Halts all multiplexed streams | Halts only the specific affected stream |

## Cross-links
* [Theory](THEORY.md)
* [Interview Q&A](INTERVIEW-QA.md)
