# Follow-Ups

1.  **How do you handle real-time ACL changes?**
    *   ACL updates can be propagated via CDC. However, caching user-to-group mappings at the edge reduces latency.
2.  **How do you handle multi-region deployments?**
    *   Deploy read-replicas of the Vector DB in different regions and route user traffic via Geo-DNS.
