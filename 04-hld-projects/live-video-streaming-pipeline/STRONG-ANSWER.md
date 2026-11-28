# Live Video Streaming Pipeline — Strong Answer (Time-Boxed)

**Say:** "Live video at 50,000 broadcasters and 10 million concurrent viewers is a real-time routing, synchronization, and fan-out caching problem. To hit sub-3-second latency without abandoning HTTP CDN economics, I will use SRT/RTMP/WHIP for ingest, keyframe-aligned GPU transcoding into 200ms CMAF partial chunks, LL-HLS with blocking reloads over a 2-tier Origin Shield, and SEI NTP timestamps for frame-accurate chat sync."

A time-boxed 45-minute strong answer outline for a Live Video Streaming Pipeline system design interview. Each phase includes target timing, concrete numbers, and the key points an interviewer expects to hear.

> **Related docs:** [PROBLEM](./PROBLEM.md) · [DESIGN](./DESIGN.md) · [APPROACH](./APPROACH.md) · [RUBRIC](./RUBRIC.md) · [PITFALLS](./PITFALLS.md) · [FOLLOW-UPS](./FOLLOW-UPS.md) · [COMPARISON](./COMPARISON.md)

---

## ⏱️ Time Allocation (45 Minutes)

| Phase | Duration | Focus |
|---|---|---|
| 1. Requirements & Clarification | 5 min | Scope latency, protocols, and non-goals |
| 2. Back-of-Envelope Estimation | 5 min | Quantify ingest, egress, and manifest RPS |
| 3. APIs, Data Model & High-Level Design | 12 min | Control vs. media planes and end-to-end pipeline |
| 4. Deep Dives & Failure Handling | 18 min | LL-HLS latency, Origin Shield, chat sync, and 5 failure paths |
| 5. Trade-offs & 60–90 Second Wrap-up | 5 min | Justify choices and deliver closing summary |

---

## Phase 1 — Requirements & Clarification (5 min)

### Clarifying Questions to Ask
1. "What glass-to-glass latency target are we optimizing for — sub-second interactive (WebRTC) or 2–3 seconds broadcast scale (LL-HLS)?"
2. "How many concurrent broadcasters and concurrent viewers should we design for, and how skewed are flash-crowd events?"
3. "Do we need real-time chat synchronization with the video frame, or is best-effort chat acceptable?"
4. "Is VOD recording/DVR replay in scope, or strictly live playback?"
5. "Which ingest clients must we support — desktop encoders like OBS (RTMP/SRT) and browser/mobile WebRTC (WHIP)?"

### Functional Requirements (confirm aloud)
- **Ingest:** Authenticate broadcasters and accept RTMP, SRT, and WHIP streams.
- **Transcoding:** Produce a multi-bitrate ABR ladder (1080p, 720p, 480p, 360p) with synchronized IDR keyframes.
- **Packaging & Delivery:** Package 200ms CMAF partial chunks and serve LL-HLS playlists globally.
- **Synchronization:** Embed NTP timestamps in SEI frames so client chat aligns with the rendered video frame.

### Non-Functional Requirements & Scope
- **Latency:** < 3 seconds glass-to-glass.
- **Scale & Availability:** 50,000 concurrent streams, 10M concurrent viewers, resilient to encoder drops, transcoder crashes, and origin/shield faults.
- **Out of scope:** VOD archival pipeline, chat backend implementation, monetization, and home-feed ranking.

---

## Phase 2 — Back-of-Envelope Estimation (5 min)

**Say:** "Let's size only the numbers that change our architecture: ingest bandwidth, viewer egress bandwidth, and manifest request rate."

```text
Ingest bandwidth:   50,000 streams × 6 Mbps  = 300 Gbps total ingest
Viewer egress:      10M viewers × 3 Mbps avg = 30 Tbps total egress
Manifest RPS:       10M viewers × 1–5 req/s  = 10M–50M manifest RPS if uncollapsed
Transcode compute:  50,000 streams × 4 rungs = 200,000 real-time encode outputs (GPU/ASIC pool)
```

