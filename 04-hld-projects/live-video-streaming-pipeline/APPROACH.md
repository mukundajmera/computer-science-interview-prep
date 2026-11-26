# Live Video Streaming Pipeline - Approach & Alternatives

This document outlines the strategic choices made when designing the Live Video Streaming pipeline, contrasting the selected path against viable alternatives.

## 1. Ingestion Protocols

### RTMP (Real-Time Messaging Protocol)
- **Status:** Selected (Legacy Support).
- **Pros:** Universal support across all broadcasting software (OBS, XSplit) and hardware encoders.
- **Cons:** Built on TCP, making it highly susceptible to Head-of-Line blocking on lossy mobile networks. Deprecated by Adobe.

### SRT (Secure Reliable Transport)
- **Status:** Selected (Modern Standard).
- **Pros:** Built on UDP with selective retransmission. Performs exceptionally well over poor networks (like 4G/5G mobile connections) by avoiding TCP's backoff mechanisms.
- **Cons:** Requires modern broadcasting software support.

### WebRTC (WHIP)
- **Status:** Selected (Future/Ultra-low latency).
- **Pros:** Sub-second latency. Ideal for co-streaming or browser-based broadcasting without dedicated software.
- **Cons:** UDP-based, requires specific NAT traversal (STUN/TURN) handling at the ingest edge.

## 2. Delivery & Playback Protocols

The core architectural decision is how to distribute the video to 10 million concurrent viewers.

### Alternative A: WebRTC for Egress (The Zoom/Discord model)
- **How it works:** The server maintains a dedicated, stateful UDP connection with every single viewer.
- **Pros:** Ultra-low latency (< 500ms). Perfect for video conferencing.
- **Cons:** **Does not scale to 10M viewers economically.** It bypasses the entire global HTTP CDN caching infrastructure. Running 10M stateful WebRTC sessions requires massive, expensive, specialized server farms.

### Alternative B: Standard HLS / DASH
- **How it works:** Video is chopped into 6-10 second segments. Clients download segments over standard HTTP.
- **Pros:** Scales infinitely using standard, cheap HTTP CDNs.
- **Cons:** High latency. A player typically buffers 3 segments before playback starts. 3 * 6s = 18 seconds of glass-to-glass latency. Unacceptable for interactive live streams.

### Selected Approach: Low-Latency HLS (LL-HLS) with CMAF
- **How it works:** Uses standard HTTP CDNs, but the 6-second segments are internally broken down into 200ms "partial chunks" (CMAF). As soon as a 200ms chunk is encoded, it is announced in the manifest and pushed over HTTP chunked transfer encoding.
- **Why it wins:** Combines the infinite, cheap scalability of HTTP CDNs (solving the 10M viewer problem) with latency profiles close to interactive protocols (2-3 seconds).

## 3. Dealing with Manifest Thundering Herds

With LL-HLS, clients request manifest updates every time a new partial chunk is available (e.g., every 500ms). 10 Million clients polling = 20 Million requests/sec.

### Alternative A: Polling
- **How it works:** Clients just HTTP GET the manifest blindly.
- **Cons:** Cache misses hit the origin. The origin cannot handle 20M RPS.

### Selected Approach: Origin Shield + Blocking Requests (LL-HLS Delta Updates)
- **How it works:** 
  1. Clients request the manifest and say "Hold this request open until partial chunk `N+1` is ready."
  2. The CDN Edge holds millions of open HTTP connections.
  3. When `N+1` is generated, the Origin pushes *one* copy to the CDN Edge.
  4. The CDN Edge immediately streams that response out to the millions of waiting connections.
- **Why it wins:** Turns a polling DDoS attack into an efficient pub/sub mechanism utilizing the CDN Edge's massive connection-handling capacity.

## 4. Cross-links
* [Design Document](DESIGN.md)
* [Comparison: Live vs VOD](COMPARISON.md)
