# Live Video Streaming Pipeline - Strong Interview Answer

## 1. Requirements & Core Insight

**Say:** "To design a live streaming pipeline for 50,000 creators and 10 million concurrent viewers, our primary enemy is latency and the 'thundering herd' problem. VOD is a storage problem; Live is a real-time routing and synchronization problem.

To achieve our goal of sub-3-second glass-to-glass latency while remaining economically viable, we cannot use WebRTC for the egress to 10 million viewers. We must leverage existing HTTP CDN infrastructure using Low-Latency HLS (LL-HLS) with CMAF partial chunking. Furthermore, to support real-time chat, we must inject absolute timestamps into the video stream itself."

## 2. Ingestion & Transcoding

**Say:** "The streamer connects to our closest Ingest Gateway using SRT or RTMP. 

At this gateway, we do something critical: we inject the current NTP server time as an SEI (Supplemental Enhancement Information) metadata frame directly into the H.264 bitstream. This timestamp will travel intact all the way to the viewer's player, allowing the client device to perfectly synchronize the rendering of WebSocket chat messages with the video frame currently on screen.

The gateway forwards the stream to our Transcoding Cluster. Because we need Adaptive Bitrate (ABR), we decode the stream and encode it into multiple renditions (1080p, 720p, etc.). I will enforce strict, time-aligned IDR keyframes across all transcoders. If keyframes aren't synchronized, the client player will stall when trying to switch from 720p to 1080p mid-stream."

## 3. Packaging & Delivery (The Core Engine)

**Say:** "To achieve low latency without bypassing CDNs, we use the LL-HLS protocol. 

Instead of waiting for a 6-second segment to finish encoding, the Packager writes out 200-millisecond 'partial chunks'. As soon as a chunk begins encoding, the Packager announces it in the manifest. 

When a viewer requests that partial chunk, the Packager streams the bytes out using HTTP Chunked Transfer Encoding. The bytes flow through the Origin, through the CDN, and into the viewer's player while the chunk is still actively being encoded."

## 4. Origin Shield & Thundering Herd Mitigation

**Say:** "With LL-HLS, 10 million clients will request a manifest update every 200ms to 500ms. If we rely on standard polling, our origin will be crushed by 20 to 50 million Requests Per Second.

I will implement a Hierarchical Origin Shield utilizing LL-HLS Blocking Reloads. 

When clients ask for the next manifest, the Edge CDN holds the HTTP connections open. When the origin publishes the updated manifest, it pushes a single copy to the Regional Shield, which pushes to the Edge PoPs. The Edge PoP then takes that single response and multiplexes it to all 100,000 waiting connections simultaneously. This turns a DDoS attack of polling into an efficient, stateful pub/sub distribution tree."

## 5. Summary

**Say:** "In summary, we ingest via SRT, inject SEI timestamps for chat sync, transcode to a keyframe-aligned ABR ladder, package into 200ms CMAF chunks, and distribute via LL-HLS over a 2-tier Origin Shielded CDN. This provides the massive scale of HTTP caching with latency approaching interactive protocols."

## Cross-links
* [Design Document](DESIGN.md)
* [Scoring Rubric](RUBRIC.md)
