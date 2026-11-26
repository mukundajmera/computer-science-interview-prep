# Interview Questions: CDN (Content Delivery Network)

## Basic Questions

### 1. What is a CDN and why do we need it?
**Q**: Explain what a CDN is and the problems it solves.

**A**: A CDN is a geographically distributed network of servers that cache and deliver content from locations close to users.

**Problems solved**:
- **Latency**: Reduces round-trip time from 200ms (cross-continent) to 20ms (local edge)
- **Bandwidth**: Offloads 80-90% of traffic from origin servers
- **Availability**: Provides redundancy if origin fails
- **Scalability**: Handles traffic spikes without origin scaling

---

### 2. What's the difference between Pull CDN and Push CDN?
**Q**: Compare pull and push CDN strategies.

**A**: 
| Aspect | Pull CDN | Push CDN |
|--------|----------|----------|
| **Mechanism** | CDN fetches on first request | Origin uploads proactively |
| **Cold cache** | First user waits | Content ready immediately |
| **Complexity** | Simpler, automatic | Requires push logic |
| **Best for** | General web content | Video, large files |
| **Example** | Cloudflare | Netflix Open Connect |

---

### 3. How does DNS routing work in CDN?
**Q**: Explain how users are routed to the nearest CDN edge.

**A**: CDNs use **GeoDNS** (Geographic DNS):
1. User requests `cdn.example.com`
2. DNS looks up user's IP geolocation
3. Returns IP of nearest edge server
4. User connects to local edge

**Alternative**: **Anycast** - same IP announced from all edges, BGP routing finds closest.

---

### 4. What content is appropriate for CDN caching?
**Q**: What types of content should and shouldn't be cached?

**A**:
**Cache (static/rarely changing)**:
- Images, CSS, JavaScript
- Video files
- Fonts, icons
- API responses (GET, with care)

**Don't cache**:
- Real-time data (stock prices)
- Personalized content (user dashboards)
- POST/PUT/DELETE requests
- Sensitive data (unless encrypted)

---

### 5. What are Cache-Control headers?
**Q**: Explain common Cache-Control directives.

**A**:
```
public              # CDN can cache
private             # Browser only, not CDN
max-age=3600        # Cache for 1 hour
s-maxage=86400      # CDN caches 1 day (overrides max-age)
no-cache            # Must revalidate before use
no-store            # Never cache
stale-while-revalidate=60  # Serve stale while fetching
```

---

## Intermediate Questions

### 6. How do you handle cache invalidation?
**Q**: A user updates their profile picture. How do you ensure all CDN edges serve the new image?

**A**: **Four strategies**:

1. **Versioned URLs** (preferred):
   ```
   /images/avatar.v2.jpg
   /images/avatar.jpg?v=abc123
   ```
   New URL = automatic cache bypass

2. **Purge API**:
   ```bash
   POST /purge {"urls": ["/images/avatar.jpg"]}
   ```
   Takes 5-30 seconds globally

3. **Short TTL** for frequently changing content:
   ```
   Cache-Control: max-age=60
   ```

4. **Soft purge** (stale-while-revalidate):
   - Mark stale, serve old while fetching new
   - No latency spike

**Trade-off**: Versioned URLs are most reliable but require URL changes.

---

### 7. What is cache stampede and how do you prevent it?
**Q**: Explain cache stampede and mitigation strategies.

**A**: **Cache stampede** (thundering herd): When cache expires, many simultaneous requests hit origin.

**Mitigations**:

1. **Request coalescing**: CDN combines concurrent misses into one origin request
2. **Stale-while-revalidate**: Serve stale content while fetching fresh
3. **Jittered TTL**: Add random time to prevent synchronized expiry
4. **Origin shield**: Single point fetches from origin, other edges fetch from shield
5. **Probabilistic early expiration**: Some requests refresh before actual expiry

```
Stampede:
Edge 1 ─┐
Edge 2 ─┼──▶ Origin (overwhelmed)
Edge 3 ─┘

With Shield:
Edge 1 ─┐                    
Edge 2 ─┼──▶ Shield ──▶ Origin (protected)
Edge 3 ─┘
```

---

### 8. How do you cache personalized content?
**Q**: Can you cache user-specific pages?

**A**: **Strategies**:

1. **Separate static/dynamic**: Cache page shell, fetch personalized data via AJAX
2. **Edge compute**: Run personalization at edge (Cloudflare Workers)
3. **Cache by user segment**: Group users (country, subscription tier)
4. **Private cache only**: `Cache-Control: private` for browser caching

**Example** (E-commerce):
```
Cached at CDN:     Product page HTML, images, CSS
Fetched via AJAX:  User's cart count, recommendations
```

---

### 9. What is an origin shield?
**Q**: Explain the purpose and implementation of an origin shield.

**A**: **Origin shield** is an intermediate caching layer between edge nodes and origin.

```
Without Shield:                   With Shield:
Edge (NYC) ──┐                   Edge (NYC) ──┐
Edge (LA)  ──┼──▶ Origin         Edge (LA)  ──┼──▶ Shield ──▶ Origin
Edge (CHI) ──┘                   Edge (CHI) ──┘
3 origin requests                1 origin request
```

**Benefits**:
- Reduces origin load on cache misses
- Single cache population for multiple edges
- Lower bandwidth costs
- Better cache hit rates at shield tier

---

### 10. How do you implement cache warming?
**Q**: Before a product launch, how do you ensure CDN caches are ready?

**A**: **Cache warming strategies**:

1. **Preload scripts**: Systematically request URLs from each edge region
2. **Push CDN**: Upload content directly to edges
3. **Synthetic requests**: Automated tools request content before launch
4. **Predictive caching**: ML predicts popular content

