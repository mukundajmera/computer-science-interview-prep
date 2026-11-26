# Distributed Object Storage - Follow-Up Questions

## Follow-up questions

1. **How do you handle rapid bucket listings (e.g., millions of objects with a specific prefix)?**
   - *Expected:* Discuss using a specialized search index (like Elasticsearch) or leveraging Cassandra's wide-column features to index object names by prefix. Alternatively, a dedicated Trie-based cache.

2. **How does the system enforce strict consistency if a client reads an object immediately after overwriting it?**
   - *Expected:* The write path must achieve quorum in the Metadata DB before acknowledging success. The read path must use strong consistency reads (e.g., `QUORUM` reads in Cassandra) to ensure it gets the latest version ID.

3. **What happens if a Chunk Server completely dies and its data needs rebuilding, but the network is saturated?**
   - *Expected:* Discuss traffic shaping and rate-limiting the Placement & Repair Service. Rebuilds must be throttled during peak hours to avoid impacting user read/write latency.

## Variants and extensions

- **Cold Storage (Glacier-like):** Extend the design to support tiering. Move rarely accessed 1GB container files to slower, cheaper magnetic tapes or power-down disk arrays. Update the metadata DB to flag objects as `COLD`, requiring an async restore job.
- **Cross-Region Replication:** Support buckets that automatically replicate objects to a secondary continent. Involves an async worker tailing the Metadata DB changes and copying chunks across regions.

## Interviewer probes to prepare

- "Walk me through exactly what happens when one of your Erasure Coded disks fails. How much data is read to rebuild a 1GB file?"
- "Your SQLite metadata per chunk server seems like a single point of failure. What happens if that SQLite file gets corrupted?" *(Answer: The container file's chunks have headers with their own IDs. A background script can scan the container and rebuild the SQLite index from scratch).*

## Cross-links
- [Problem Statement](./PROBLEM.md)
- [Design Document](./DESIGN.md)
