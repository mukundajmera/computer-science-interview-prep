# Live Video Streaming Pipeline - Design

## 1. Requirements & Constraints Recap
- **Scale:** 50,000 live streamers (300 Gbps ingest); 10M concurrent live viewers (30 Tbps egress).
- **Latency:** < 3s glass-to-glass latency via LL-HLS / CMAF partial chunk streaming.
- **Transcoding:** Real-time multi-bitrate ABR ladder (1080p, 720p, 480p, 360p) with synchronized IDR keyframes.
- **Delivery:** Hierarchical 2-tier Origin Shield tree absorbing 10M manifest queries/sec.
- **Interactivity:** Timed metadata injection (SEI frames) embedding NTP timestamps for live chat sync.

## 2. System Architecture

The live streaming pipeline is composed of distinct physical stages designed to take a high-quality single-feed ingest, transcode it, package it, and distribute it out to massive edge networks.

### 2.1 Ingest Gateways
- **Role:** Terminate the broadcaster's connection (e.g., from OBS).
- **Protocols Supported:** RTMP (legacy standard), SRT (Secure Reliable Transport for lossy networks), and WHIP (WebRTC HTTP Ingestion Protocol for sub-second latency).
- **Functionality:** 
  - Connection termination and stream authentication.
  - Demuxing incoming feeds.
  - Injects NTP timestamps into H.264/H.265 SEI (Supplemental Enhancement Information) frames. This is crucial: by stamping absolute time in the video frames themselves, client players can synchronize playback state exactly with external websocket events (like Live Chat).

### 2.2 Transcoding Cluster
- **Role:** Convert the high-bitrate source stream into an Adaptive Bitrate (ABR) ladder to serve different client network conditions.
- **Workflow:**
  - A stream router consistently hashes the stream ID to a specific transcode node (or node pair for redundancy).
  - The transcoder decodes the source stream and scales it to multiple resolutions (e.g., 1080p, 720p, 480p, 360p).
  - **Synchronized IDR Keyframes:** The encoder is forced to emit an IDR (Instantaneous Decoding Refresh) frame at exact, synchronized intervals (e.g., every 1 second) across *all* renditions. Without this, players cannot seamlessly switch bitrates mid-stream.
- **Hardware:** Often utilizes GPU instances (Nvidia NVENC) or specialized ASIC encoders for high-density real-time processing.

### 2.3 Packaging (LL-HLS / CMAF)
- **Role:** Take the raw transcoded output and wrap it in HTTP-deliverable containers.
- **CMAF Partial Chunking:** Instead of waiting for a full 2-second or 6-second segment to finish encoding before publishing, the packager writes *partial chunks* (e.g., 200ms duration) using CMAF (Common Media Application Format).
- **LL-HLS:** Generates Low-Latency HLS manifests. The manifest is updated with references to partial chunks as they become available.
- **HTTP Chunked Transfer:** Partial chunks are pushed to the origin/CDN using HTTP chunked transfer encoding, allowing bytes to flow to the CDN edge before the chunk is even fully encoded.

### 2.4 Origin & Origin Shield (Hierarchical 2-Tier)
- **Role:** Serve manifests and media chunks to the global CDN edge networks without collapsing under thundering herds.
- **The Problem:** 10M viewers refreshing an LL-HLS manifest every second generates 10M requests/sec. If edges miss, the origin collapses.
- **The Solution:** A 2-Tier Origin Shield.
  - **Tier 1 (Edge Shield/Regional Origin):** Positioned close to the CDN Edges. Collapses requests from many edge PoPs into a single request.
  - **Tier 2 (Core Origin):** Sits directly in front of the Packager. Collapses requests from Regional Origins.
- **Request Collapsing / Promise Mechanism:** If 10,000 edges request chunk `100.m4s` simultaneously, the shield holds 9,999 of them, sends 1 request to the packager, and multiplexes the response out to all 10,000 connections simultaneously.

### 2.5 CDN Edge Network
- **Role:** Terminate viewer TLS connections and serve media bytes from memory/SSD caches close to the user.
- **Push vs Pull:** Modern LL-HLS uses HTTP/2 Server Push or standard HTTP GETs with chunked transfer. The edge caches the partial chunks as they arrive and streams them to the client player.

## 3. Data Model

