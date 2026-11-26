# Live Video Streaming Pipeline - Problem Statement

## 1. Description
Design a live video streaming pipeline capable of ingesting video from thousands of live creators and distributing it to millions of concurrent viewers globally with low glass-to-glass latency. The system should support platforms similar to Twitch or YouTube Live.

## 2. Core User Value
- **Creators:** Reliable, high-quality ingest of their live streams from broadcasting software (OBS) or mobile apps.
- **Viewers:** Buffer-free, high-quality, and low-latency playback across various devices and network conditions.
- **Community:** Synchronized viewing experience enabling realtime chat and interactivity.

## 3. Scope & Requirements

### 3.1 Functional Requirements
- Support live video ingestion via standard protocols (RTMP, SRT, WHIP).
- Real-time transcoding to multi-bitrate ABR (Adaptive Bitrate) ladders (1080p, 720p, 480p, 360p).
- Synchronized IDR (Instantaneous Decoding Refresh) keyframes across all renditions.
- Package and deliver video chunks via low-latency HTTP streaming protocols (LL-HLS / CMAF).
- Inject timed metadata (SEI frames) embedding NTP timestamps to synchronize the video stream with realtime features like live chat.

### 3.2 Non-Functional Requirements
- **Low Latency:** Glass-to-glass latency (from creator camera to viewer screen) of < 3 seconds.
- **High Availability:** The streaming pipeline must withstand regional failures and infrastructure degradation.
- **Scalability:** Able to handle massive flash crowds and highly skewed traffic patterns (e.g., esports finals).
- **Efficiency:** Optimize egress and origin load through aggressive multi-tier caching.

### 3.3 Out of Scope
- VOD (Video on Demand) processing and storage.
- The implementation of the Live Chat service itself (though synchronization with it is in scope).
- Creator monetization and viewer subscription management.
- Recommendation engines and home page ranking.

## 4. Scale & Constraints

### 4.1 Load Estimates
- **Concurrent Streamers:** 50,000 active live streams.
- **Ingest Traffic:** ~6 Mbps per stream * 50,000 = **300 Gbps total ingest**.
- **Concurrent Viewers:** 10 Million viewers.
- **Egress Traffic:** Assuming an average bitrate of 3 Mbps per viewer = **30 Tbps total egress**.
- **Manifest Requests:** Viewers request manifests/playlists every second (LL-HLS partial chunking). ~10M requests/sec for manifests if un-cached.

### 4.2 System Constraints
- **Origin Overload:** The origin servers must be shielded from the 10M manifests/sec request rate via a Hierarchical 2-tier Origin Shield.
- **Transcoding Compute:** Real-time transcoding is highly CPU/GPU intensive and requires dedicated, horizontally scalable pools.
- **Synchronicity:** Transcoding different resolutions must produce segments with identical temporal boundaries for smooth ABR switching by the client player.