**Example script**:
```python
regions = ["us-east", "us-west", "eu-west", "asia"]
urls = ["/product/new-launch.html", "/images/hero.jpg"]

for region in regions:
    for url in urls:
        # Route request through specific region
        requests.get(f"https://{region}.cdn.example.com{url}")
```

---

## Advanced Questions

### 11. Design a CDN from scratch
**Q**: How would you design a basic CDN for a video streaming service?

**A**: 

**Components**:
```
                    ┌──────────────────┐
                    │   Control Plane  │
                    │  ┌────────────┐  │
                    │  │ Config DB  │  │
                    │  │ Monitoring │  │
                    │  │ Analytics  │  │
                    │  └────────────┘  │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │    GeoDNS        │
                    │  (Route users)   │
                    └────────┬─────────┘
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼
   ┌──────────┐        ┌──────────┐        ┌──────────┐
   │  Shield  │        │  Shield  │        │  Shield  │
   │   US     │        │    EU    │        │   Asia   │
   └────┬─────┘        └────┬─────┘        └────┬─────┘
        │                   │                   │
   ┌────┼────┐         ┌────┼────┐         ┌────┼────┐
   ▼    ▼    ▼         ▼    ▼    ▼         ▼    ▼    ▼
 Edge Edge Edge      Edge Edge Edge      Edge Edge Edge
```

**Data Flow**:
1. DNS routes to nearest edge based on IP geolocation
2. Edge checks local SSD cache for video segment
3. Miss → fetch from regional shield (HDD cache)
4. Miss → fetch from origin, cache at both tiers

**Key Decisions**:
- **Storage**: SSD at edge (hot), HDD at shield (warm)
- **Eviction**: LRU with popularity weighting
- **Protocol**: HTTP/2 for multiplexing, QUIC for mobile
- **Security**: TLS termination at edge, token validation

---

### 12. How do you handle CDN failures?
**Q**: What happens when an edge node fails? How do you handle cascading failures?

**A**: **Failure handling**:

1. **Health checks**: Active probing every 5-10 seconds
2. **DNS TTL**: Low TTL (30-60s) allows quick failover
3. **Anycast routing**: BGP automatically reroutes on node failure
4. **Fallback chain**: Edge → Shield → Origin
5. **Circuit breakers**: Stop sending traffic to unhealthy nodes

**Cascading failure prevention**:
```
Normal:    Edge ─── 1000 RPS ──▶ Origin

Edge fails: 
Without protection: 3 Edges ─── 3000 RPS ──▶ Origin (overloaded)

With protection:
- Rate limiting at shield: max 1200 RPS to origin
- Request shedding: 429 responses to excess
- Queue with timeout: Smooth burst
```

---

### 13. How do you handle TLS at scale in a CDN?
**Q**: Managing TLS certificates across thousands of edge nodes and millions of domains?

**A**: **Challenges and solutions**:

1. **Certificate distribution**: 
   - Automated renewal (Let's Encrypt, ACME)
   - Push to all edges on update
   - Eventual consistency is OK (old cert valid during transition)

2. **TLS termination at edge**:
   - Decrypt at edge for caching
   - Re-encrypt to origin (mTLS)
   - Session tickets for resumption

3. **SNI-based multi-tenancy**:
   - Single IP, thousands of domains
   - Server Name Indication identifies cert to use

4. **Performance**:
   - Hardware acceleration (AES-NI)
   - Session caching to avoid handshakes
   - OCSP stapling for revocation checks

---

### 14. How do you optimize video delivery?
**Q**: Design CDN optimizations for streaming video at scale.

**A**: **Key optimizations**:

1. **Adaptive bitrate**: Cache multiple quality versions
   ```
   /video/abc/720p/segment-001.ts
   /video/abc/1080p/segment-001.ts
   /video/abc/4k/segment-001.ts
   ```

2. **Chunk-based caching**: HLS/DASH segments cached independently

3. **Predictive prefetching**: Fetch next segments before requested

4. **Hot/cold tiering**:
   - Hot (popular): Edge SSD
   - Warm (recent): Shield HDD
   - Cold (archive): Origin/cloud storage

5. **Byte-range requests**: Resume interrupted downloads

6. **Manifest caching**: Short TTL for playlist files, longer for segments

---

## Common Follow-ups

- **What happens if your purge fails?** Versioned URLs as fallback, monitoring for stale content alerts
- **How do you test CDN changes?** Canary deployments, A/B with percentage rollout
- **How do you handle partial content (Range requests)?** Cache full file, serve ranges from cache
- **Cost optimization?** Regional pricing, origin offload metrics, cache-on-revalidate

## Red Flags to Avoid

- **Ignoring cache invalidation complexity**: "Just purge it" - explain timing and global propagation
- **Caching everything**: Not all content should be cached
- **Forgetting security**: CDN requires TLS, origin validation, access control
- **Single region thinking**: CDN is inherently global, consider all regions
- **Ignoring cold cache**: First users after expiry/purge see origin latency

## How to Explain in 30 Seconds

"A CDN is a globally distributed cache layer that serves content from locations close to users. Instead of a Tokyo user requesting data from a New York server with 200ms latency, they get it from a Tokyo edge node in 20ms. The CDN handles cache invalidation through TTLs or purge APIs, uses GeoDNS to route users to the nearest edge, and employs multiple tiers—edge nodes for hot content, shields to protect origin, and the origin as the source of truth. The main challenge is cache invalidation, which is why versioned URLs are preferred over time-based expiry."
