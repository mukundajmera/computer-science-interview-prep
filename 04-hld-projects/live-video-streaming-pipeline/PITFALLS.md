# Live Video Streaming Pipeline - Common Pitfalls

## 1. WebRTC for Mass Broadcast
- **Failure Signal:** Designing the egress system using WebRTC (or raw WebSockets) for 10 million concurrent viewers to achieve "zero latency".
- **Root Cause:** Treating a 1-to-many broadcast problem like an N-to-N conferencing problem. WebRTC is stateful and UDP-based; it cannot be trivially cached by standard HTTP CDNs.
- **Mitigation:** Recognize that while WebRTC is great for the *ingest* of a single streamer (WHIP), delivery to 10M people requires HTTP-based protocols (LL-HLS/DASH) to leverage the global caching hierarchy of CDNs.

## 2. Ignoring Manifest Request Volume
- **Failure Signal:** Drawing an architecture where 10M mobile apps directly hit an S3 bucket or a basic cluster of Nginx servers to read the `m3u8` manifest every second.
- **Root Cause:** Failing to calculate the request rate of live HLS. 10M viewers pulling a manifest every 1 second = 10,000,000 RPS. This will melt any basic origin.
- **Mitigation:** Design a multi-tier Origin Shield architecture. Explain how Edge CDNs collapse requests, and Regional Shields collapse edge requests, ensuring the origin only sees a handful of requests per second.

## 3. Naive Chat Synchronization
- **Failure Signal:** Synchronizing live chat by just sending the server's current clock time to the client via WebSocket and rendering it immediately.
- **Root Cause:** Ignoring network buffering. Viewer A might have a 2-second buffer, Viewer B a 5-second buffer. Real-time chat messages will appear "in the future" relative to Viewer B's video stream, spoiling the content.
- **Mitigation:** Inject absolute NTP timestamps into the video stream itself (via SEI NAL units) at the ingest stage. The client player extracts this time, and the chat UI uses it to delay message rendering until the video catches up.

## 4. Unsynchronized ABR Ladders
- **Failure Signal:** Describing the transcoding tier as simply "compressing the video into 4 sizes" without mentioning keyframes.
- **Root Cause:** Lack of domain knowledge regarding how video players switch resolutions mid-stream.
- **Mitigation:** Explicitly state that the transcoders must be configured to output time-aligned IDR (Instantaneous Decoding Refresh) keyframes. If the 1080p and 720p streams have keyframes at different timestamps, the player will stutter or crash when switching between them.

## Cross-links
* [Design Document](DESIGN.md)
* [Scoring Rubric](RUBRIC.md)