### Design Implications
- **30 Tbps egress** rules out stateful WebRTC fan-out to 10M viewers; HTTP CDN edge caching is mandatory.
- **10M+ manifest RPS** rules out direct-to-origin polling; we need blocking reloads plus a 2-tier Origin Shield with request collapsing.
- **300 Gbps ingest + 200K encode rungs** requires regionally distributed ingest gateways and horizontally scaled GPU/ASIC transcoding pools.

---

## Phase 3 — APIs, Data Model & High-Level Design (12 min)

### Core API Contracts
| Layer | Method & Endpoint | Purpose |
|---|---|---|
| Control Plane | `POST /api/v1/streams/sessions` | Allocate regional ingest URLs (`srt://`, `rtmps://`, `whip`), `session_id`, and bitrate limits |
| Ingest Auth | `POST /api/v1/ingest/authenticate` | Validate stream key hash, enforce single-publisher `ingest_epoch` fencing, return transcoder pool |
| Viewer Join | `POST /api/v1/streams/{stream_id}/join` | Return signed primary + fallback CDN `master.m3u8` URLs and chat WebSocket endpoint |
| CDN Delivery | `GET /live/v1/{stream_id}/{rendition}/index.m3u8?_HLS_msn=N&_HLS_part=P&_HLS_skip=YES` | LL-HLS blocking-reload playlist fetch (plus immutable `.m4s` partial chunks) |

### Data Model
- **Control Plane Store:** Partitioned by `stream_id` (channel config, active `session_id`, `ingest_epoch`, transcoder assignment, heartbeat TTL).
- **Media Plane:** No relational DB on the hot path — state is the LL-HLS Multivariant Playlist (`master.m3u8`), sliding-window Media Playlist (`index.m3u8` with `#EXT-X-PART` and `#EXT-X-SERVER-CONTROL:CAN-BLOCK-RELOAD=YES,PART-HOLD-BACK=0.6`), and immutable CMAF `.m4s` chunks.

### End-to-End Architecture
```text
Broadcaster (OBS/Mobile)
  → Ingest Gateway (RTMP/SRT/WHIP + Auth + SEI NTP Injection)
  → Consistent-Hash Router → GPU Transcoding Cluster (1080p/720p/480p/360p, Aligned IDR)
  → LL-HLS / CMAF Packager (200ms partial chunks, HTTP chunked transfer)
  → Tier 2 Core Origin (Multi-AZ)
  → Tier 1 Regional Origin Shield (Request Collapsing)
  → CDN Edge PoPs (Blocking Reload Multiplexing + RAM Cache)
  → 10M Viewers (ABR Player + SEI-Synced Live Chat)
```

---

## Phase 4 — Deep Dives & Failure Handling (18 min)

### 4a. Achieving < 3s Latency with LL-HLS & CMAF (~4 min)
**Say:** "Standard HLS waits for a full 6-second segment and buffers 3 segments, putting us at 18+ seconds. Instead, our packager emits 200ms CMAF partial chunks and announces them in the manifest immediately. Using HTTP chunked transfer encoding, bytes stream through the Origin Shield and CDN edge while the full 2-second segment is still being encoded, so the player only buffers ~0.6s–1.0s of partial chunks."

### 4b. Defeating the 10M RPS Manifest Thundering Herd (~4 min)
**Say:** "With LL-HLS, 10 million viewers ask for the next partial chunk every few hundred milliseconds. We combine **Blocking Reloads** (`_HLS_msn`, `_HLS_part`) with a **2-Tier Origin Shield**. Edge PoPs hold viewer HTTP/2 or HTTP/3 requests open; when the packager publishes part `P`, one copy flows Core Origin → Regional Shield → Edge PoP, and each edge multiplexes that single cached response to hundreds of thousands of waiting connections."

