# Google Maps & Navigation - Common Pitfalls

## 1. Using Standard Dijkstra for Global Routing
- **Signal:** Candidate proposes standard Dijkstra's or Breadth-First Search for finding routes between cities.
- **Root Cause:** Lack of understanding of scale. A continental road graph has tens of millions of nodes. Standard Dijkstra explores radially, taking seconds or minutes.
- **Mitigation:** Explicitly introduce hierarchical routing or Contraction Hierarchies (CH). Explain that the route graph is preprocessed offline to create shortcuts across major highways, reducing query times to under 5ms.

## 2. Raster Image Tiles Instead of Vector Tiles
- **Signal:** Designing the map serving layer using statically generated PNG images.
- **Root Cause:** Treating the map purely as a traditional image CDN problem rather than a modern client-rendered application.
- **Mitigation:** Propose Vector Protobuf tiles. Explain that they consume 75% less bandwidth (~5KB vs ~20KB), allow smooth client-side rotation (3D), and enable dynamic styling without re-downloading images.

## 3. Synchronous Telemetry Writes to a Relational Database
- **Signal:** Candidate designs an API where every GPS ping is written synchronously to PostgreSQL before acknowledging the client.
- **Root Cause:** Failing to account for the 1M peak QPS scale and the bursty nature of mobile telemetry.
- **Mitigation:** Introduce an asynchronous ingestion pipeline (API Gateway -> Kafka -> Flink). Buffer writes and acknowledge the client quickly. Use Cassandra for high-volume time-series storage.

## 4. Ignoring Map Matching
- **Signal:** Assuming raw GPS coordinates cleanly map to roads and immediately calculating speed.
- **Root Cause:** Disregarding real-world GPS inaccuracy (urban canyons, tunnels).
- **Mitigation:** Include a "Map Matching" component in the stream processing layer. Explain how algorithms (like Hidden Markov Models) snap noisy GPS points to the most probable road segments before calculating traffic speeds.

## 5. Over-Chatty Mobile Clients
- **Signal:** Suggesting mobile phones send a GPS ping every 1 second over cellular networks.
- **Root Cause:** Ignoring client battery life and cellular radio overhead.
- **Mitigation:** Propose client-side batching (e.g., collect data every second, but send a batched payload every 15-30 seconds).
