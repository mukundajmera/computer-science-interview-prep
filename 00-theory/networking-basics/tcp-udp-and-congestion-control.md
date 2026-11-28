# TCP, UDP & Congestion Control

Every system design interview eventually comes down to a transport decision. TCP, UDP, and QUIC make very different promises about delivery, ordering, and latency, and congestion control is the invisible machinery that keeps shared networks from collapsing under load. This page explains how TCP actually behaves on the wire, when UDP is the right call, and why modern protocols like HTTP/3 are built on QUIC.

---

## 📦 What Each Protocol Guarantees

A transport protocol is a contract. Before picking one, be precise about what the contract promises.

| Guarantee | TCP | UDP | QUIC |
|-----------|-----|-----|------|
| Delivery | Reliable, retransmitted | Best effort, may drop | Reliable, retransmitted |
| Ordering | Single ordered byte stream | No ordering | Ordered within each stream only |
| Connection | Connection-oriented (handshake) | Connectionless | Connection-oriented (built into handshake) |
| Encryption | Optional (TLS on top) | Optional (DTLS on top) | Always (TLS 1.3 built in) |

- **TCP** gives you a reliable, ordered byte stream between two endpoints. Bytes arrive exactly once, in order, or the connection fails.
- **UDP** gives you raw datagrams: no handshake, no retransmission, no ordering, no congestion control. What you send is what the network carries.
- **QUIC** rebuilds reliable, ordered streams on top of UDP, with encryption and connection setup fused into one handshake.

---

## 🤝 The TCP Three-Way Handshake

Before any application data moves, TCP synchronizes sequence numbers with three messages:

```
Client                                        Server
   │──────────── SYN (seq = x) ───────────────▶│
   │◀────── SYN + ACK (seq = y, ack = x+1) ────│
   │──────────── ACK (ack = y+1) ──────────────▶│
   │═════════ application data ════════════════▶│
```

The handshake costs **one full round trip (1 RTT) before the first data byte can be sent**. On a transcontinental link that can be 100 ms or more of pure setup latency, which is why connection reuse and keep-alive matter so much. If TLS runs on top, the cryptographic handshake adds further round trips unless the stack supports session resumption.

---

## 🔁 Reliability: Sequence Numbers, ACKs and Retransmission

TCP reliability rests on three mechanisms:

- **Sequence numbers.** Every byte in the stream is numbered. The receiver acknowledges bytes with cumulative ACKs: "ACK 5001" means everything up to byte 5000 arrived safely.
- **Retransmission timeout (RTO).** The sender keeps a timer per unacknowledged segment. TCP estimates the round-trip time continuously and sets the RTO from that estimate; if the timer fires first, the segment is resent.
- **Fast retransmit.** Waiting for a timer is slow. If the sender sees **three duplicate ACKs** for the same sequence number, it treats the next segment as lost and resends immediately, without waiting for the RTO.

A checksum on every segment catches corrupted data, and out-of-order segments are buffered until the gap is filled.

---

## 🎛️ Flow Control vs Congestion Control

These two mechanisms are constantly confused in interviews, but they solve **different problems**:

- **Flow control protects the receiver.** A slow consumer must not be buried under data it cannot buffer. The receiver advertises a **receive window (rwnd)** in every ACK, and the sender may have at most that many unacknowledged bytes in flight.
- **Congestion control protects the network.** Links and routers between the endpoints have finite capacity, and no one announces it. TCP probes for available bandwidth using a **congestion window (cwnd)**:
  - **Slow start:** cwnd starts small and roughly doubles every RTT, so throughput ramps up exponentially.
  - **Congestion avoidance:** once cwnd passes a threshold (ssthresh), growth becomes additive, about one segment per RTT, to probe gently.
  - **Loss reaction:** packet loss is treated as a congestion signal. Classic TCP cuts cwnd multiplicatively (Tahoe/Reno style), while a full timeout collapses back to slow start. Modern variants such as CUBIC shape this curve differently, but the principle stands.

The sender's actual in-flight limit is `min(rwnd, cwnd)`: the tighter of the two constraints always wins.

---

## 🚧 Head-of-Line Blocking and Why QUIC Moved to UDP

