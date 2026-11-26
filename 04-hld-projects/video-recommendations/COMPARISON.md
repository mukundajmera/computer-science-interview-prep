# Video Recommendations — Comparison Notes

| System | Similarity | Key difference |
|---|---|---|
| [News Feed](../news-feed/) | ranking under heavy read traffic | session-aware recommendation candidates vs follow-graph timeline |
| [Video Streaming](../video-streaming/) | same product surface | ranking/control plane vs media ingestion/delivery data plane |
| [Realtime Metrics Platform](../realtime-metrics-platform/) | high-volume feedback analytics | recommendation objective optimization vs generic metrics processing |

## Reuse guidance

- Reuse caching, stream ingestion, and observability patterns.
- Keep recommendation ranking independent from delivery pipeline.
- Share experiment and feature-store infrastructure across ranking systems.
