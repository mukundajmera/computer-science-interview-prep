# Live Video Streaming Pipeline - Comparison

## Live Streaming vs Video On Demand (VOD)

While both systems deliver video to users, the architectural constraints and priorities are fundamentally different. VOD (like Netflix) optimizes for quality and storage efficiency. Live Streaming (like Twitch) optimizes for latency and real-time processing.

| Concern | Live Streaming | VOD (Video on Demand) |
|---|---|---|
| **Latency Tolerance** | Low (< 3 seconds). Critical for interactivity. | High. User doesn't care if the movie takes 2 seconds to buffer initially. |
| **Transcoding** | Real-time, 1-pass encoding. Highly CPU/GPU bound. Trade-offs made for speed over perfect compression. | Offline, multi-pass encoding. Can take hours to compress perfectly to save CDN bandwidth. |
| **Storage** | Ephemeral. Video chunks are held in RAM/NVMe at the edge for a sliding window of a few minutes. | Permanent. Stored in Blob Storage (S3) and replicated globally. |
| **Manifests** | Dynamic. The `m3u8` playlist is updated every second. Massive request volume just for manifests. | Static. The `m3u8` playlist is generated once and cached indefinitely at the edge. |
| **Caching Profile** | Simultaneous flash crowd. 10M people watch the *exact same chunk* at the *exact same time*. High risk of thundering herds. | Long tail. Users watch different parts of different movies at different times. |
| **Ingest** | Single continuous stream over RTMP/SRT. Vulnerable to broadcaster's network drops. | File upload (mp4/mkv) over HTTPS. Can be paused and resumed. |

## Delivery Protocols: LL-HLS vs WebRTC

For delivering live video to the end user, these are the two dominant paradigms.

| Feature | LL-HLS (Low-Latency HLS) | WebRTC |
|---|---|---|
| **Underlying Protocol** | HTTP / TCP (Standard Web) | UDP |
| **Glass-to-glass Latency** | 2 - 5 seconds | < 0.5 seconds |
| **Scalability** | Practically infinite (via standard CDNs) | Hard and expensive (requires dedicated UDP media servers) |
| **Caching** | Native CDN edge caching | No native caching, relies on pub/sub server cascading |
| **Best Use Case** | Massive broadcasts (Esports, Concerts) | Interactive conferencing (Zoom), Co-streaming, Cloud Gaming |

## Cross-links
* [Design Document](DESIGN.md)
* [Approach & Alternatives](APPROACH.md)