TCP's ordered byte stream has a structural flaw: **one lost segment stalls everything behind it**. If bytes 1–1000 are lost but 1001–5000 arrived, the receiver cannot deliver any of it to the application until the gap is retransmitted. HTTP/2 multiplexed many logical streams over one TCP connection, which made this worse: a single lost packet froze every stream on that connection.

QUIC moves reliability into userspace on top of UDP:

- **Independent streams.** Loss on one stream blocks only that stream; the others keep flowing.
- **Faster setup.** Transport and TLS 1.3 handshakes are combined, cutting connection establishment versus TCP + TLS.
- **Connection migration.** Connections are identified by connection IDs, not IP/port tuples, so a phone switching from Wi-Fi to cellular keeps its connection alive.

UDP is the vehicle because middleboxes ossify new TCP options, and a userspace protocol over UDP can evolve without kernel or router changes.

---

## 🧭 Choosing Between TCP, UDP and QUIC

| Product scenario | Transport choice | Why |
|------------------|------------------|-----|
| Banking API serving account balances | TCP (HTTPS) | Correctness is non-negotiable; a lost response must be retransmitted |
| Multiplayer game state sync | UDP | A retransmitted position update is stale; fresh state at 60 Hz beats guaranteed delivery of old state |
| Voice and video calls | UDP (WebRTC) | Late audio is worthless; minor loss sounds better than a pause |
| Mobile app browsing on flaky networks | QUIC (HTTP/3) | Faster setup and no cross-stream head-of-line blocking on lossy links |
| DNS name resolution | UDP (TCP fallback) | One small request and response; handshake overhead would dominate |

The pattern: pick UDP when timeliness beats completeness and you can rebuild what you need on top; pick TCP when the stream must be exactly right; pick QUIC when you want TCP-grade reliability without its head-of-line and setup costs.

---

## 🎤 Interview Questions

**1. Why does TCP need three handshake messages instead of two?**
Both sides must prove they can send and receive. The SYN and SYN-ACK establish the client's sequence number, but only the third message (the ACK) confirms to the client that the server received its acknowledgment, synchronizing the server's sequence number both ways. Two messages would leave one direction unconfirmed and also allow stale, delayed SYNs to open phantom connections.

**2. What is the difference between flow control and congestion control?**
Flow control protects the receiver using the advertised receive window; congestion control protects the network using the sender-side congestion window built from loss and RTT signals. The sender respects both at once by capping in-flight bytes at the smaller of the two windows.

**3. Walk through what happens when a TCP segment is lost.**
The receiver keeps ACKing the last in-order byte, producing duplicate ACKs. After three duplicates the sender fast-retransmits the missing segment and typically halves its congestion window; if the retransmission timer fires first, the segment is resent and TCP drops back toward slow start. Data behind the gap is buffered until the hole is filled.

**4. Why did QUIC choose UDP instead of extending TCP?**
TCP is implemented in operating-system kernels and its options are mangled by middleboxes, so deploying a new TCP variant at internet scale is practically impossible. Building on UDP lets QUIC iterate in userspace while adding independent streams, integrated TLS 1.3, and connection migration.

---

## ⚠️ Common Pitfalls

- **Confusing flow control with congestion control.** One is about the receiver's buffers, the other about the network's capacity; saying "the window" without naming which one is a red flag in interviews.
- **Assuming UDP is automatically faster.** UDP moves the reliability problem to your application. If you end up rebuilding ACKs and retransmission badly, you get TCP's cost with worse machinery.
- **Ignoring handshake round trips in latency budgets.** TCP setup costs 1 RTT before data, and TLS adds more; on high-RTT paths this dwarfs transfer time for small responses.
- **Believing HTTP/2 fixed head-of-line blocking.** HTTP/2 removed application-level HOL blocking, but the single underlying TCP connection still stalls all streams on packet loss. Only QUIC's independent streams address that layer.

---

## 📚 Related Topics

- [Networking Essentials](./networking-essentials.md) — latency budgets, protocol selection, failure handling
- [HTTP & HTTPS Protocols](./http-https.md) — the application layer that runs over these transports
- [WebSockets](./websockets.md) — persistent full-duplex channels over TCP
- [Load Balancing](../../03-hld-concepts/load-balancing/) — distributing connections across servers
- [DNS](../../03-hld-concepts/dns/) — name resolution that precedes every connection