### 4c. Synchronized ABR & Frame-Accurate Chat Sync (~4 min)
- **Aligned IDR Keyframes:** Force identical IDR cadence (e.g., every 1–2s) across all transcode renditions so ABR switches never stall the decoder.
- **SEI NTP Timestamps:** Inject absolute NTP time into H.264/H.265 SEI NAL units at the Ingest Gateway. The viewer's chat client buffers incoming WebSocket messages and releases them only when the video player's decoded on-screen SEI timestamp catches up, preventing chat spoilers across different viewer buffer depths.

### 4d. Failure Modes & Recovery Paths (~6 min)
Walk through the five production failure paths proactively:
1. **Encoder drop & reconnect:** Hold a 15–30s grace window (optional slate) rather than terminating the stream; on reconnect, increment `ingest_epoch` to fence stale sockets and insert `#EXT-X-DISCONTINUITY` so players reset cleanly.
2. **Transcoder loss:** Detect missed heartbeats/backpressure within 1–2s, reroute the demuxed feed to a warm standby GPU node (or active-active pair for tier-1 events), resume on the next IDR keyframe, and degrade to source pass-through if regional GPU capacity is exhausted.
3. **Segment CDN origin failure:** Run Tier 2 Core Origin active-active across AZs; fail over CDN Edges to a secondary Tier 1 Regional Shield with strict request collapsing and jittered backoff so misses never stampede the packager.
4. **Manifest staleness:** Cap blocking-reload hold time (~600ms–1s) and return `503` + `Retry-After` instead of hanging sockets; keep short playlist TTLs (`max-age=0, s-maxage=1`) and let players fail over to `fallback_manifest_url` or full-segment polling after 2–3 stale fetches.
5. **Viewer-side rebuffering:** Step down the ABR ladder at the next aligned IDR boundary, temporarily widen `PART-HOLD-BACK` (0.6s → 1.5s–2.0s) to stabilize playback, and gently catch up at `1.03x–1.05x` playback speed once throughput recovers.

---

## Phase 5 — Trade-offs & 60–90 Second Wrap-up (5 min)

### Key Trade-offs to Surface
| Decision | Choice | Trade-off Accepted |
|---|---|---|
| Delivery protocol | LL-HLS / CMAF over HTTP CDNs | ~2–3s latency instead of WebRTC's < 0.5s, in exchange for 10M-viewer CDN economics |
| Ingest protocol | SRT + WHIP alongside RTMP | Slightly higher gateway complexity, but far better resilience on lossy mobile links |
| Transcoder HA | Active-passive default, active-active for top events | 1–2s recovery blip on standard streams to avoid doubling GPU fleet cost across 50K channels |
| Latency vs. stability | Dynamic `PART-HOLD-BACK` relaxation | Temporarily adds ~1s latency on poor viewer links to prevent jarring rebuffer stalls |

### Closing Statement (60–90 Seconds)
> **Say:** "To summarize: we designed a live video streaming pipeline for 50,000 broadcasters and 10 million concurrent viewers targeting under 3 seconds glass-to-glass latency. Broadcasters authenticate via our control plane with epoch-fenced stream keys and ingest over SRT, RTMP, or WHIP, where we inject NTP SEI timestamps for frame-accurate live chat sync. Consistent-hashed GPU transcoders produce keyframe-aligned ABR ladders packaged into 200ms CMAF partial chunks. To absorb 10M+ manifest requests per second and 30 Tbps of egress, we pair LL-HLS blocking reloads with a 2-tier Origin Shield and global HTTP CDN edges. Our core trade-off is choosing LL-HLS over WebRTC for egress—giving up sub-second latency to gain HTTP CDN scale—while protecting the pipeline end-to-end against encoder drops, transcoder loss, origin outages, stale manifests, and viewer rebuffering."

---

*See [RUBRIC](./RUBRIC.md) for how this answer maps to scoring criteria, and [PITFALLS](./PITFALLS.md) for common mistakes to avoid.*