Live video doesn't rely on traditional databases for the streaming path. The data model is represented by the Manifests.

### LL-HLS Multivariant Playlist (Master Manifest)
Points to the different available renditions.
```text
#EXTM3U
#EXT-X-STREAM-INF:BANDWIDTH=6000000,RESOLUTION=1920x1080
1080p.m3u8
#EXT-X-STREAM-INF:BANDWIDTH=3000000,RESOLUTION=1280x720
720p.m3u8
```

### LL-HLS Media Playlist (Level Manifest)
Contains the sliding window of available chunks and partial chunks.
```text
#EXTM3U
#EXT-X-TARGETDURATION:2
#EXT-X-SERVER-CONTROL:CAN-BLOCK-RELOAD=YES,PART-HOLD-BACK=0.6
...
#EXT-X-PROGRAM-DATE-TIME:2023-10-27T12:00:00.000Z
#EXT-X-PART:DURATION=0.200,URI="chunk_100_part1.m4s"
#EXT-X-PART:DURATION=0.200,URI="chunk_100_part2.m4s"
#EXT-X-PART:DURATION=0.200,URI="chunk_100_part3.m4s"
#EXTINF:2.0,
chunk_100.m4s
```

## 4. Deep Dives

### 4.1 Achieving < 3s Latency (LL-HLS vs Standard HLS)
Standard HLS requires the encoder to finish a full segment (e.g., 6 seconds) before publishing. The player needs 3 segments buffered to start playing smoothly, resulting in 18+ seconds of latency.

LL-HLS splits segments into partial chunks (e.g., 200ms). The packager announces partial chunks in the manifest before the full segment is finished. The CDN uses chunked transfer encoding to stream these bytes to the player immediately. The player buffers only a few partial chunks, dropping latency to ~2-3 seconds.

### 4.2 Timed Metadata for Live Chat Sync
Live streams and live chats are delivered over entirely different protocols (Video via HTTP/CDN, Chat via WebSockets/PubSub).
Because network buffering varies per user, User A might be 2.5s behind real-time, while User B is 4.0s behind. If the chat system simply displays messages as they arrive, the chat will spoil stream events (e.g., a goal in soccer) for User B.

**Solution:**
1. The Ingest server injects the current NTP time as an SEI (Supplemental Enhancement Information) NAL unit directly into the H.264/H.265 video bitstream.
2. The client player extracts this timestamp during decode.
3. The Chat websocket client holds incoming messages in a buffer.
4. The Chat client queries the video player: "What is the absolute timestamp of the frame currently on screen?"
5. The Chat client renders messages only when the video player's on-screen timestamp catches up to the message's timestamp.

### 4.3 Thundering Herd & Manifest Caching
Every time a partial chunk is created (e.g., every 200ms), the manifest updates. 10 million viewers are constantly polling this manifest.
- **Blocking Reload (`CAN-BLOCK-RELOAD`):** LL-HLS allows the client to ask for the manifest "only when part N is ready". The CDN edge holds the HTTP request open.
- **Request Collapsing:** When part N is published, the Origin pushes the new manifest to the CDN Edge. The Edge immediately replies to all 10M blocked, waiting requests simultaneously, utilizing its cache. This prevents the origin from being hit 10 million times.

## 5. Trade-offs

| Decision | Option Chosen | Alternative | Rationale |
|---|---|---|---|
| **Delivery Protocol** | LL-HLS / CMAF | WebRTC | WebRTC provides <0.5s latency but scales poorly to 10M viewers (requires active UDP connections, bypassing standard HTTP CDNs). LL-HLS leverages cheap, ubiquitous HTTP CDN caching. |
| **Ingest Protocol** | RTMP / SRT / WHIP | RTMP only | RTMP is standard but suffers on lossy connections. SRT handles packet loss better for remote mobile broadcasters. WHIP is the future for ultra-low latency ingest. |
| **Transcoding** | On-the-fly Server | Client-side ABR | Client cannot reliably generate ABR ladders due to CPU constraints and limited upload bandwidth. Must be done centrally. |

## 6. Cross-links
* [Problem Statement](PROBLEM.md)
* [Approach & Alternatives](APPROACH.md)
* [Comparison: Live vs VOD](COMPARISON.md)

---
**Real-world reference**: See how YouTube solved this in the [YouTube case study](../../case-studies/youtube-video/)
