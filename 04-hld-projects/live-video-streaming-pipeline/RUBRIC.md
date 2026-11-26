# Live Video Streaming Pipeline - Interview Scoring Rubric

## Scoring Dimensions

| Dimension | Weight | What strong answers show |
|---|---|---|
| **Domain Knowledge (Video)** | High | Understands the difference between ingest protocols (RTMP/SRT) and delivery protocols (LL-HLS/DASH). Understands ABR, keyframes, and transcoding necessity. |
| **Scale & CDN** | High | Explicitly solves the "thundering herd" problem of manifest requests. Uses HTTP caching, CDN architectures, and Origin Shields. |
| **Latency vs Throughput** | High | Articulates the trade-off between WebRTC (low latency, hard to scale) and LL-HLS (medium latency, easy to scale). |
| **Synchronization** | Medium | Can explain how to synchronize out-of-band data (Live Chat) with the video stream using injected metadata (SEI frames / NTP timestamps). |
| **Fault Tolerance** | Medium | Addresses what happens if a transcoder node dies mid-stream, or an origin shield tier fails. |

## Performance Bands

### 1 (Weak)
- Proposes WebRTC for 10 million concurrent viewers without realizing the infrastructure cost.
- Fails to explain how ABR (Adaptive Bitrate) works.
- Suggests putting video blobs directly into a database (PostgreSQL/MongoDB).
- Misses the CDN completely or treats it as a magic black box.

### 3 (Okay)
- Correctly identifies RTMP for ingest and HLS for delivery.
- Uses a CDN.
- Understands transcoding is required for multiple resolutions.
- Struggles to explain how to get latency under 10 seconds.
- Uses arbitrary polling or timestamps for chat sync without understanding client-side buffering differences.

### 5 (Strong)
- Deep understanding of LL-HLS and CMAF partial chunking for low latency.
- Designs a hierarchical Origin Shield to protect the transcoder output from CDN cache misses.
- Understands that IDR keyframes must be strictly synchronized across all ABR transcodes.
- Accurately details injecting SEI frame metadata at the ingest layer to ensure frame-perfect chat synchronization at the client player.
- Discusses edge-caching mechanics (HTTP Chunked Transfer Encoding).

## Cross-links
* [Problem Statement](PROBLEM.md)
* [Design Document](DESIGN.md)
