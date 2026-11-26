# Video Streaming — Comparison

## Video Streaming vs File Storage

| Concern | Video Streaming | File Storage |
|---|---|---|
| Read model | segmented playback via manifests | object download |
| Post-upload path | mandatory transcode and packaging | optional processing |
| Distribution | CDN-heavy | mixed |

## Video Streaming vs Realtime Metrics Platform

| Concern | Video Streaming | Realtime Metrics Platform |
|---|---|---|
| Primary SLO | startup/rebuffer UX | ingest/query latency |
| Core data | media segments/manifests | metric events/time series |
| Hot path risk | origin overload | cardinality + late events |

## Video Streaming Rec Extension vs Standalone Recommender

| Concern | In-Platform Rec Subsystem | Standalone Rec Product |
|---|---|---|
| Scope | watch-next/home ranking for playback product | multi-surface ranking platform |
| Coupling | tight with media metadata/playback context | broader cross-product feature graph |
| Feedback loops | managed with product-level exploration and freshness caps | broader ecosystem-level interventions |
| Interview focus | latency-constrained extension | full rec platform architecture |
