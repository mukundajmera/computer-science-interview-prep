# Live Video Streaming Pipeline - Follow-Up Questions

## Follow-up questions

1. **Transcoder Node Failure:** What happens if the GPU node transcoding the 1080p rendition of a massive e-sports final dies mid-stream? How does the system recover without dropping the stream for millions of viewers?
2. **Flash Crowds:** A streamer gets raided, and viewer count jumps from 1,000 to 500,000 in 10 seconds. How does your caching layer handle this without overwhelming the origin before caches are warm?
3. **Global Ingest:** A creator in South Africa wants to stream to your platform, but your primary ingest servers are in Virginia. How do you handle ingest routing to minimize packet loss and latency before the stream even reaches your transcoder?
4. **VOD Archival:** The live stream just ended. How do you efficiently convert the live LL-HLS stream into a permanent Video-On-Demand (VOD) asset?

## Variants and extensions

- **Co-streaming (Guest Stars):** How would you modify the architecture to allow a streamer to invite 3 viewers on screen with them in real-time? (Hint: Requires WebRTC bridging into the RTMP/SRT ingest pipeline).
- **Interactive Video (Twitch Plays):** If viewers can click the video to control a game, the <3s latency of LL-HLS is too slow. How do you design for sub-second latency? (Hint: Requires transitioning to a massive WebRTC egress network, accepting the high cost).

## Interviewer probes to prepare

- "Walk me through exactly how an HTTP Chunked Transfer works when serving a CMAF partial chunk."
- "You mentioned Origin Shield. What happens if the Tier 1 Shield goes down? Where do the Edge PoPs route their traffic?"
- "Why can't we just use TCP for ingest?"

## Cross-links
* [Problem Statement](PROBLEM.md)
* [Design Document](DESIGN.md)
